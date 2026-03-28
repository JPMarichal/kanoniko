"""LLM-powered entity profile generation (Phase 2).

Given metadata-stage profiles (mention_count, key_passages), generates
bilingual summaries and disambiguation notes via the cheapest LLM tier.
"""

from __future__ import annotations

import json
import logging

from alejandria.chat.llm import complete_with_model
from alejandria.chat.models import Tier, select_model
from alejandria.knowledge.profile_store import EntityProfile, ProfileStore

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a scripture study assistant specializing in biblical and Latter-day Saint texts.
You produce concise, factual entity profiles in JSON format.
Always respond with valid JSON only — no markdown, no extra text."""

_USER_PROMPT_TEMPLATE = """\
The following passages mention "{name}" (type: {entity_type}).

{passages}

Produce a JSON object with these fields:
- "summary_en": 2-3 sentence English description of who/what this entity is, based ONLY on the passages above.
- "summary_es": 2-3 sentence Spanish translation of the same description.
- "disambiguation": If the passages clearly refer to MULTIPLE DISTINCT individuals/entities \
sharing this name, list each as an object with "id" (short disambiguator like "Iscariot" or \
"brother of Jesus"), "summary_en", and "summary_es". If there is only ONE entity, set this to null.

Respond with valid JSON only."""


class ProfileGenerator:
    """Generate LLM-enriched profiles from metadata profiles."""

    def __init__(self, profile_store: ProfileStore, tier: str = "fast") -> None:
        self._store = profile_store
        self._tier = Tier(tier) if tier in ("fast", "balanced", "quality") else Tier.FAST
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    def generate_profile(self, profile: EntityProfile) -> EntityProfile | list[EntityProfile]:
        """Generate LLM summary for a single entity profile.

        Returns the updated profile, or a list of profiles if disambiguation
        detected multiple distinct entities.
        """
        model = select_model(self._tier)
        if model is None:
            logger.warning("No LLM model available for profile generation")
            return profile

        # Build passages text from key_passages
        passages_text = self._format_passages(profile)
        if not passages_text:
            logger.debug("No passages for %s, skipping LLM", profile.entity_name)
            return profile

        user_msg = _USER_PROMPT_TEMPLATE.format(
            name=profile.entity_name,
            entity_type=profile.entity_type,
            passages=passages_text,
        )

        try:
            response = complete_with_model(_SYSTEM_PROMPT, user_msg, model)
            self._total_input_tokens += response.input_tokens
            self._total_output_tokens += response.output_tokens
        except Exception:
            logger.exception("LLM call failed for %s", profile.entity_name)
            return profile

        # Parse JSON response
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response.text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
            else:
                logger.warning("Failed to parse LLM response for %s: %s", profile.entity_name, response.text[:200])
                return profile

        disambiguation = data.get("disambiguation")

        if disambiguation and isinstance(disambiguation, list) and len(disambiguation) > 1:
            # Multiple distinct entities detected — split into separate profiles
            return self._split_disambiguated(profile, disambiguation)

        # Single entity — update profile
        profile.summary_en = data.get("summary_en") or profile.summary_en
        profile.summary_es = data.get("summary_es") or profile.summary_es
        profile.status = "profiled"
        profile.profile_version += 1
        return profile

    def generate_batch(
        self,
        entity_types: list[str] | None = None,
        max_entities: int = 50,
        force: bool = False,
    ) -> dict:
        """Generate LLM profiles for a batch of entities.

        Args:
            entity_types: Filter to specific types. None = all.
            max_entities: Max entities to process.
            force: If True, regenerate even already-profiled entities.

        Returns stats dict.
        """
        import time

        start = time.time()
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        # Get candidates — highest mention_count first
        status_filter = None if force else "metadata"
        type_filter = entity_types[0] if entity_types and len(entity_types) == 1 else None

        candidates = self._store.get_all(
            entity_type=type_filter,
            status=status_filter,
            min_mentions=1,
            limit=max_entities,
        )

        # If multiple types requested, filter in memory
        if entity_types and len(entity_types) > 1:
            type_set = set(entity_types)
            candidates = [c for c in candidates if c.entity_type in type_set]

        total = len(candidates)
        logger.info("Profile generation: %d candidates", total)

        generated = 0
        disambiguated = 0

        for i, profile in enumerate(candidates):
            result = self.generate_profile(profile)

            if isinstance(result, list):
                # Disambiguation split — save all variants
                for p in result:
                    self._store.upsert_profile(p)
                disambiguated += 1
                generated += len(result)
            else:
                self._store.upsert_profile(result)
                generated += 1

            if (i + 1) % 50 == 0:
                logger.info(
                    "Profile generation: %d/%d (%.0f%%), %d input tokens, %d output tokens",
                    i + 1, total, (i + 1) / total * 100,
                    self._total_input_tokens, self._total_output_tokens,
                )

        elapsed = time.time() - start
        stats = {
            "entities_processed": total,
            "profiles_generated": generated,
            "disambiguations": disambiguated,
            "input_tokens": self._total_input_tokens,
            "output_tokens": self._total_output_tokens,
            "elapsed_seconds": round(elapsed, 1),
        }
        logger.info(
            "Profile generation complete: %d entities, %d profiles, %d disambiguations in %.1fs",
            total, generated, disambiguated, elapsed,
        )
        return stats

    def _format_passages(self, profile: EntityProfile, max_passages: int = 15) -> str:
        """Format key_passages into a numbered text block for the LLM prompt."""
        lines = []
        for i, passage in enumerate(profile.key_passages[:max_passages]):
            ref = passage.get("reference", "?")
            snippet = passage.get("snippet", "")
            lines.append(f"{i+1}. [{ref}] {snippet}")
        return "\n".join(lines)

    def _split_disambiguated(
        self, original: EntityProfile, disambiguation: list[dict]
    ) -> list[EntityProfile]:
        """Split a generic profile into multiple disambiguated profiles."""
        profiles = []
        for variant in disambiguation:
            disambiguator = variant.get("id", "")
            new_name = f"{original.entity_name} ({disambiguator})" if disambiguator else original.entity_name

            p = EntityProfile(
                entity_name=new_name,
                entity_type=original.entity_type,
                mention_count=original.mention_count // len(disambiguation),  # rough split
                document_count=original.document_count // len(disambiguation),
                books=original.books,  # shared for now — Phase 3 can refine
                key_passages=original.key_passages,  # shared for now
                aliases=[original.entity_name],  # original name is an alias
                disambiguator=disambiguator,
                summary_en=variant.get("summary_en"),
                summary_es=variant.get("summary_es"),
                disambiguation_notes=f"Disambiguated from generic '{original.entity_name}'",
                profile_version=original.profile_version + 1,
                status="profiled",
            )
            profiles.append(p)

        # Mark original as disambiguated
        original.disambiguation_notes = f"Split into {len(profiles)} variants: {[p.entity_name for p in profiles]}"
        original.status = "profiled"
        profiles.append(original)
        return profiles
