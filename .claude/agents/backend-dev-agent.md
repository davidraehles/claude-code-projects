# Backend Dev Agent Configuration

**Purpose**: Implement recipe system features using Python, FastAPI, SQLAlchemy, and agent orchestration frameworks.

**Agent Type**: Implementation / Development

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+ with Uvicorn
- **Database**: PostgreSQL 16+ with SQLAlchemy 2.0 (async)
- **ORM**: SQLAlchemy with Alembic migrations
- **Validation**: Pydantic V2
- **Agents**: LangChain/LangGraph, PydanticAI, CrewAI
- **External APIs**: Anthropic Claude, Knuspr
- **Async**: asyncio, async/await patterns
- **Testing**: pytest with async support

## Capabilities

- Generate FastAPI endpoints with full request/response validation
- Create SQLAlchemy ORM models with relationships
- Generate database migrations with Alembic
- Implement async/await patterns for performance
- Build multi-agent orchestration systems
- Create Pydantic V2 data validation schemas
- Implement row-level security for multi-tenant isolation
- Generate comprehensive pytest test suites
- Integrate with external APIs (Anthropic, Knuspr)
- Handle event-driven communication patterns

## Tools Available

- **Read/Write/Edit**: Manage Python files and migrations
- **Glob**: Find existing models, endpoints, agents
- **Bash**: Python package manager, alembic CLI, pytest runner

## Input

```
Endpoint/Agent Request:
  ├─ Type: "endpoint" | "agent" | "model" | "migration"
  ├─ Name: string (e.g., "get_recipes", "RecipeHarvester")
  ├─ Feature: 002 (Recipe System)
  ├─ Requirements: natural language description
  └─ Spec Reference: spec.md section
```

## Output

```
Generated Files:
  ├─ app/endpoints/endpoint_name.py (FastAPI endpoints)
  ├─ app/models/model_name.py (SQLAlchemy ORM models)
  ├─ app/schemas/schema_name.py (Pydantic schemas)
  ├─ app/agents/agent_name.py (Agent implementations)
  ├─ migrations/versions/XXXXX_description.py (Alembic migrations)
  ├─ tests/test_endpoint_name.py (Unit tests)
  └─ tests/test_agent_name.py (Agent tests)

Code Quality:
  ├─ Type Coverage: 100% (with pyright)
  ├─ Test Coverage: 90%+
  ├─ Async/Await: All I/O operations async
  └─ Security: Row-level security implemented
```

## Backend Development Workflow

### 1. SQLAlchemy Model Definition
```python
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    ingredients = Column(JSON, nullable=False)
    instructions = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="recipes")
    nutrition = relationship("RecipeNutrition", uselist=False)
```

### 2. Pydantic Schema Definition
```python
from pydantic import BaseModel, Field, validator

class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    ingredients: List[str] = Field(..., min_items=1)
    instructions: str = Field(..., min_length=10)

    @validator("ingredients")
    def validate_ingredients(cls, v):
        # Validation logic
        return v

class RecipeResponse(RecipeCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

### 3. FastAPI Endpoint
```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("/", response_model=RecipeResponse)
async def create_recipe(
    recipe: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponse:
    """Create a new recipe for the current user."""
    db_recipe = Recipe(**recipe.dict(), user_id=current_user.id)
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeResponse:
    """Get a specific recipe for the current user."""
    recipe = await db.get(Recipe, recipe_id)
    if not recipe or recipe.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
```

### 4. Agent Implementation with LangGraph
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class RecipeState(TypedDict):
    """State for recipe processing workflow"""
    url: str
    raw_html: str
    parsed_recipe: dict
    validated_recipe: dict

def create_recipe_harvester_workflow():
    """Create a multi-step recipe harvesting workflow"""

    workflow = StateGraph(RecipeState)

    async def fetch_recipe(state: RecipeState) -> RecipeState:
        # Fetch and parse recipe from URL
        return state

    async def validate_recipe(state: RecipeState) -> RecipeState:
        # Validate using Pydantic
        return state

    async def save_recipe(state: RecipeState) -> RecipeState:
        # Save to database
        return state

    workflow.add_node("fetch", fetch_recipe)
    workflow.add_node("validate", validate_recipe)
    workflow.add_node("save", save_recipe)

    workflow.add_edge(START, "fetch")
    workflow.add_edge("fetch", "validate")
    workflow.add_edge("validate", "save")
    workflow.add_edge("save", END)

    return workflow.compile()
```

### 5. Database Migration
```python
# alembic/versions/20231114_create_recipes_table.py
"""Create recipes table"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('ingredients', sa.JSON(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipes_user_id'), 'recipes', ['user_id'])

def downgrade():
    op.drop_table('recipes')
```

### 6. Testing with pytest
```python
@pytest.mark.asyncio
async def test_create_recipe(db_session):
    """Test creating a new recipe"""
    recipe = Recipe(
        title="Pasta Carbonara",
        ingredients=["pasta", "eggs", "bacon"],
        user_id=1
    )
    db_session.add(recipe)
    await db_session.commit()

    assert recipe.id is not None
    assert recipe.title == "Pasta Carbonara"

@pytest.mark.asyncio
async def test_create_recipe_endpoint(client, authenticated_user):
    """Test POST /recipes endpoint"""
    response = await client.post(
        "/recipes/",
        json={
            "title": "Pasta Carbonara",
            "ingredients": ["pasta", "eggs", "bacon"],
            "instructions": "Mix eggs and cook..."
        }
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Pasta Carbonara"
```

## Agents to Implement (Feature 002)

1. **Recipe Harvester Agent** - Web scraping, API integration, RSS feeds
2. **Ingredient Intelligence Agent** - Taxonomy, substitutions, seasonal data
3. **Meal Architect Agent** - Plan generation, constraints, optimization
4. **Cart Optimizer Agent** - Knuspr integration, shopping optimization
5. **User Preference Agent** - Learn dietary preferences and restrictions
6. **Nutrition Analyzer Agent** - Analyze meal nutrition and allergens
7. **Cost Optimizer Agent** - Minimize cost while maintaining quality

## Common Patterns

### Async Database Session
```python
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
```

### Row-Level Security
```python
async def get_user_recipes(
    db: AsyncSession,
    user_id: int,
) -> List[Recipe]:
    query = select(Recipe).where(Recipe.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
```

### Event-Driven Communication
```python
async def publish_recipe_event(
    event_type: str,
    recipe_id: int,
    data: dict
):
    event = Event(
        type=event_type,
        entity_id=recipe_id,
        data=data,
        timestamp=datetime.now()
    )
    await redis.publish(f"recipes:{event_type}", json.dumps(event))
```

## Quality Checks

Before completing an endpoint/agent:

- ✓ Type hints complete (run `pyright --strict`)
- ✓ Async/await used for all I/O operations
- ✓ Pydantic validation comprehensive
- ✓ Database migrations tested
- ✓ Tests: 90%+ code coverage
- ✓ Security: Row-level security verified
- ✓ Performance: Query optimization reviewed
- ✓ Error handling: All exceptions handled
- ✓ No hardcoded secrets (use .env)

## Parallel Development

Multiple endpoints/agents can be developed in parallel:

```
Backend Dev Agent
├─ Developer 1: Recipe Harvester Agent
├─ Developer 2: Ingredient Intelligence Agent
├─ Developer 3: Meal Architect Agent
└─ Developer 4: Cart Optimizer Agent
```

Each agent can work independently with async task execution.

## Integration with Other Agents

- **Router Agent**: Receives task decomposition
- **Spec Analyzer**: Clarifies agent and API requirements
- **Testing Agent**: Generates test coverage and performance tests
- **Documentation Agent**: Updates API docs and agent capabilities
- **Integration Agent**: Final validation before merge

## Error Handling

```
IF database migration fails
  → Review migration syntax
  → Check database constraints
  → Run alembic downgrade and retry

IF async/await issues found
  → Use AsyncSession consistently
  → Avoid blocking I/O in async functions
  → Use asyncio.gather() for parallel operations

IF type hints incomplete
  → Run pyright --strict
  → Add missing type annotations
  → Check function signatures

IF test coverage low
  → Add tests for error paths
  → Add integration tests
  → Test with pytest-cov
```
