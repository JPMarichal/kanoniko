#!/usr/bin/env python3
"""
Filter Women in the Scriptures URLs into corpus-worthy vs. excluded.
Reads data/wits_raw_urls.txt, outputs three files in data/.
"""

import re
from pathlib import Path

RAW_FILE = Path(__file__).parent.parent / "data" / "wits_raw_urls.txt"
OUT_DIR = Path(__file__).parent.parent / "data"

# ── Slug substrings that trigger exclusion ───────────────────────────────────

EXCLUDE_SLUGS = {
    # Navigation duplicates
    "subcat-post": "subcat-navigation",
    # Personal roundups
    "five-things-for-friday": "personal-roundup",
    "five-things-for-saturday": "personal-roundup",
    "greatest-hits-of": "personal-roundup",
    # Promos / giveaways
    "giveaway": "promo",
    "win-free": "promo",
    "free-admission": "promo",
    "free-copies": "promo",
    "free-study-guide": "promo",
    "free-relaxation": "promo",
    "free-subscription": "promo",
    "sign-up-for-my-emails": "promo",
    "pre-order-walking": "book-promo",
    "book-release": "book-promo",
    "my-book-has-cover": "book-promo",
    "launch-party": "book-promo",
    "cover-is-unveiled": "book-promo",
    "winners": "promo",
    # Event announcements
    "registration-is-open": "event",
    "i-will-be-speaking": "event",
    "lds-booksellers": "event",
    "link-and-mingle": "event",
    "conference-accomplished": "event",
    "spring-break-for-women": "event",
    "three-chances-to-see-me": "event",
    # Personal birth stories (author's children)
    "ashers-birth-story": "personal-birth",
    "roses-birth-story": "personal-birth",
    "tabithas-birth-story": "personal-birth",
    "noelles-birth-story": "personal-birth",
    "abrahams-birth-story": "personal-birth",
    "the-first-noelle": "personal-birth",
    # Personal diary / lifestyle
    "home-school-tour": "personal",
    "mrs-weasleys-pensieve": "personal",
    "my-life-is-full-of-typos": "personal",
    "my-life-is-tree": "personal",
    "my-favorite-story-about-my-dad": "personal",
    "the-most-creative-years": "personal",
    "my-covered-wagon": "personal",
    "building-solomons-temple-in-my-kitchen": "personal",
    "vintage-bible-flannel-board": "personal",
    "five-years-ago": "personal",
    "my-hair-shirt": "personal",
    "very-simple-quiet-book": "personal",
    "quiet-book-swap": "personal",
    "emergency-haircut": "personal",
    "speed-dating": "personal",
    "homemade-christmas": "personal",
    "the-chicken-mummy": "personal",
    "bless-this-mess-christmas": "personal",
    "dress-dare": "personal",
    "half-way-through-dress": "personal",
    "eating-chickens": "personal",
    "marriage-of-penguins": "personal",
    "red-coats-and-race-cars": "personal",
    "the-summer-of-my-life": "personal",
    "the-best-financial-advice": "personal",
    "best-labor-day-ever": "personal",
    "babymoon": "personal",
    "bootiful-navuoo": "personal",
    "my-talented-family": "personal",
    "take-my-poll": "personal",
    "meeting-my-hero": "personal",
    "in-which-i-vent": "personal",
    "back-from-break": "personal",
    "changed-my-mind": "personal",
    "every-other-wednesdays": "personal",
    "i-apologize-for-being": "personal",
    "what-do-you-want-to-know-about-me": "personal",
    "let-me-introduce-you-to": "personal",
    "calling-all-international": "personal",
    "celebrating-my-3rd-blog": "personal",
    "celebrating-my-4th-blog": "personal",
    "personal-ponderings-4th": "personal",
    "what-is-working-and-what-isnt": "personal",
    "birth-on-brain": "personal",
    "ill-be-wearing-skirt": "personal",
    "new-year-miracles": "personal",
    "re-issuing-challenge": "personal",
    "i-am-writing-book": "personal",
    "a-very-late-fathers-day": "personal",
    "the-perfect-gift": "personal",
    "general-conference-in-whirl": "personal",
    "how-to-catch-feminist": "personal",
    "good-news-momen": "personal",
    "flood-warnings": "personal",
    "due-date": "personal",
    "having-a-december-birthday": "personal",
    "too-many-speedo-ish": "personal",
    "a-swastika-on-floor": "personal",
    "work-nashville-tribute-to-missionaries": "personal",
    "save-wri": "personal",
    "scripture-power.html": "personal",
    "deep-beauty": "personal",
    "stitch-by-stitch": "personal",
    "because-you-love-me": "personal",
    "appreciating-physicality": "personal",
    "why-i-love-my-stretch-marks": "personal",
    "my-easter-gift-for-you": "personal",
    "darkest-day-of-year": "personal",
    "have-you-opened-your-gift": "personal",
    "give-oh-give": "personal",
    "dont-wait": "personal",
    "taking-challenge": "personal",
    "my-climb-up-jacobs-ladder": "personal",
    "shout-out-for-women-of-old": "meta",
    "ask-mormon-question": "meta",
    "celebrating-emma-smiths-birthday-again": "personal",
    # FHE personal parenting
    "family-home-evening": "personal-parenting",
    "fhe-with-pimentels": "personal-parenting",
    "challenges-of-fhe": "personal-parenting",
    "20-minutes-every-monday": "personal-parenting",
    "how-to-get-kids-to-pay-attention": "personal-parenting",
    "our-zero-tolerance-policy": "personal-parenting",
    # Guest posts (personal, not scriptural)
    "forgiveness-is-complicated-by-leslie": "guest-personal",
    "relief-society-vs-fit-it-society-by-amy": "guest-personal",
    "love-life-and-learning-by-michelle": "guest-personal",
    "a-princess-story-guest-post": "guest-personal",
    "learning-and-choosing-to-be-happy": "guest-personal",
    # Book reviews (not original scripture analysis)
    "girls-who-choose-god": "book-review",
    "covenant-motherhood-book-review": "book-review",
    "eve-in-beginning-book-review": "book-review",
    "glimpse-of-heaven-book-review": "book-review",
    "women-of-book-of-mormon-book-review": "book-review",
    "book-recommendations-for-studying": "book-review",
    # "LDS Women Around the World" series (modern profiles, not scripture)
    "latter-day-saint-women-around-world": "modern-profiles",
    "later-day-saint-women-around-world": "modern-profiles",
    # Modern testimonies
    "amandas-testimony": "modern-testimony",
    "abis-testimony": "modern-testimony",
    "ramonas-testimony": "modern-testimony",
    "karin-from-denmarks-testimony": "modern-testimony",
    "my-testimony-for-emma": "modern-testimony",
    "video-tribute-for-emma": "modern-testimony",
    # Non-scripture topics
    "the-reason-you-love-jane-austen": "non-scripture",
    "the-american-woman-today": "non-scripture",
    "a-brief-history-of-eugenics": "non-scripture",
    "would-democracy-cease-to-exist": "non-scripture",
    "when-is-it-art-when-is-it-pornography": "non-scripture",
    "song-pilates-wife-by-nashville": "non-scripture",
    # Additional personal/meta caught in review pass
    "call-for-guest-posters": "meta",
    "celebrating-my-blog-iversary-with": "personal",
    "great-upcycled-dress-challenge": "personal",
    "women-in-scriptures-event-you-wont-want": "event",
    "wishing-you-mary-christmas": "personal",
    "a-spiritual-way-to-celebrate-my": "personal",
    "okay-i-think-i-like-sister-burton": "personal",
    "the-more-you-give-more-you-receive": "personal",
    "when-you-feel-like-you-are-falling": "personal",
    "acclimated-and-desensitized": "personal",
    "a-blessing-from-my-daughter": "personal",
    "any-problem-that-can-be-fixed-with-money": "personal",
    "my-childrens-names": "personal",
    "book-is-born": "book-promo",
    "all-thanks-and-praise": "personal",
    "fidning-time-for-personal-prayer": "personal",
    "recommended-reading": "meta",
    "baby-blessing": "personal",
    "study-guide-for-women-in-book-of-mormon": "promo",
    "free-study-guide-for-women-in-new": "promo",
    "happy-birthday-emma-my-testimony": "personal",
    "happy-birthday-for-emma-smith": "personal",
    "letter-to-mother-of-girl": "personal",
    "womens-bodies-and-shame": "personal",
    "mothers-and-careers-age-old": "personal",
    "why-you-wont-want-to-miss-general": "personal",
    # Misc excluded
    "modestpop-4th": "promo",
    "from-dust-4th": "promo",
    "rockin-their-babies": "promo",
    "certain-woman-necklace": "promo",
    "fhe-winners": "promo",
    "test-your-knoweldge": "promo",
    "one-final-gift": "promo",
}

# Exact slug matches to exclude (for ambiguous short slugs)
EXCLUDE_EXACT = {
    "nothing", "glimpse", "nativity",
}

# ── TIER 1: Woman profile slugs (scripture-based, high value) ────────────────
# These are the named profiles from the site's index pages.

PROFILE_SLUGS = {
    # OT
    "abigail", "asenath", "athaliah", "hagar", "deborah", "peninnah",
    "huldah", "vashti", "estherhadassah", "potiphars-wife",
    "widow-of-zarephath", "concubine-in-judges-19", "noahs-wife",
    "daughters-of-zelophehad", "daughters-of-shallum", "daughters-of-zion",
    "jemima-kezia-keren-happuch", "three-daughters-of-heman", "little-maid",
    "puah-and-shiphrah", "pharaohs-daughter-solomons-wife",
    "gomer-and-lo-ruhamah", "jehosheba", "prophetess-wife-of-isaiah",
    "elisheba-and-daughters-of-aaron", "moses-ethiopian-wife",
    "bilhah-and-zilpahs-birth-stories-old", "daughter-of-barzillai",
    "shunamite-woman", "jehoshebajehoshabeath",
    # NT
    "anna", "claudia", "damaris", "damsel-and-maid-to-whom-peter-denied",
    "drusilla", "eunice", "lois", "lydia", "peters-wifes-mother",
    "phebephoebe", "pontius-pilates-wife", "rhoda", "sapphira",
    "tabithadorcus", "tryphena-and-tryphosa", "widow-of-nain",
    "woman-with-issue-of-blood", "elect-lady", "first-sorrow-of-mary",
    "devout-honorable-and-chief-women", "women-at-empty-tomb",
    # BoM
    "mothers-of-2060-stripling", "nephis-wife",
    "nephite-and-lamanite-women-who-toiled",
    "nephite-women-of-sherrizah", "queen-of-king-lamoni",
    "women-in-wilderness", "women-of-city-bountiful", "daughters-of-onitah",
    # PoGP
    "egyptus",
    # D&C / LDS history profiles
    "emma-smiths-patriarchal-blessing", "emmas-dream",
    # Aggregate / list profiles
    "list-of-all-women-in-old-testament", "list-of-all-women-in-new-testament",
    "where-are-all-women-in-book-of-mormon",
    # Additional profiles (longer slugs from blog posts)
    "miriam-prophetess-and-leader-of-women", "miriam-leprosy-and-bad-case-of",
    "vashti-and-esther-why-it-doesnt-pay", "vashti-put-your-crown-on",
    "tamar-whats-girl-to-do", "sariahs-breaking-point",
    "wives-made-to-bow-down-with-grief", "hannahs-vow",
    "the-women-who-delivered-moses", "2060-sons-of-helaman",
    "three-daughters-of-heman-2", "daughters-of-shallum-2",
    "jehosheba", "the-huldah-gates",
    # Mary-focused profiles
    "first-sorrow-of-mary", "what-mary-felt", "in-marys-words",
    "mary-knew", "a-mary-sort-of-christmas", "mary-christ-mass",
    "was-mary-the-mother-of-jesus-a-musician",
    "behold-condescension-of-god",
    # Rebekah, Rachel, Sarah, Eve deep dives
    "i-will-go-rebekahs-famous-refrain",
    "blessings-of-sarah-rebekah-and-rachel",
    "is-anything-too-hard-for-lord-sarahs",
    "rebekahs-birth-story-counsel-with-lord",
    "bearing-children-in-wilderness-sariah",
    "eve-and-her-faithful-daughters", "eves-curse",
    "what-does-it-mean-that-eve-was-beguiled", "getting-adam-to-partake",
    "honoring-eve-by-marilyn-hull",
    # Birth stories FROM SCRIPTURE (not personal)
    "from-womb-samsons-birth-story", "phinehas-wifes-birth-story",
    "to-prepare-way-elisabeths-birth-story",
    "hannahs-birth-story-my-horn-is-exalted",
    "delivered-ere-midwives-come",
    "breastfeeding-women-in-scriptures-part-1",
    "breastfeeding-women-in-scriptures-part-2",
}

# ── TIER 2: Pure scriptural analysis (text-focused, no agenda) ───────────────

SCRIPTURAL_ANALYSIS_SLUGS = {
    "real-meaning-of-term-help-meet",
    "spiritual-symbolism-of-veils",
    "magnificat-and-hannahs-psalm",
    "abrahams-tent",
    "adams-rib",
    "being-called-woman",
    "the-lost-teachings-of-jesus-on-sacred",
    "the-matriarchal-order",
    "how-to-use-strongs-concordance-to",
    "his-mother-made-him-little-coat",
    "dwelling-in-tent",
    "blood-or-milk",
    "womb-to-tomb",
    "the-biggest-battle-that-ever-was-won",
    "celebrating-purim", "purim-katan-little-purim",
    "not-good-for-man-to-be-alone",
    "god-is-gardener",
    "if-all-men-were-like-joseph",
    "where-was-jesus-really-born",
    "the-firstling-of-our-flock",
    "three-biblical-love-stories",
    "laman-and-lemuels-motivation",
    "what-was-the-temple-in-jerusalem-like",
    "what-makes-women-in-bible-so-beautiful",
    "god-comes-to-women",
    "rent-in-twain",
    "women-in-image-of-son-being-female-and",
    "a-photographic-tribute-to-biblical",
    "vessels-of-lord",
    "honoring-dead",
    "the-ancient-relief-society-of-new",
    "15-women-who-have-lead-relief-society",
    "similar-organization-for-women-existed",
    "the-women-of-zions-camp",
    "our-reenactment-of-first-relief-society",
    "understanding-emma-smiths-life-by-mark",
    "coming-to-know-emma-by-katherine",
    "life-of-emma-smith-part-1",
    "life-of-emma-smith-part-2",
    "through-inspiration-lds-hymns-composed",
    "names-of-christ-advent-devotional",
    "women-giving-blessings-in-early-days-of",
    "the-presidents-ward",
    "what-does-it-mean-for-woman-to-be",
    "importance-of-birth",
    "infertility-and-scriptural-promise",
    "midwifery-as-calling",
    "teaching-children-about-adam-and-eve",
    "bible-says-women-can-propose-to-their",
    "i-will-tell-you-of-wrestle-which-i-had",
    "understanding-what-it-means-to-preside",
    "a-treasure-box-with-two-keys",
    "new-way-to-study-women-in-scriptures",
    "women-in-scriptures-jeopardy",
    "learning-our-history",
    "the-perks-of-having-rich-dad",
    "who-cooked-first-thanksgiving-meal",
    "to-everything-there-is-season",
    "how-holy-is-sabbath-day",
    "no-respector-of-persons",
    "every-baby-is-a-royal-baby",
    "the-power-of-a-mothers-blessing",
    "does-the-journey-seem-long",
    "counseling-together-in-marriage-example",
}

# ── OPINION / AGENDA essays (exclude from corpus) ───────────────────────────

OPINION_SLUGS = {
    "yes-virginia-girls-have-preisthood": "opinion-priesthood",
    "a-call-for-restoration-of-true-feminism": "opinion-feminism",
    "why-dont-women-hold-priesthood": "opinion-priesthood",
    "its-not-about-priesthood-what-lds-women": "opinion-priesthood",
    "almost-half-million-women-hold": "opinion-priesthood",
    "this-is-type-of-feminist-i-am": "opinion-feminism",
    "goddess-archetypes": "opinion-theology",
    "archetypes-instead-of-stereotypes": "opinion-feminism",
    "my-worth-as-woman-is-not-dependent-upon": "opinion-feminism",
    "power-or-influence-which-would-you": "opinion-feminism",
    "all-violence-is-violence-against-women": "opinion-social",
    "is-it-harder-to-be-boy-or-girl": "opinion-social",
    "the-meaning-of-marriage": "opinion-social",
    "marriage-is-death": "opinion-social",
    "divorce-is-as-hard-as-death": "opinion-social",
    "when-nurturing-doesnt-come-naturally": "opinion-personal",
    "barbie-dilemma": "opinion-social",
    "satan-hates-mothers": "opinion-social",
    "how-much-is-mother-really-worth": "opinion-social",
    "called-to-work-is-it-bad-if-i-feel": "opinion-personal",
    "a-culture-of-light-or-culture-of": "opinion-social",
    "every-baby-comes-with-loaf-of-bread": "opinion-social",
    "when-it-comes-to-having-children-it-is": "opinion-social",
    "fasting-while-pregnant-or-breastfeeding": "opinion-practice",
    "lds-churchs-stance-on-tubal-litigations": "opinion-practice",
    "memorizing-proclamation-of-family": "opinion-personal",
    "setting-record-straight-there-really": "opinion-history",
    "good-guys-and-bad-guys": "opinion-personal",
    "judge-not-or-in-other-words-what-i": "opinion-personal",
    "the-dark-days-of-faith": "opinion-personal",
    "face-cards-yea-or-nay": "opinion-culture",
    "mormon-womans-thougths-on-homosexuality": "opinion-social",
    "how-to-change-world": "opinion-social",
    "celebrating-our-heavenly-mother-on": "opinion-theology",
    "finding-nobility-in-motherhood-and-joy": "opinion-personal",
    "strengthening-marriage-family-and-home": "opinion-personal",
    "why-relief-society-is-not-glorified": "opinion-church",
    "tribute-to-sister-julie-b-beck": "opinion-personal",
    "the-birth-and-re-birth-of-my-children": "opinion-personal",
    "women-as-embassadors-of-peace": "opinion-social",
    "identity-crisis": "opinion-personal",
    "what-charity-feels-like": "opinion-personal",
    "god-knows-desires-of-your-heart": "opinion-personal",
    "women-of-faith-and-our-first-mother": "opinion-personal",
    "an-angel-in-hallway": "opinion-personal",
    "teaching-children-patience": "opinion-parenting",
    "teaching-children-charity": "opinion-parenting",
    "teaching-children-humility": "opinion-parenting",
    "teaching-children-obedience": "opinion-parenting",
    "teaching-children-honesty": "opinion-parenting",
    "teaching-children-about-sexual-intimacy": "opinion-parenting",
    "a-babys-blessing": "opinion-personal",
    "moms-missionary-training-center": "opinion-parenting",
    "baby-changes-everything": "opinion-personal",
    "canning-jars-and-charity": "opinion-personal",
    "spending-time-in-scriptures-every-day": "opinion-personal",
    "improving-your-personal-scripture-study": "opinion-personal",
    "how-i-study-my-scriptures": "opinion-personal",
    "family-scripture-study-with-young": "opinion-parenting",
    "would-you-have-peeked-at-gold-plates": "opinion-personal",
    "nitty-gritty-womens-work": "opinion-personal",
    "interview-with-diana-webb": "opinion-interview",
    "masters-wheel": "opinion-personal",
    "guardians-of-hearth": "opinion-social",
    "becoming-equal-partners": "opinion-social",
    "where-were-you": "opinion-personal",
    "divinely-appointed": "opinion-personal",
    "inspired-once-again-by-sister-beck": "opinion-personal",
    "gift-of-giving-life": "opinion-personal",
    "sister-scriptorians": "opinion-personal",
    "turning-my-heart-to-women-in-my-past": "opinion-personal",
    "practicing-fatherhood": "opinion-personal",
    "for-fathers": "opinion-personal",
    "importance-of-keeping-personal-history": "opinion-personal",
    "nauvoo-willow-tree": "opinion-personal",
    "women-in-scripture-challenge": "opinion-promo",
    "questions-to-ask-yourself-when-you-come": "opinion-personal",
    "all-women-are-mothers": "opinion-social",
    "modern-day-prophetess": "opinion-personal",
    "if-you-ever-wanted-to-learn-ancient": "opinion-personal",
    "why-being-a-mom-is-just-as-cool": "opinion-personal",
    "okay-i-think-i-like-sister-burton": "opinion-personal",
    "mary-knew-2": "opinion-personal",
}


def extract_urls(filepath):
    """Parse URLs from the numbered list format."""
    urls = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\d+\.\s+(https?://\S+?)(?:\s+\(.*\))?$", line.strip())
            if m:
                urls.append(m.group(1))
    return urls


def get_slug(url):
    """Extract the slug from a URL."""
    return url.rstrip("/").split("/")[-1].replace(".html", "")


def slug_match(url, slug_set):
    """Check if any slug in the set matches a substring of the URL."""
    for s in slug_set:
        if s in url:
            return True
    return False


def classify(url):
    """Return (category, reason)."""
    slug = get_slug(url)

    # Exact slug exclusion
    if slug in EXCLUDE_EXACT:
        return "EXCLUDE", "exact-excluded"

    # Pattern exclusion (personal, promo, etc.)
    for pattern, reason in EXCLUDE_SLUGS.items():
        if pattern.replace(".html", "") in url:
            return "EXCLUDE", reason

    # Opinion essays
    for pattern, reason in OPINION_SLUGS.items():
        if pattern in url:
            return "EXCLUDE", reason

    # Tier 1: profiles
    if slug_match(url, PROFILE_SLUGS):
        return "PROFILE", "woman-profile"

    # Tier 2: scriptural analysis
    if slug_match(url, SCRIPTURAL_ANALYSIS_SLUGS):
        return "ANALYSIS", "scriptural-analysis"

    # Anything that survived all filters but wasn't classified
    return "UNCLASSIFIED", "needs-review"


def main():
    urls = extract_urls(RAW_FILE)
    print(f"Parsed {len(urls)} URLs from {RAW_FILE.name}")

    profiles, analysis, exclude, unclassified = [], [], [], []
    for url in urls:
        cat, reason = classify(url)
        if cat == "PROFILE":
            profiles.append(url)
        elif cat == "ANALYSIS":
            analysis.append(url)
        elif cat == "EXCLUDE":
            exclude.append((url, reason))
        else:
            unclassified.append(url)

    # Write profile list (Tier 1 — download these)
    p_path = OUT_DIR / "wits_urls_profiles.txt"
    with open(p_path, "w", encoding="utf-8") as f:
        f.write(f"# Women in the Scriptures - TIER 1: Woman Profiles\n")
        f.write(f"# {len(profiles)} entries - scripture-based, high corpus value\n")
        f.write(f"# Source: womeninthescriptures.com\n\n")
        for url in sorted(profiles):
            f.write(url + "\n")

    # Write analysis list (Tier 2 — review before download)
    a_path = OUT_DIR / "wits_urls_analysis.txt"
    with open(a_path, "w", encoding="utf-8") as f:
        f.write(f"# Women in the Scriptures - TIER 2: Scriptural Analysis\n")
        f.write(f"# {len(analysis)} entries - text-focused essays, review for bias\n")
        f.write(f"# Source: womeninthescriptures.com\n\n")
        for url in sorted(analysis):
            f.write(url + "\n")

    # Write exclude list
    exc_path = OUT_DIR / "wits_urls_exclude.txt"
    with open(exc_path, "w", encoding="utf-8") as f:
        f.write(f"# Women in the Scriptures - Excluded URLs\n")
        f.write(f"# {len(exclude)} entries\n\n")
        by_reason = {}
        for url, reason in exclude:
            by_reason.setdefault(reason, []).append(url)
        for reason in sorted(by_reason):
            f.write(f"\n## {reason} ({len(by_reason[reason])})\n")
            for url in sorted(by_reason[reason]):
                f.write(f"  {url}\n")

    # Write unclassified (if any)
    if unclassified:
        u_path = OUT_DIR / "wits_urls_unclassified.txt"
        with open(u_path, "w", encoding="utf-8") as f:
            f.write(f"# Women in the Scriptures - Unclassified ({len(unclassified)})\n\n")
            for url in sorted(unclassified):
                f.write(url + "\n")

    print(f"\nResults:")
    print(f"  PROFILES (Tier 1):  {len(profiles):>4}  -> {p_path.name}")
    print(f"  ANALYSIS (Tier 2):  {len(analysis):>4}  -> {a_path.name}")
    print(f"  EXCLUDED:           {len(exclude):>4}  -> {exc_path.name}")
    if unclassified:
        print(f"  UNCLASSIFIED:       {len(unclassified):>4}  -> wits_urls_unclassified.txt")

    # Exclusion breakdown
    by_reason = {}
    for _, reason in exclude:
        by_reason[reason] = by_reason.get(reason, 0) + 1
    print(f"\nExclusion breakdown:")
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        print(f"  {reason:<25} {count:>4}")


if __name__ == "__main__":
    main()
