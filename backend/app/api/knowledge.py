"""
Knowledge Transformation API Endpoints

Provides endpoints for transforming AI knowledge into MMO content
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.ai_knowledge_to_mmo import (
    AIKnowledgeToMMO,
    AIKnowledge,
    Difficulty
)
from app.services.knowledge_mmo_integration import (
    KnowledgeMMOIntegration,
    KnowledgeGraph,
    KnowledgeConcept,
    KnowledgeRelation
)


router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# ============================================================================
# Request/Response Models
# ============================================================================

class AIKnowledgeRequest(BaseModel):
    """Request for AI knowledge"""
    title: str
    content: str
    type: str  # "paper", "concept", "algorithm", "technique"
    difficulty: str = "intermediate"  # beginner, intermediate, advanced, expert
    keywords: List[str] = []
    sections: Dict[str, str] = {}


class ConceptRequest(BaseModel):
    """Request for ML concept"""
    name: str
    description: str


class QuestResponse(BaseModel):
    """Response for quest"""
    id: str
    title: str
    description: str
    objectives: List[str]
    rewards: List[str]
    difficulty: str
    prerequisites: List[str] = []
    npc_giver: Optional[str] = None
    location: Optional[str] = None


class CharacterClassResponse(BaseModel):
    """Response for character class"""
    id: str
    name: str
    description: str
    abilities: List[str]
    strengths: List[str]
    weaknesses: List[str]
    playstyle: str


class AbilityResponse(BaseModel):
    """Response for ability"""
    id: str
    name: str
    description: str
    effect: str
    cooldown: float = 0.0
    cost: float = 0.0


class TransformationResponse(BaseModel):
    """Response for transformation"""
    quests: List[QuestResponse]
    character_classes: List[CharacterClassResponse]
    abilities: List[AbilityResponse]
    metadata: Dict = {}


class KnowledgeConceptRequest(BaseModel):
    """Request for knowledge concept"""
    id: str
    name: str
    description: str
    type: str
    difficulty: int = 1
    prerequisites: List[str] = []
    related_concepts: List[str] = []


class KnowledgeRelationRequest(BaseModel):
    """Request for knowledge relation"""
    from_concept: str
    to_concept: str
    relation_type: str
    strength: float = 1.0


class KnowledgeGraphRequest(BaseModel):
    """Request for knowledge graph"""
    concepts: List[KnowledgeConceptRequest]
    relations: List[KnowledgeRelationRequest]
    domain: str


class MMOWorldResponse(BaseModel):
    """Response for MMO world"""
    quests: Dict[str, QuestResponse]
    characters: List[Dict]  # Simplified
    locations: List[Dict]  # Simplified
    metadata: Dict = {}


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/paper-to-quests")
async def transform_paper_to_quests(
    request: AIKnowledgeRequest
) -> TransformationResponse:
    """
    Transform research paper into quest chain

    Example: "Attention Is All You Need" →
    - Quest 1: "The RNN Problem" (Introduction)
    - Quest 2: "Learn Self-Attention" (Method)
    - Quest 3: "Defeat Sequential Boss" (Experiment)
    - Quest 4: "Master Transformer" (Results)

    Returns quests, character classes, and abilities generated from the paper.
    """
    try:
        # Parse difficulty
        difficulty_map = {
            "beginner": Difficulty.BEGINNER,
            "intermediate": Difficulty.INTERMEDIATE,
            "advanced": Difficulty.ADVANCED,
            "expert": Difficulty.EXPERT
        }
        difficulty = difficulty_map.get(request.difficulty, Difficulty.INTERMEDIATE)

        # Create AI knowledge
        knowledge = AIKnowledge(
            title=request.title,
            content=request.content,
            type=request.type,
            difficulty=difficulty,
            keywords=request.keywords,
            sections=request.sections
        )

        # Transform
        transformer = AIKnowledgeToMMO()
        result = transformer.transform_paper(knowledge)

        # Convert to response
        quests = [
            QuestResponse(
                id=q.id,
                title=q.title,
                description=q.description,
                objectives=q.objectives,
                rewards=q.rewards,
                difficulty=q.difficulty.value,
                prerequisites=q.prerequisites,
                npc_giver=q.npc_giver,
                location=q.location
            )
            for q in result.quests
        ]

        character_classes = [
            CharacterClassResponse(
                id=c.id,
                name=c.name,
                description=c.description,
                abilities=c.abilities,
                strengths=c.strengths,
                weaknesses=c.weaknesses,
                playstyle=c.playstyle
            )
            for c in result.character_classes
        ]

        abilities = [
            AbilityResponse(
                id=a.id,
                name=a.name,
                description=a.description,
                effect=a.effect,
                cooldown=a.cooldown,
                cost=a.cost
            )
            for a in result.abilities
        ]

        return TransformationResponse(
            quests=quests,
            character_classes=character_classes,
            abilities=abilities,
            metadata=result.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Paper transformation failed: {str(e)}"
        )


@router.post("/concept-to-class")
async def transform_concept_to_class(
    request: ConceptRequest
) -> TransformationResponse:
    """
    Transform ML concept into character class

    Example: "Neural Network" → "Connectionist" class
    - Abilities: Forward Pass, Backpropagation, Layer Stack
    - Element: Network
    - Playstyle: Strategic network manipulation

    Returns character class with abilities.
    """
    try:
        transformer = AIKnowledgeToMMO()
        result = transformer.transform_concept(request.name, request.description)

        # Convert to response
        character_classes = [
            CharacterClassResponse(
                id=c.id,
                name=c.name,
                description=c.description,
                abilities=c.abilities,
                strengths=c.strengths,
                weaknesses=c.weaknesses,
                playstyle=c.playstyle
            )
            for c in result.character_classes
        ]

        abilities = [
            AbilityResponse(
                id=a.id,
                name=a.name,
                description=a.description,
                effect=a.effect,
                cooldown=a.cooldown,
                cost=a.cost
            )
            for a in result.abilities
        ]

        return TransformationResponse(
            quests=[],
            character_classes=character_classes,
            abilities=abilities,
            metadata=result.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Concept transformation failed: {str(e)}"
        )


@router.post("/graph-to-mmo")
async def transform_knowledge_graph(
    request: KnowledgeGraphRequest
) -> MMOWorldResponse:
    """
    Transform knowledge graph into complete MMO world

    Converts:
    - Concepts → Quests with dependencies
    - Concept types → Locations (Theory→Library, Algorithm→Dungeon)
    - Experts → NPC teachers
    - Prerequisites → Quest dependencies

    Returns complete MMO world with quests, NPCs, and locations.
    """
    try:
        # Build knowledge graph
        concepts = {
            c.id: KnowledgeConcept(
                id=c.id,
                name=c.name,
                description=c.description,
                type=c.type,
                difficulty=c.difficulty,
                prerequisites=c.prerequisites,
                related_concepts=c.related_concepts
            )
            for c in request.concepts
        }

        relations = [
            KnowledgeRelation(
                from_concept=r.from_concept,
                to_concept=r.to_concept,
                relation_type=r.relation_type,
                strength=r.strength
            )
            for r in request.relations
        ]

        knowledge_graph = KnowledgeGraph(
            concepts=concepts,
            relations=relations,
            domain=request.domain
        )

        # Transform
        integration = KnowledgeMMOIntegration()
        mmo_world = integration.transform_knowledge_graph_to_mmo(knowledge_graph)

        # Convert to response
        quests = {
            q_id: QuestResponse(
                id=quest.id,
                title=quest.title,
                description=quest.description,
                objectives=quest.objectives,
                rewards=quest.rewards,
                difficulty=str(quest.difficulty),
                prerequisites=quest.required_quests,
                npc_giver=quest.npc,
                location=quest.location
            )
            for q_id, quest in mmo_world.quests.items()
        }

        characters = [
            {
                "id": npc.id,
                "name": npc.name,
                "role": npc.role,
                "dialogue": npc.dialogue,
                "knowledge_domain": npc.knowledge_domain
            }
            for npc in mmo_world.characters.values()
        ]

        locations = [
            {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description,
                "type": loc.type,
                "quests": loc.quests,
                "npcs": loc.npcs
            }
            for loc in mmo_world.locations.values()
        ]

        return MMOWorldResponse(
            quests=quests,
            characters=characters,
            locations=locations,
            metadata=mmo_world.metadata
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Knowledge graph transformation failed: {str(e)}"
        )


@router.post("/learning-path")
async def create_learning_path(
    graph: KnowledgeGraphRequest,
    target_concept: str,
    player_level: int = 1
) -> List[QuestResponse]:
    """
    Create optimal learning path to master a concept

    Uses TSP-style optimization to find best order of quests.
    Recursively finds all prerequisites and orders them by difficulty.

    Example: Path to "Deep Learning"
    → Linear Regression → Neural Network → Deep Learning

    Returns ordered list of quests.
    """
    try:
        # Build knowledge graph (same as graph-to-mmo)
        concepts = {
            c.id: KnowledgeConcept(
                id=c.id,
                name=c.name,
                description=c.description,
                type=c.type,
                difficulty=c.difficulty,
                prerequisites=c.prerequisites,
                related_concepts=c.related_concepts
            )
            for c in graph.concepts
        }

        relations = [
            KnowledgeRelation(
                from_concept=r.from_concept,
                to_concept=r.to_concept,
                relation_type=r.relation_type,
                strength=r.strength
            )
            for r in graph.relations
        ]

        knowledge_graph = KnowledgeGraph(
            concepts=concepts,
            relations=relations,
            domain=graph.domain
        )

        # Create learning path
        integration = KnowledgeMMOIntegration()
        quest_chain = integration.create_learning_path(
            knowledge_graph,
            target_concept,
            player_level
        )

        # Convert to response
        quests = [
            QuestResponse(
                id=q.id,
                title=q.title,
                description=q.description,
                objectives=q.objectives,
                rewards=q.rewards,
                difficulty=str(q.difficulty),
                prerequisites=q.required_quests,
                npc_giver=q.npc,
                location=q.location
            )
            for q in quest_chain
        ]

        return quests

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Learning path creation failed: {str(e)}"
        )


@router.get("/transformations")
async def list_transformations() -> Dict:
    """
    List available knowledge transformations

    Returns information about each transformation including:
    - Input/output formats
    - Use cases
    - Examples
    """
    return {
        "transformations": [
            {
                "id": "paper-to-quests",
                "name": "Research Paper → Quest Chain",
                "input": "AI/ML research paper",
                "output": "4-stage quest chain (Intro, Method, Challenge, Boss)",
                "use_case": "Transform academic papers into game content",
                "example": {
                    "input": "Attention Is All You Need (Transformer paper)",
                    "output": "4 quests teaching attention mechanism"
                }
            },
            {
                "id": "concept-to-class",
                "name": "ML Concept → Character Class",
                "input": "Machine learning concept",
                "output": "Character class with abilities",
                "use_case": "Create playable classes from AI concepts",
                "example": {
                    "input": "Neural Network concept",
                    "output": "Connectionist class with Network abilities"
                }
            },
            {
                "id": "graph-to-mmo",
                "name": "Knowledge Graph → MMO World",
                "input": "Knowledge graph with concepts and relations",
                "output": "Complete MMO world (quests, NPCs, locations)",
                "use_case": "Generate entire game world from curriculum",
                "example": {
                    "input": "Machine Learning curriculum graph",
                    "output": "ML MMO world with 10+ quests, 3 locations, 3 NPCs"
                }
            },
            {
                "id": "learning-path",
                "name": "Learning Path Generation",
                "input": "Knowledge graph + target concept",
                "output": "Optimal quest order",
                "use_case": "Guide players through prerequisites",
                "example": {
                    "input": "Target: Deep Learning",
                    "output": "Linear Regression → Neural Network → Deep Learning"
                }
            }
        ],
        "patterns": {
            "paper_sections": {
                "introduction": "Tutorial quest (learn the problem)",
                "method": "Learning quest (study the solution)",
                "experiments": "Challenge quest (apply knowledge)",
                "conclusion": "Boss quest (prove mastery)"
            },
            "concept_types": {
                "theory": "Library location",
                "method": "Training Grounds location",
                "algorithm": "Dungeon location",
                "application": "City location"
            },
            "ml_concepts": {
                "transformer": "Attention Master class",
                "neural_network": "Connectionist class",
                "reinforcement_learning": "Explorer class",
                "decision_tree": "Branching Sage class"
            }
        }
    }
