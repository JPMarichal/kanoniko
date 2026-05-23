# Workspace Migration Specifications

> **Status:** Design phase (pre-implementation)
> **Date:** 2026-05-17
> **Author:** JPMarichal

Este documento especifica la migración de kanoniko desde un monolito a una arquitectura uv + hatch workspaces con diseño specs-driven.

---

## 1. Motivación

### Problemas Actuales

1. **Monolito acoplado** - Todos los componentes en un solo paquete `alejandria`
2. **Dificultad de testing** - No hay separación clara entre dominios
3. **Deployment monolítico** - No se pueden desplegar componentes independientemente
4. **Falta de contratos** - No hay especificaciones formales entre componentes
5. **Productos futuros** - Sitios Wordpress, apps móviles necesitan backend limpio

### Objetivos

1. **Separación por dominios** - Core, knowledge, ingestion, api como paquetes independientes
2. **Contratos formales** - Specs-driven design con Pydantic schemas y protocols
3. **Workspace unificado** - uv + hatch para desarrollo coordinado
4. **Productos independientes** - Apps consumen API REST, no código Python
5. **Type safety** - mypy estricto cross-paquete

---

## 2. Arquitectura Objetivo

### Estructura del Repo Principal

```
kanoniko/                              # Repo Python (backend + corpus + prods)
├── pyproject.toml                     # Workspace config (hatch)
├── uv.lock                            # Lock file compartido
├── .pre-commit-config.yaml            # Validación automática
├── corpus/                            # Corpus (640 MB, 119,810 archivos)
│   ├── en/                            # 80,847 archivos
│   └── es/                            # 38,962 archivos
├── packages/                          # Paquetes Python independientes
│   ├── core/                          # alejandria-core
│   │   ├── pyproject.toml
│   │   ├── src/alejandria_core/
│   │   │   ├── specs/                 # Especificaciones para búsqueda semántica
│   │   │   │   ├── storage_schemas.py
│   │   │   │   ├── search_schemas.py
│   │   │   │   └── protocols.py
│   │   │   ├── storage/               # Specs inline en código
│   │   │   │   └── textual.py        # Pydantic + Protocol inline
│   │   │   ├── search/
│   │   │   │   └── semantic.py       # Specs inline
│   │   │   └── embeddings/
│   │   └── tests/
│   │       ├── properties/            # Property-based tests (Hypothesis)
│   │       └── integration/
│   ├── knowledge/                     # alejandria-knowledge
│   │   ├── pyproject.toml
│   │   ├── src/alejandria_knowledge/
│   │   │   ├── specs/                 # Especificaciones para búsqueda semántica
│   │   │   │   ├── kg_schemas.py
│   │   │   │   └── protocols.py
│   │   │   ├── kg/
│   │   │   │   └── graph_client.py   # Specs inline
│   │   │   └── extraction/
│   │   └── tests/
│   │       ├── properties/
│   │       └── integration/
│   ├── ingestion/                     # alejandria-ingestion
│   │   ├── pyproject.toml
│   │   ├── src/alejandria_ingestion/
│   │   │   ├── specs/                 # Especificaciones para búsqueda semántica
│   │   │   └── ingestion/             # Specs inline
│   │   └── tests/
│   │       └── integration/
│   └── api/                           # alejandria-api
│       ├── pyproject.toml
│       ├── src/alejandria_api/
│       │   ├── specs/                 # Especificaciones para búsqueda semántica
│       │   │   └── api_schemas.py
│       │   ├── api/
│       │   │   └── routes_search.py   # FastAPI genera OpenAPI
│       │   ├── chat/
│       │   ├── cli.py
│       │   └── mcp_server.py
│       └── tests/
│           └── integration/
├── scripts/
│   ├── validate.sh                    # Validación unificada
│   ├── visualize_deps.py              # Grafo de dependencias
│   └── generate_openapi.py            # Generar OpenAPI desde código
├── prods/                             # Contenido estático (markdown)
│   ├── formas-t/                      # 128 formas doctrinales
│   ├── ilustraciones/                 # 53 ilustraciones
│   ├── discursos/                     # 5 discursos
│   ├── articulos/                     # 29 artículos
│   ├── dossiers/                      # 13 dossiers
│   ├── mapas/                         # 1 mapa
│   └── BACKLOG.md
├── tests/                             # Tests integracionales cross-paquete
├── docs/
│   ├── ARCHITECTURE.yml               # Estructura consumible por IA
│   ├── dependency-graph.svg           # Grafo visual
│   └── workspace-migration-specs.md   # Este documento
└── benchmarks/                        # Benchmarks
```

### Repositorios Separados (Productos Complejos)

```
juanpablomarichal/wordpress-alejandria/     # Sitio Wordpress
├── wp-content/
│   ├── themes/custom-theme/
│   └── plugins/alejandria-api-client/
├── composer.json
└── .env

juanpablomarichal/alejandria-nextjs/       # App Next.js (explorador KG)
├── src/
│   ├── components/
│   └── lib/alejandria-client.ts
├── package.json
└── .env

juanpablomarichal/alejandria-mobile/       # App móvil (React Native)
├── src/
│   └── services/alejandria-api.ts
├── package.json
└── .env
```

---

## 3. Especificaciones Specs-Driven

### Principios

1. **Specs duales** - `specs/` para búsqueda semántica + specs inline en código para contexto
2. **Contratos entre paquetes** - Cada paquete expresa schemas/protocols como API pública
3. **Property-based testing** - Hypothesis para validación automática de propiedades
4. **OpenAPI generado** - FastAPI genera OpenAPI automáticamente desde Pydantic
5. **Type safety** - mypy estricto con pre-commit hooks
6. **Validación unificada** - Scripts unificados para todas las validaciones

### Especificación de Core

#### `packages/core/src/alejandria_core/specs/storage_schemas.py`

```python
"""Contracts for storage layer - implementation-agnostic specifications."""

from pydantic import BaseModel, Field
from typing import Protocol, runtime_checkable
from enum import Enum


class StorageBackend(str, Enum):
    """Supported storage backends."""
    SQLITE = "sqlite"
    POSTGRES = "postgres"


class ChunkMetadata(BaseModel):
    """Specification for chunk metadata."""
    file_path: str = Field(..., description="Source file path")
    chunk_index: int = Field(..., ge=0)
    reference: str | None = None
    start_char: int | None = None
    end_char: int | None = None
    language: str = Field("en", pattern="^(en|es)$")
    metadata: dict = Field(default_factory=dict)


class SearchQuery(BaseModel):
    """Specification for search queries."""
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResult(BaseModel):
    """Specification for search results."""
    chunk_id: int
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    metadata: ChunkMetadata


@runtime_checkable
class TextualSearchEngine(Protocol):
    """Protocol for textual search engines - contract specification."""
    
    async def search(self, query: SearchQuery) -> list[SearchResult]:
        """Execute textual search query."""
        ...
    
    async def index_chunk(self, chunk_id: int, text: str, metadata: ChunkMetadata) -> None:
        """Index a chunk for textual search."""
        ...
```

#### `packages/core/src/alejandria_core/specs/search_schemas.py`

```python
"""Contracts for search engines - implementation-agnostic specifications."""

from pydantic import BaseModel, Field
from typing import Protocol, runtime_checkable
from enum import Enum


class SearchMode(str, Enum):
    """Search modes."""
    TEXTUAL = "textual"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class SemanticSearchQuery(BaseModel):
    """Specification for semantic search queries."""
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)
    model: str = Field("paraphrase-multilingual-MiniLM-L12-v2")


class SemanticSearchResult(BaseModel):
    """Specification for semantic search results."""
    chunk_id: int
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    embedding: list[float] | None = None


@runtime_checkable
class SemanticSearchEngine(Protocol):
    """Protocol for semantic search engines - contract specification."""
    
    async def search(self, query: SemanticSearchQuery) -> list[SemanticSearchResult]:
        """Execute semantic search query."""
        ...
    
    async def index_chunk(self, chunk_id: int, text: str) -> None:
        """Index a chunk for semantic search."""
        ...
```

### Especificación de Knowledge

#### `packages/knowledge/src/alejandria_knowledge/specs/kg_schemas.py`

```python
"""Contracts for knowledge graph - implementation-agnostic specifications."""

from pydantic import BaseModel, Field
from typing import Protocol, runtime_checkable
from enum import Enum


class EntityType(str, Enum):
    """Standard entity types."""
    PERSON = "person"
    PLACE = "place"
    CONCEPT = "concept"
    ORGANIZATION = "organization"
    SCRIPTURE = "scripture"


class RelationType(str, Enum):
    """Standard relation types."""
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    SPOUSE_OF = "spouse_of"
    AUTHORED = "authored"
    MENTIONED_IN = "mentioned_in"
    PROPHESIED = "prophesied"


class Entity(BaseModel):
    """Specification for an entity."""
    id: int
    name: str = Field(..., min_length=1)
    type: EntityType
    aliases: list[str] = Field(default_factory=list)
    disambiguator: str | None = None
    metadata: dict = Field(default_factory=dict)


class Relation(BaseModel):
    """Specification for a relation."""
    id: int
    source_id: int
    target_id: int
    type: RelationType
    confidence: str = Field("llm_low", pattern="^(curated|metadata|llm_high|llm_low|ner)$")
    source_ref: str | None = None
    properties: dict = Field(default_factory=dict)


@runtime_checkable
class GraphClient(Protocol):
    """Protocol for graph clients - contract specification."""
    
    async def find_entity(self, name: str, entity_type: EntityType | None = None) -> Entity | None:
        """Find an entity by name."""
        ...
    
    async def get_neighbors(self, entity_id: int, relation_types: list[RelationType] | None = None) -> list[Relation]:
        """Get neighbors of an entity."""
        ...
    
    async def add_relation(self, relation: Relation) -> int:
        """Add a relation to the graph."""
        ...
    
    async def get_entity_profile(self, entity_id: int) -> dict:
        """Get entity profile with summaries."""
        ...
```

### Especificación de API

#### `packages/api/src/alejandria_api/api/routes_search.py`

```python
"""FastAPI routes with OpenAPI generated automatically from Pydantic."""

from fastapi import APIRouter
from alejandria_core.specs.search_schemas import SearchQuery, SearchResult
from alejandria_api.specs.api_schemas import HybridSearchRequest, HybridSearchResponse

router = APIRouter()

@router.post("/search/hybrid", response_model=HybridSearchResponse)
async def search_hybrid(request: HybridSearchRequest) -> HybridSearchResponse:
    """FastAPI genera OpenAPI automáticamente desde estos Pydantic models."""
    results = await hybrid_search(request)
    return HybridSearchResponse(
        query=request.query,
        mode="hybrid",
        count=len(results),
        results=results
    )
```

**Nota:** OpenAPI se genera automáticamente desde FastAPI. No mantener `openapi.yaml` manual. Use `scripts/generate_openapi.py` para exportar si es necesario.

---

## 4. Property-Based Testing con Hypothesis

### Estructura de Tests

Cada paquete tiene dos categorías de tests:

1. **Property-based tests** - Validan propiedades generales usando Hypothesis
2. **Integration tests** - Validan integración cross-paquete

### Ejemplo: Property-Based Test para Core

#### `packages/core/tests/properties/test_search_properties.py`

```python
"""Property-based tests for search using Hypothesis."""

from hypothesis import given, strategies as st
from alejandria_core.storage.textual import TextualSearchEngine
from alejandria_core.specs.storage_schemas import SearchQuery, ChunkMetadata

@given(st.text(min_size=1, max_size=100), st.integers(min_value=1, max_value=100))
def test_search_always_returns_valid_results(query, limit):
    """Property: search always returns results with valid scores."""
    engine = TextualSearchEngine()
    results = await engine.search(SearchQuery(query=query, limit=limit))
    
    for result in results:
        assert 0.0 <= result.score <= 1.0
        assert result.metadata.chunk_index >= 0
        assert len(result.text) > 0

@given(st.text(min_size=1), st.integers(min_value=0, max_value=1000))
def test_chunk_metadata_validation(file_path, chunk_index):
    """Property: chunk metadata validates file paths and indices."""
    metadata = ChunkMetadata(
        file_path=file_path if file_path.endswith('.txt') else f"{file_path}.txt",
        chunk_index=chunk_index,
        language="en"
    )
    assert metadata.file_path.endswith('.txt')
    assert metadata.chunk_index == chunk_index
```

### Ejemplo: Property-Based Test para Knowledge

#### `packages/knowledge/tests/properties/test_kg_properties.py`

```python
"""Property-based tests for knowledge graph using Hypothesis."""

from hypothesis import given, strategies as st
from alejandria_knowledge.kg.graph_client import GraphClient
from alejandria_knowledge.specs.kg_schemas import Relation, RelationType

@given(st.integers(min_value=1, max_value=1000), st.integers(min_value=1, max_value=1000))
def test_add_relation_preserves_confidence(source_id, target_id):
    """Property: adding relation preserves confidence values."""
    client = GraphClient()
    relation = Relation(
        id=1,
        source_id=source_id,
        target_id=target_id,
        type=RelationType.PARENT_OF,
        confidence="curated"
    )
    relation_id = await client.add_relation(relation)
    assert isinstance(relation_id, int)
    assert relation_id > 0
```

### Beneficios de Property-Based Testing

- **Cobertura de edge cases** - Hypothesis genera casos que no pensarías manualmente
- **Menos código** - Una propiedad reemplaza muchos test cases manuales
- **Bug finding** - Encuentra bugs en edge cases que tests manuales no encuentran
- **Mantenimiento** - Es más fácil mantener propiedades que test cases específicos

---

## 5. Type Safety con Pre-Commit Hooks

### Configuración Mypy

#### `pyproject.toml` (raíz)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### Pre-Commit Hook

#### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
        args: [--strict, packages/]
        additional_dependencies: [pydantic>=2.0, fastapi>=0.115.0]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix, packages/]
  - repo: local
    hooks:
      - id: pytest-properties
        name: Run property-based tests
        entry: uv run pytest packages/*/tests/properties/
        language: system
        pass_filenames: false
```

### Instalación y Uso

```bash
# Instalar pre-commit hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files

# Los hooks corren automáticamente antes de cada commit
git add .
git commit -m "feat: add new feature"  # pre-commit corre mypy + ruff + pytest
```

---

## 6. Documentación Estructurada para IA

### ARCHITECTURE.yml

#### `docs/ARCHITECTURE.yml`

```yaml
packages:
  core:
    description: "Storage and search layer"
    dependencies: []
    exports:
      - TextualSearchEngine
      - SemanticSearchEngine
      - ChunkMetadata
    contracts:
      - storage_schemas
      - search_schemas
    location: packages/core/
  
  knowledge:
    description: "Knowledge graph and entity extraction"
    dependencies: [core]
    exports:
      - GraphClient
      - EntityExtractor
    contracts:
      - kg_schemas
    location: packages/knowledge/
  
  ingestion:
    description: "Corpus ingestion pipeline"
    dependencies: [core, knowledge]
    exports:
      - IngestionPipeline
      - Chunker
    contracts:
      - ingestion_schemas
    location: packages/ingestion/
  
  api:
    description: "REST API, CLI, and MCP server"
    dependencies: [core, knowledge, ingestion]
    exports:
      - FastAPI app
      - CLI
      - MCP server
    contracts:
      - api_schemas
    location: packages/api/

data_flow:
  ingestion:
    source: corpus/
    pipeline: ingestion → core → knowledge
    output: Postgres
  query:
    input: API
    flow: api → core → knowledge
    output: Search results
```

## 7. Visualización de Dependencias

### Script para Generar Grafo

#### `scripts/visualize_deps.py`

```python
"""Generate dependency graph visualization."""

import graphviz
from pathlib import Path
import toml

def parse_dependencies(pyproject_path: Path) -> list[str]:
    """Parse dependencies from pyproject.toml."""
    with open(pyproject_path) as f:
        data = toml.load(f)
    deps = data.get('project', {}).get('dependencies', [])
    return [d.split('>=')[0].split('==')[0] for d in deps]

def generate_dependency_graph():
    """Generate dependency graph for all packages."""
    dot = graphviz.Digraph(comment='Alejandria Package Dependencies')
    
    for pkg_dir in Path('packages').iterdir():
        if not pkg_dir.is_dir():
            continue
        
        pyproject = pkg_dir / 'pyproject.toml'
        if not pyproject.exists():
            continue
        
        deps = parse_dependencies(pyproject)
        pkg_name = pkg_dir.name
        
        dot.node(pkg_name)
        
        for dep in deps:
            if dep.startswith('alejandria-'):
                dep_name = dep.replace('alejandria-', '')
                dot.edge(pkg_name, dep_name)
    
    dot.render('docs/dependency-graph', format='svg', cleanup=True)
    print('Dependency graph generated at docs/dependency-graph.svg')

if __name__ == '__main__':
    generate_dependency_graph()
```

### Uso

```bash
# Generar grafo
python scripts/visualize_deps.py

# El grafo se guarda en docs/dependency-graph.svg
```

### Configuración uv + Hatch

#### `pyproject.toml` (Raíz)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "kanoniko-workspace"
version = "0.1.0"
description = "Workspace monorepo for Alejandria"

[tool.hatch]
metadata.allow-direct-references = true

[tool.hatch.envs.default]
dependencies = ["uv"]

[tool.hatch.envs.test]
dependencies = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "hypothesis>=6.0",
    "mypy>=1.8",
    "graphviz>=0.20",
]

[tool.hatch.envs.test.scripts]
test = "pytest packages/"
properties = "pytest packages/*/tests/properties/"
validate = "./scripts/validate.sh"
```

### packages/core/pyproject.toml

```toml
[project]
name = "alejandria-core"
version = "0.1.0"
description = "Core storage and search layer (specs-driven)"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "psycopg[binary]>=3.1",
    "pgvector>=0.3",
    "sentence-transformers>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "mypy>=1.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/alejandria_core"]
```

### packages/knowledge/pyproject.toml

```toml
[project]
name = "alejandria-knowledge"
version = "0.1.0"
description = "Knowledge graph and entity extraction (specs-driven)"
requires-python = ">=3.11"
dependencies = [
    "alejandria-core",
    "spacy>=3.7",
    "neo4j>=5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "mypy>=1.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/alejandria_knowledge"]
```

### packages/ingestion/pyproject.toml

```toml
[project]
name = "alejandria-ingestion"
version = "0.1.0"
description = "Corpus ingestion pipeline (specs-driven)"
requires-python = ">=3.11"
dependencies = [
    "alejandria-core",
    "alejandria-knowledge",
    "beautifulsoup4>=4.12",
    "markdown-it-py>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "mypy>=1.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/alejandria_ingestion"]
```

### packages/api/pyproject.toml

```toml
[project]
name = "alejandria-api"
version = "0.1.0"
description = "REST API, CLI, and MCP server (specs-driven)"
requires-python = ">=3.11"
dependencies = [
    "alejandria-core",
    "alejandria-knowledge",
    "alejandria-ingestion",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30",
    "anthropic>=0.40",
    "openai>=1.50",
    "click>=8.1",
]

[project.scripts]
alejandria = "alejandria_api.cli:main"
alejandria-api = "alejandria_api.main:start"
alejandria-mcp = "alejandria_api.mcp_server:start"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "mypy>=1.8",
    "openapi-spec-validator>=0.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/alejandria_api"]
```

---

## 8. Scripts de Validación Unificados

### Script de Validación

#### `scripts/validate.sh`

```bash
#!/bin/bash
set -e

echo "=== Alejandria Workspace Validation ==="

echo "[1/5] Type checking..."
uv run mypy packages/

echo "[2/5] Property-based tests..."
uv run pytest packages/*/tests/properties/ -v

echo "[3/5] Integration tests..."
uv run pytest tests/ -v

echo "[4/5] Dependency graph consistency..."
python scripts/visualize_deps.py

echo "[5/5] OpenAPI generation..."
python scripts/generate_openapi.py

echo "=== All validations passed! ==="
```

### Script de Generación OpenAPI

#### `scripts/generate_openapi.py`

```python
"""Generate OpenAPI spec from FastAPI."""

import json
from alejandria_api.main import app

def generate_openapi():
    """Generate OpenAPI spec from FastAPI app."""
    spec = app.openapi()
    
    with open('docs/openapi.json', 'w') as f:
        json.dump(spec, f, indent=2)
    
    print('OpenAPI spec generated at docs/openapi.json')

if __name__ == '__main__':
    generate_openapi()
```

### Uso

```bash
# Validación completa
./scripts/validate.sh

# Validación individual
uv run mypy packages/
uv run pytest packages/*/tests/properties/
python scripts/visualize_deps.py
python scripts/generate_openapi.py
```

---

## 9. Estrategia para el Corpus

### Estado Actual

- **Tamaño**: 119,810 archivos (~640 MB)
- **Estructura**: `corpus/en/` (80,847 archivos) + `corpus/es/` (38,962 archivos)
- **Git**: Trackeado en el repo (backup/history)
- **Uso**: Bind-mounted en Docker para el pipeline de ingesta

### Estrategia: Corpus en Repo Principal

**Ubicación**: `corpus/` se queda en `kanoniko/`

**Ventajas**:
- Simplicidad: Un solo source of truth
- Git history: Versionado completo del corpus
- Co-ubicación: Scripts de descarga e ingesta en el mismo repo
- 640 MB es manejable: Git LFS no es necesario todavía

**Acceso desde productos**:
- **Opción 1**: Via API REST (endpoints especiales para contenido crudo)
- **Opción 2**: Git clone del repo `kanonico` (solo `corpus/` usando `git sparse-checkout`)

### Git Sparse-Checkout para Productos

Si un producto necesita acceso directo al corpus:

```bash
# Clonar solo corpus usando sparse-checkout
git clone --filter=blob:none --sparse https://github.com/juanpablomarichal/kanoniko.git
cd kanoniko
git sparse-checkout set corpus
```

### Trigger para Cambiar a Repo Separado

Mover a repo separado si:
- Corpus > 2 GB (GitHub clone se vuelve lento)
- Múltiples productos necesitan acceso directo frecuente
- Necesitas Git LFS para archivos binarios grandes
- Corpus tiene su propio ciclo de release independiente

---

## 10. Estrategia para Productos

### Categoría 1: Contenido Estático (se queda en kanoniko)

**Ubicación**: `prods/` dentro del repo Python

**Razón**:
- Son markdown files que no necesitan runtime
- Se versionan junto con el backend
- Pueden ser servidos por cualquier frontend (Wordpress, Next.js, etc.)
- Facilita la integración con skills de Claude (`/ilustracion`, `/articulo`)

**Acceso desde productos**:
- Via API REST (endpoints especiales para servir contenido)
- O via Git clone (para productos que necesitan acceso raw)

### Categoría 2: Aplicaciones (repos separados)

**Ubicación**: Repositorios independientes bajo `juanpablomarichal/`

**Razón**:
- Stack diferente (PHP, JS, etc.) no encaja en workspace Python
- Ciclos de release independientes
- Equipos diferentes pueden trabajar en cada producto
- Deployment independiente (VPS diferente, CDN, etc.)

**Integración**:
- Consumen API REST de Alejandría
- Usan API keys para autenticación
- Implementan caching local para performance

### API REST como Punto de Integración

```
┌─────────────────────────────────────────────────────────────┐
│  kanoniko/ (Python Backend)                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ packages/api/ (FastAPI)                               │   │
│  │  GET /api/search/textual                              │   │
│  │  GET /api/search/semantic                             │   │
│  │  GET /api/search/hybrid                               │   │
│  │  GET /api/kg/profile/{entity}                         │   │
│  │  GET /api/kg/neighbors/{entity}                       │   │
│  │  GET /api/chat/ask                                    │   │
│  │  POST /api/chat/ask                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │ HTTP/JSON
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
│  Wordpress     │   │  Next.js App    │   │  Mobile App     │
│  (PHP)         │   │  (TypeScript)   │   │  (React Native) │
│                │   │                 │   │                 │
│  Plugin:       │   │  Cliente:       │   │  Cliente:       │
│  alejandria-   │   │  @alejandria/   │   │  @alejandria/   │
│  api-client    │   │  api-client     │   │  api-client     │
└────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## 10. Patrones de Diseño Relevantes

### Patrones Ya Implementados

El proyecto ya usa correctamente varios patrones:

1. **Factory Pattern** - `make_*` factories en `api/dependencies.py` para crear instancias
2. **Strategy Pattern** - Feature flag `ALEJANDRIA_STORAGE_BACKEND` para swappear SQLite/Postgres
3. **Dependency Injection** - Inyección de dependencias vía factories en API/CLI/MCP
4. **Protocol-based Programming** - Python protocols como contratos (ya en propuesta specs-driven)

### Patrones a Considerar Adicionalmente

#### 1. Repository Pattern (Formalizar)

**Estado actual:** Abstracción parcial con factories.

**Mejora:** Formalizar Repository Pattern para storage layer:

```python
# packages/core/src/alejandria_core/storage/repository.py
from abc import ABC, abstractmethod

class ChunkRepository(ABC):
    """Repository pattern for chunk storage."""
    
    @abstractmethod
    async def save(self, chunk: Chunk) -> None:
        ...
    
    @abstractmethod
    async def find_by_id(self, chunk_id: int) -> Chunk | None:
        ...

class PostgresChunkRepository(ChunkRepository):
    """Postgres implementation."""
    ...

class SQLiteChunkRepository(ChunkRepository):
    """SQLite implementation (legacy)."""
    ...
```

**Beneficio:** Abstracción más limpia, testing más fácil con mocks.

---

#### 2. Adapter Pattern (Para KG Client)

**Estado actual:** `PostgresGraphClient` tiene 30 métodos con `NotImplementedError`.

**Mejora:** Adapter Pattern para gradualmente portar métodos:

```python
# packages/knowledge/src/alejandria_knowledge/kg/adapter.py
class Neo4jAdapter:
    """Adapter to Neo4j for unimplemented methods."""
    def __init__(self, neo4j_client):
        self.neo4j = neo4j_client
    
    def get_typed_relations(self, ...):
        return self.neo4j.get_typed_relations(...)

class PostgresGraphClient:
    """Postgres client with adapter fallback."""
    def __init__(self, postgres_client, neo4j_adapter=None):
        self.postgres = postgres_client
        self.neo4j = neo4j_adapter
    
    def get_typed_relations(self, ...):
        if self.neo4j:
            return self.neo4j.get_typed_relations(...)
        raise NotImplementedError(...)
```

**Beneficio:** Gradual migration sin breaking changes.

---

#### 3. Observer Pattern (Para Indexing Events)

**Nuevo patrón:** Notificar cambios en indexing:

```python
# packages/ingestion/src/alejandria_ingestion/events.py
from typing import Protocol

@runtime_checkable
class IndexObserver(Protocol):
    async def on_chunk_indexed(self, chunk_id: int) -> None:
        ...
    
    async def on_file_completed(self, file_path: str) -> None:
        ...

class IndexProgressTracker:
    def __init__(self):
        self.observers: list[IndexObserver] = []
    
    def register(self, observer: IndexObserver):
        self.observers.append(observer)
    
    async def notify_chunk_indexed(self, chunk_id: int):
        for observer in self.observers:
            await observer.on_chunk_indexed(chunk_id)
```

**Beneficio:** Desacopla indexing de monitoreo/progresos.

---

#### 4. Builder Pattern (Para Configuración Compleja)

**Nuevo patrón:** Para configuración de search engines:

```python
# packages/core/src/alejandria_core/search/builder.py
class SearchEngineBuilder:
    def __init__(self):
        self._backend = None
        self._model = None
        self._index_path = None
    
    def with_backend(self, backend: StorageBackend):
        self._backend = backend
        return self
    
    def with_model(self, model: str):
        self._model = model
        return self
    
    def with_index_path(self, path: str):
        self._index_path = path
        return self
    
    def build(self) -> SearchEngine:
        return SearchEngine(
            backend=self._backend,
            model=self._model,
            index_path=self._index_path
        )

# Uso
engine = (SearchEngineBuilder()
    .with_backend(StorageBackend.POSTGRES)
    .with_model("paraphrase-multilingual-MiniLM-L12-v2")
    .build())
```

**Beneficio:** Configuración compleja más legible.

---

## 11. Pendientes Críticos Antes de Workspace Migration

Según `docs/postgres-migration-status.md` y revisión actual del código, la migración a Postgres está en **Phase 1**:

**Completado:**
- ✅ Infra completa (Postgres 16 + pgvector en IONOS VPS)
- ✅ Read path completo (search layer ya está 100% en Postgres - textual.py y semantic.py)
- ✅ Storage layer Postgres (connection, schema, DDL)
- ✅ KG cleanup scripts (R0, R7)
- ✅ Feature-flagged (default "sqlite")

**Pendiente:**
- ❌ Write path NO migrado (ingestion aún usa SQLite/Neo4j)
- ❌ KG client parcial (3/34 métodos implementados)

### Blockers

#### 1. PR #2: postgres-write-path (3-5 días) - CRÍTICO

**Estado:** Write path de ingesta aún está en SQLite/Neo4j.

**Bloquea:**
- La migración a workspace asume stack estable
- Mover código mientras el write path está en transición es arriesgado
- `ingestion/registry.py` y `knowledge/profile_store.py` necesitan refactor

**Recomendación:** Completar PR #2 antes de workspace migration.

---

#### 2. PR #1: postgres-kg-client-rest (3-4 días) - ALTA PRIORIDAD

**Estado:** KG client tiene 30/34 métodos implementados. Tiers 2c/2d pendientes.

**Bloquea:**
- `knowledge/` package en workspace tendrá código parcialmente implementado
- Tests de integración fallarán

**Recomendación:** Completar PR #1 antes de extraer `knowledge/` package.

---

#### 3. KG Ingestion Refactor (docs/kg-ingestion-refactor.md) - MEDIA PRIORIDAD

**Estado:** Backlog R0-R10 de hygiene del KG. R0 y R7 completados.

**Bloquea:**
- `knowledge/` package tendrá código que necesita limpieza
- Mejor hacerlo antes de separar en package

**Recomendación:** Completar R1-R3 (filtros en ingesta) antes de workspace migration.

---

## 12. Estrategia Recomendada

### Opción A: Completar Postgres Migration Primero (Recomendada)

```
1. Completar PR #2: postgres-write-path (3-5 días)
2. Completar PR #1: postgres-kg-client-rest (3-4 días)
3. Completar R1-R3 de KG refactor (1-2 días)
4. PR #3: postgres-cutover (1-2 semanas, opcional)
5. Workspace migration (5-7 días)
```

**Ventajas:**
- Stack estable antes de reestructuración
- Menos riesgo de breaking changes
- Tests más confiables

**Tiempo total:** ~3-4 semanas

---

### Opción B: Workspace Migration Paralela (Arriesgado)

```
1. Comenzar workspace migration (Fase 1-2)
2. Paralelamente completar PR #2 y #1
3. Integrar Postgres write path en workspace
```

**Ventajas:**
- Más rápido en teoría

**Desventajas:**
- Alto riesgo de merge conflicts
- Difícil debuggear problemas cross-stack
- No recomendado

---

### Recomendación Final

**Completar Postgres migration antes de workspace migration.**

El sistema está en medio de una transición crítica (SQLite+Neo4j → Postgres). Añadir la complejidad de workspace migration encima de esto es innecesariamente arriesgado.

**Orden recomendado:**
1. PR #2: postgres-write-path
2. PR #1: postgres-kg-client-rest  
3. KG refactor R1-R3
4. Workspace migration
5. PR #3: postgres-cutover (opcional, puede ser después)

---

## 13. Riesgos y Mitigación

### Riesgo 1: Breaking Changes en Producción

**Descripción:** Migración a workspace podría introducir breaking changes que afecten producción.

**Probabilidad:** Media
**Impacto:** Alto

**Mitigación:**
- Feature flags para cada fase de migración
- Testing exhaustivo en staging antes de producción
- Rollback plan documentado (git revert)
- Monitoreo de errores en producción post-deploy
- Gradual cutover (canary deployment)

**Plan de contingencia:**
- Si errores críticos: revertir PR inmediatamente
- Si errores no críticos: hotfix en branch separado

---

### Riesgo 2: Dependencies Cross-Package Rota

**Descripción:** Imports entre paquetes podrían romperse durante la separación.

**Probabilidad:** Alta
**Impacto:** Medio

**Mitigación:**
- Validar imports después de cada fase con `uv run mypy packages/`
- Tests de integración cross-paquete en `tests/`
- Script `scripts/validate.sh` ejecuta todas las validaciones
- Property-based tests para validar contratos

**Plan de contingencia:**
- Si imports rotos: revisar `pyproject.toml` de cada paquete
- Si circular dependencies: refactorizar para eliminar ciclo

---

### Riesgo 3: Performance Degradation

**Descripción:** Workspace overhead podría afectar performance de queries/ingesta.

**Probabilidad:** Baja
**Impacto:** Medio

**Mitigación:**
- Benchmarks antes y después de migración
- Profile de queries en cada fase
- Comparación de latencia con baseline actual
- Optimización si degradation > 10%

**Plan de contingencia:**
- Si degradation > 20%: revertir y optimizar antes de retry
- Si degradation 10-20%: aceptable, monitorear

---

### Riesgo 4: Pre-commit Hooks Lentos

**Descripción:** Pre-commit hooks (mypy, ruff, pytest) podrían ser lentos y afectar workflow.

**Probabilidad:** Media
**Impacto:** Bajo

**Mitigación:**
- Configurar hooks para correr solo en archivos modificados
- Usar caching de mypy (`.mypy_cache/`)
- Limitar pytest a tests relevantes (no correr todos en pre-commit)
- Opción de bypass con `--no-verify` en commits urgentes

**Plan de contingencia:**
- Si hooks > 30s: optimizar configuración
- Si hooks > 60s: mover tests a CI, mantener solo mypy/ruff en pre-commit

---

### Riesgo 5: Property-Based Tests Encuentran Bugs Ocultos

**Descripción:** Hypothesis podría encontrar bugs en código existente que no se conocían.

**Probabilidad:** Media
**Impacto:** Medio

**Mitigación:**
- Documentar bugs encontrados
- Priorizar fixes según severidad
- No bloquear migración por bugs no críticos
- Crear issues en backlog para bugs no críticos

**Plan de contingencia:**
- Si bug crítico: fix antes de continuar
- Si bug no crítico: crear issue, continuar migración

---

### Riesgo 6: Postgres Migration Incompleta Interfiere

**Descripción:** Si Postgres migration no está completa, workspace migration podría fallar.

**Probabilidad:** Alta (si se ignora prerequisitos)
**Impacto:** Alto

**Mitigación:**
- Completar PR #2 (postgres-write-path) antes
- Completar PR #1 (postgres-kg-client-rest) antes
- Validar stack Postgres en Fase 0
- No proceder si tests Postgres fallan

**Plan de contingencia:**
- Si Postgres migration incompleta: pausar workspace migration
- Completar Postgres migration primero

---

### Riesgo 7: Corpus Acceso Rompe

**Descripción:** Scripts de ingesta podrían perder acceso a corpus después de reestructuración.

**Probabilidad:** Baja
**Impacto:** Alto

**Mitigación:**
- Validar path de corpus en cada fase
- Tests de ingesta con corpus real
- Documentar path absoluto vs relativo
- Usar environment variable para corpus path

**Plan de contingencia:**
- Si corpus path roto: actualizar scripts con path correcto
- Si corpus no accesible: verificar Docker bind-mount

---

### Riesgo 8: MCP Server o CLI Rompe

**Descripción:** Entry points (MCP, CLI) podrían romperse después de separación de paquetes.

**Probabilidad:** Media
**Impacto:** Medio

**Mitigación:**
- Tests de integración para CLI y MCP
- Validar entry points después de Fase 5
- Documentar comandos de prueba
- Rollback si entry points no funcionan

**Plan de contingencia:**
- Si CLI rompe: revisar imports en `cli.py`
- Si MCP rompe: revisar imports en `mcp_server.py`

---

### Riesgo 9: Docker Stack Rompe

**Descripción:** Docker containerization podría romperse después de cambios en estructura.

**Probabilidad:** Baja
**Impacto:** Alto

**Mitigación:**
- Validar Docker build después de cada fase
- Tests de integración en Docker
- Documentar cambios en Dockerfile si necesarios
- Mantener Dockerfile simple (no complejizar)

**Plan de contingencia:**
- Si Docker build falla: revisar `COPY` paths en Dockerfile
- Si runtime Docker falla: revisar volumes y environment variables

---

### Riesgo 10: Time Estimation Incorrecta

**Descripción:** Migración podría tomar más tiempo del estimado (5-7 días).

**Probabilidad:** Media
**Impacto:** Bajo

**Mitigación:**
- Buffer de 2-3 días en estimación
- Priorizar fases críticas
- Dejar fases opcionales para después
- Documentar blockers si surgen

**Plan de contingencia:**
- Si demora > 10 días: reevaluar prioridad
- Si demora > 14 días: considerar split en múltiples PRs

---

### Matriz de Riesgos

| Riesgo | Probabilidad | Impacto | Severidad | Mitigación Principal |
|--------|-------------|---------|-----------|---------------------|
| Breaking changes en producción | Media | Alto | Alto | Feature flags + rollback plan |
| Dependencies cross-package rota | Alta | Medio | Alto | Mypy + tests de integración |
| Performance degradation | Baja | Medio | Medio | Benchmarks + monitoreo |
| Pre-commit hooks lentos | Media | Bajo | Bajo | Optimización + caching |
| Property-based tests encuentran bugs | Media | Medio | Medio | Documentación + priorización |
| Postgres migration incompleta | Alta | Alto | Crítico | Completar prerequisitos |
| Corpus acceso rompe | Baja | Alto | Medio | Tests de ingesta |
| MCP/CLI rompe | Media | Medio | Medio | Tests de integración |
| Docker stack rompe | Baja | Alto | Medio | Validar Docker build |
| Time estimation incorrecta | Media | Bajo | Bajo | Buffer + priorización |

**Severidad:** Crítico > Alto > Medio > Bajo

---

## 14. Plan de Migración por Fases (Actualizado con Prerequisitos)

### Estrategia Git

**No forkear** - Como eres el owner del repositorio, usa branches en tu propio repo con PRs incrementales.

### Prerequisitos (Antes de comenzar)

- [ ] Completar PR #2: postgres-write-path
- [ ] Completar PR #1: postgres-kg-client-rest
- [ ] Completar KG refactor R1-R3
- [ ] Validar que tests pasan en stack Postgres

### Fase 0: Validación de Stack (0.5 días)

```bash
git checkout -b feature/validate-postgres-stack

# Validar que Postgres stack es estable
ALEJANDRIA_STORAGE_BACKEND=postgres uv run pytest tests/
ALEJANDRIA_STORAGE_BACKEND=postgres uv run alejandria search "test"

# Commit y PR
git push origin feature/validate-postgres-stack
```

### Fase 1: Configuración uv + hatch + herramientas (1 día)

```bash
# Crear branch
git checkout -b feature/uv-hatch-phase1-config

# Crear estructura de directorios
mkdir -p packages/{core,knowledge,ingestion,api}
mkdir -p scripts

# Agregar pyproject.toml workspace
# Crear uv.lock inicial
# Crear .pre-commit-config.yaml
# Crear scripts/validate.sh
# Crear scripts/visualize_deps.py
# Crear docs/ARCHITECTURE.yml

# Sin mover código aún

# Instalar pre-commit hooks
pre-commit install

# Validar
uv sync --workspace
./scripts/validate.sh

# Commit y PR
git push origin feature/uv-hatch-phase1-config
```

**Entregables**:
- `pyproject.toml` (raíz) con config de workspace hatch
- `uv.lock` inicial
- `.pre-commit-config.yaml` configurado
- Scripts de validación y visualización
- `docs/ARCHITECTURE.yml` inicial
- Validación: `uv sync --workspace` funciona, pre-commit hooks instalados

### Fase 2: Extraer core (1-2 días)

```bash
git checkout -b feature/uv-hatch-phase2-core

# Mover código
mv src/alejandria/storage packages/core/src/alejandria_core/
mv src/alejandria/search packages/core/src/alejandria_core/
mv src/alejandria/embeddings packages/core/src/alejandria_core/

# Crear specs/ para búsqueda semántica
# Mover código con specs inline (Pydantic + Protocol)
# Crear pyproject.toml de core
# Actualizar imports: from alejandria.storage → from alejandria_core.storage

# Crear property-based tests (Hypothesis)
# Crear integration tests

# Validar
uv run pytest packages/core/tests/
uv run mypy packages/core/

# Commit y PR
git push origin feature/uv-hatch-phase2-core
```

**Entregables**:
- `packages/core/` completo con specs, tests
- Contract tests pasando
- Type checks pasando
- Imports actualizados en código que depende de core

### Fase 3: Extraer knowledge (1-2 días)

```bash
git checkout -b feature/uv-hatch-phase3-knowledge

# Mover código
mv src/alejandria/knowledge packages/knowledge/src/alejandria_knowledge/

# Crear specs/ para búsqueda semántica
# Mover código con specs inline
# Crear pyproject.toml de knowledge
# Actualizar imports
# Resolver dependencias con core

# Crear property-based tests
# Crear integration tests

# Validar
uv run pytest packages/knowledge/tests/
uv run mypy packages/knowledge/

# Commit y PR
git push origin feature/uv-hatch-phase3-knowledge
```

**Entregables**:
- `packages/knowledge/` completo con specs, tests
- Contract tests pasando
- Type checks pasando
- Dependencias con core resueltas

### Fase 4: Extraer ingestion (1 día)

```bash
git checkout -b feature/uv-hatch-phase4-ingestion

# Mover código
mv src/alejandria/ingestion packages/ingestion/src/alejandria_ingestion/

# Crear specs/ para búsqueda semántica
# Mover código con specs inline
# Crear pyproject.toml de ingestion
# Actualizar imports
# Resolver dependencias con core y knowledge

# Crear property-based tests
# Crear integration tests

# Validar
uv run pytest packages/ingestion/tests/
uv run mypy packages/ingestion/

# Commit y PR
git push origin feature/uv-hatch-phase4-ingestion
```

**Entregables**:
- `packages/ingestion/` completo con specs, tests
- Contract tests pasando
- Type checks pasando
- Dependencias resueltas

### Fase 5: Extraer api (1-2 días)

```bash
git checkout -b feature/uv-hatch-phase5-api

# Mover código
mv src/alejandria/api packages/api/src/alejandria_api/
mv src/alejandria/chat packages/api/src/alejandria_api/
mv src/alejandria/cli.py packages/api/src/alejandria_api/
mv src/alejandria/mcp_server.py packages/api/src/alejandria_api/
mv src/alejandria/main.py packages/api/src/alejandria_api/

# Crear specs/ para búsqueda semántica
# Mover código con specs inline (FastAPI genera OpenAPI)
# Crear pyproject.toml de api
# Actualizar imports
# Resolver dependencias con core, knowledge, ingestion

# Crear integration tests
# Validar OpenAPI generado
# Crear integration tests

# Validar
uv run pytest packages/api/tests/
uv run mypy packages/api/

# Commit y PR
git push origin feature/uv-hatch-phase5-api
```

**Entregables**:
- `packages/api/` completo con specs, tests
- OpenAPI spec validado
- Contract tests pasando
- Type checks pasando
- Entry points funcionando (CLI, API, MCP)

### Fase 6: Limpieza final (0.5 día)

```bash
git checkout -b feature/uv-hatch-phase6-cleanup

# Eliminar src/alejandria/ vacío
# Actualizar CLAUDE.md
# Actualizar docs/architecture.md
# Actualizar README

# Validación final
uv run pytest packages/
uv run mypy packages/
uv run alejandria search "test"
uv run alejandria-api  # Test API

# Commit y PR
git push origin feature/uv-hatch-phase6-cleanup
```

**Entregables**:
- Estructura limpia sin código legacy
- Documentación actualizada
- Todos los entry points funcionando
- Tests completos pasando

---

## 12. Workflow de Desarrollo Optimizado

### Desarrollo de Nuevo Feature

```bash
# 1. Escribir código con specs inline (Pydantic + Protocol)
vim packages/core/src/alejandria_core/storage/new_feature.py

# 2. Escribir property-based test
vim packages/core/tests/properties/test_new_feature_properties.py

# 3. Ejecutar test (debe fallar)
uv run pytest packages/core/tests/properties/test_new_feature_properties.py -xvs

# 4. Implementar hasta que pase test
vim packages/core/src/alejandria_core/storage/new_feature.py

# 5. Validación automática en pre-commit
git add packages/core/
git commit -m "feat(core): add new feature"  # pre-commit corre mypy + ruff + pytest

# 6. Validación completa
./scripts/validate.sh
```

### Validación Continua

```bash
# Validación completa (unificada)
./scripts/validate.sh

# Validaciones individuales
uv run mypy packages/
uv run pytest packages/*/tests/properties/
python scripts/visualize_deps.py
```

---

## 13. Criterios de Éxito

### Técnicos

- [ ] Todos los paquetes tienen specs/ para búsqueda semántica
- [ ] Todos los paquetes tienen specs inline en código
- [ ] Property-based tests pasando en todos los paquetes
- [ ] Mypy strict mode pasando en todos los paquetes
- [ ] Pre-commit hooks instalados y funcionando
- [ ] OpenAPI generado automáticamente desde FastAPI
- [ ] uv sync --workspace funciona sin errores
- [ ] Todos los entry points funcionan (CLI, API, MCP)

### Funcionales

- [ ] Búsqueda híbrida funciona igual que antes
- [ ] Knowledge graph queries funcionan igual que antes
- [ ] Ingestión de corpus funciona igual que antes
- [ ] Chat/RAG funciona igual que antes

### Operacionales

- [ ] Property-based tests pasan en < 30s
- [ ] Type check completo pasa en < 10s
- [ ] Build de workspace con uv es < 5s
- [ ] Validación unificada (`./scripts/validate.sh`) pasa
- [ ] Grafo de dependencias generado automáticamente
- [ ] Documentación estructurada (ARCHITECTURE.yml) actualizada

---

## 14. Referencias

- [uv documentation](https://github.com/astral-sh/uv)
- [Hatch documentation](https://hatch.pypa.hatch)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [Pre-commit hooks](https://pre-commit.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Protocol-based programming in Python](https://mypy.readthedocs.io/en/stable/protocols.html)

---

## 16. Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-05-17 | Versión inicial de especificaciones | JPMarichal |
| 2026-05-17 | Optimizaciones: specs duales, property-based testing, pre-commit, visualización, validación unificada | JPMarichal |
| 2026-05-17 | Patrones de diseño y pendientes críticos antes de migración | JPMarichal |
| 2026-05-17 | Riesgos y mitigación con matriz de severidad | JPMarichal |
