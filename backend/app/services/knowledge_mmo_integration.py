"""
Knowledge Transformation → MMO AI Bridge Integration

Integrates Звено 3 (Knowledge Transformation) with Звено 5 (MMO RPG Gamedesign).

Critical missing integration identified in First Chain Analysis:
- Knowledge transformation NOT integrated with MMO
- AIKnowledgeToMMO transformer absent
- Graph-based knowledge → Game content pipeline missing

This module bridges the gap.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


# ============================================================================
# Knowledge Graph Structures (from Звено 3)
# ============================================================================

@dataclass
class KnowledgeConcept:
    """Concept in knowledge graph"""
    id: str
    name: str
    description: str
    type: str  # "theory", "method", "algorithm", "application"
    difficulty: int = 1  # 1-5
    prerequisites: List[str] = field(default_factory=list)  # Concept IDs
    related_concepts: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class KnowledgeRelation:
    """Relation between concepts"""
    from_concept: str
    to_concept: str
    relation_type: str  # "prerequisite", "related", "extends", "applies_to"
    strength: float = 1.0  # 0-1


@dataclass
class KnowledgeGraph:
    """Knowledge graph structure"""
    concepts: Dict[str, KnowledgeConcept]
    relations: List[KnowledgeRelation]
    domain: str
    metadata: Dict = field(default_factory=dict)


# ============================================================================
# MMO Content Structures (from Звено 5)
# ============================================================================

@dataclass
class MMOQuestNode:
    """Quest in MMO game"""
    id: str
    title: str
    description: str
    objectives: List[str]
    rewards: List[str]
    difficulty: int  # 1-5
    required_quests: List[str] = field(default_factory=list)  # Quest IDs
    location: str = "Unknown"
    npc: str = "Quest Giver"


@dataclass
class MMOCharacter:
    """Character/NPC in MMO"""
    id: str
    name: str
    role: str  # "teacher", "merchant", "boss", "ally"
    dialogue: List[str] = field(default_factory=list)
    knowledge_domain: str = ""


@dataclass
class MMOLocation:
    """Location in MMO world"""
    id: str
    name: str
    description: str
    type: str  # "city", "dungeon", "training", "library"
    quests: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)


@dataclass
class MMOWorld:
    """Complete MMO world"""
    quests: Dict[str, MMOQuestNode]
    characters: Dict[str, MMOCharacter]
    locations: Dict[str, MMOLocation]
    metadata: Dict = field(default_factory=dict)


# ============================================================================
# Integration Service
# ============================================================================

class KnowledgeMMOIntegration:
    """
    Integrates Knowledge Transformation with MMO AI Bridge

    Pipeline:
    1. Knowledge Graph → MMO Content
       - Concepts → Quests
       - Relations → Quest chains
       - Difficulty → Level progression

    2. Expert Knowledge → NPCs
       - Domain experts → Teacher NPCs
       - Specialized knowledge → Boss NPCs

    3. Learning Path → Quest Chains
       - Prerequisite graph → Quest dependencies
       - Skill tree → Character progression
    """

    def __init__(self):
        # Mapping strategies
        self.concept_to_location_type = {
            "theory": "library",
            "method": "training",
            "algorithm": "dungeon",
            "application": "city"
        }

        self.difficulty_to_level_range = {
            1: (1, 10),
            2: (11, 25),
            3: (26, 50),
            4: (51, 75),
            5: (76, 100)
        }

    def transform_knowledge_graph_to_mmo(
        self,
        knowledge_graph: KnowledgeGraph
    ) -> MMOWorld:
        """
        Transform complete knowledge graph into MMO world

        Main integration method combining all transformations
        """
        mmo_world = MMOWorld(
            quests={},
            characters={},
            locations={},
            metadata={
                "source_domain": knowledge_graph.domain,
                "num_concepts": len(knowledge_graph.concepts),
                "transformation_date": datetime.utcnow().isoformat()
            }
        )

        # Step 1: Create locations from concept types
        locations = self._create_locations_from_concepts(knowledge_graph)
        mmo_world.locations = {loc.id: loc for loc in locations}

        # Step 2: Create NPCs from knowledge domains
        npcs = self._create_npcs_from_domain(knowledge_graph)
        mmo_world.characters = {npc.id: npc for npc in npcs}

        # Step 3: Transform concepts to quests
        quests = self._transform_concepts_to_quests(
            knowledge_graph,
            mmo_world.locations,
            mmo_world.characters
        )
        mmo_world.quests = {quest.id: quest for quest in quests}

        # Step 4: Build quest chains from relations
        self._build_quest_chains_from_relations(
            knowledge_graph,
            mmo_world.quests
        )

        # Step 5: Assign quests to locations and NPCs
        self._assign_quests_to_world(mmo_world)

        return mmo_world

    def create_learning_path(
        self,
        knowledge_graph: KnowledgeGraph,
        target_concept: str,
        player_level: int = 1
    ) -> List[MMOQuestNode]:
        """
        Create optimal learning path (quest chain) to master a concept

        Uses TSP-style optimization to find best order of quests
        """
        # Find all prerequisite concepts
        prerequisites = self._find_prerequisites_recursive(
            knowledge_graph,
            target_concept
        )

        # Create quest for each concept
        quest_chain = []
        for concept_id in prerequisites + [target_concept]:
            if concept_id in knowledge_graph.concepts:
                concept = knowledge_graph.concepts[concept_id]
                quest = self._concept_to_quest(concept)
                quest_chain.append(quest)

        # Order by difficulty and prerequisites
        quest_chain.sort(key=lambda q: q.difficulty)

        # Set dependencies
        for i in range(1, len(quest_chain)):
            quest_chain[i].required_quests.append(quest_chain[i-1].id)

        return quest_chain

    def integrate_expert_knowledge(
        self,
        expert_name: str,
        expertise_areas: List[str],
        knowledge_graph: KnowledgeGraph
    ) -> MMOCharacter:
        """
        Create NPC from expert knowledge

        Expert → Teacher NPC who gives quests related to their expertise
        """
        npc_id = f"npc_{expert_name.lower().replace(' ', '_')}"

        # Find concepts in expert's areas
        expert_concepts = [
            concept for concept in knowledge_graph.concepts.values()
            if any(area.lower() in concept.name.lower() or
                   area.lower() in concept.description.lower()
                   for area in expertise_areas)
        ]

        # Generate dialogue
        dialogue = [
            f"Greetings, I am {expert_name}, master of {', '.join(expertise_areas[:2])}.",
            f"I have spent years studying {expertise_areas[0]}.",
            "I can teach you the ways of this domain, if you're willing to learn.",
            "Complete my quests to gain mastery."
        ]

        npc = MMOCharacter(
            id=npc_id,
            name=expert_name,
            role="teacher",
            dialogue=dialogue,
            knowledge_domain=", ".join(expertise_areas)
        )

        return npc

    # Private helper methods

    def _create_locations_from_concepts(
        self,
        knowledge_graph: KnowledgeGraph
    ) -> List[MMOLocation]:
        """Create locations based on concept types"""
        locations = []

        # Group concepts by type
        concept_groups: Dict[str, List[KnowledgeConcept]] = {}
        for concept in knowledge_graph.concepts.values():
            if concept.type not in concept_groups:
                concept_groups[concept.type] = []
            concept_groups[concept.type].append(concept)

        # Create location for each group
        for concept_type, concepts in concept_groups.items():
            location_type = self.concept_to_location_type.get(concept_type, "city")
            location_id = f"location_{concept_type}_{knowledge_graph.domain}"

            location = MMOLocation(
                id=location_id,
                name=f"{concept_type.title()} {location_type.title()} of {knowledge_graph.domain}",
                description=f"A place dedicated to learning {concept_type} in {knowledge_graph.domain}.",
                type=location_type,
                quests=[],  # Will be filled later
                npcs=[]     # Will be filled later
            )
            locations.append(location)

        return locations

    def _create_npcs_from_domain(
        self,
        knowledge_graph: KnowledgeGraph
    ) -> List[MMOCharacter]:
        """Create NPCs for knowledge domain"""
        npcs = []

        # Create master NPC for domain
        master_npc = MMOCharacter(
            id=f"npc_master_{knowledge_graph.domain}",
            name=f"Master of {knowledge_graph.domain.title()}",
            role="teacher",
            dialogue=[
                f"Welcome to the study of {knowledge_graph.domain}!",
                "I can guide you on your learning journey.",
                "Complete quests to gain knowledge and experience."
            ],
            knowledge_domain=knowledge_graph.domain
        )
        npcs.append(master_npc)

        # Create specialist NPCs for difficult concepts
        high_level_concepts = [
            c for c in knowledge_graph.concepts.values()
            if c.difficulty >= 4
        ]

        for concept in high_level_concepts[:5]:  # Limit to 5 specialists
            specialist_npc = MMOCharacter(
                id=f"npc_specialist_{concept.id}",
                name=f"{concept.name} Specialist",
                role="teacher",
                dialogue=[
                    f"I am an expert in {concept.name}.",
                    f"This is advanced material. Are you ready?",
                    f"Study {concept.name} carefully."
                ],
                knowledge_domain=concept.name
            )
            npcs.append(specialist_npc)

        # Create boss NPC for final challenge
        boss_npc = MMOCharacter(
            id=f"npc_boss_{knowledge_graph.domain}",
            name=f"Guardian of {knowledge_graph.domain.title()}",
            role="boss",
            dialogue=[
                f"You dare challenge the Guardian of {knowledge_graph.domain}?",
                "Prove your mastery!",
                "Only the truly knowledgeable may pass."
            ],
            knowledge_domain=knowledge_graph.domain
        )
        npcs.append(boss_npc)

        return npcs

    def _transform_concepts_to_quests(
        self,
        knowledge_graph: KnowledgeGraph,
        locations: Dict[str, MMOLocation],
        characters: Dict[str, MMOCharacter]
    ) -> List[MMOQuestNode]:
        """Transform concepts into quests"""
        quests = []

        for concept in knowledge_graph.concepts.values():
            quest = self._concept_to_quest(concept)

            # Assign location based on concept type
            location_type = self.concept_to_location_type.get(concept.type, "city")
            matching_location = next(
                (loc for loc in locations.values() if loc.type == location_type),
                None
            )
            if matching_location:
                quest.location = matching_location.name

            # Assign NPC based on difficulty
            if concept.difficulty >= 4:
                # High difficulty → specialist
                matching_npc = next(
                    (npc for npc in characters.values()
                     if npc.role == "teacher" and concept.name in npc.knowledge_domain),
                    None
                )
                if matching_npc:
                    quest.npc = matching_npc.name
            else:
                # Normal difficulty → master
                master_npc = next(
                    (npc for npc in characters.values()
                     if "master" in npc.id.lower()),
                    None
                )
                if master_npc:
                    quest.npc = master_npc.name

            quests.append(quest)

        return quests

    def _concept_to_quest(self, concept: KnowledgeConcept) -> MMOQuestNode:
        """Convert single concept to quest"""
        quest_id = f"quest_{concept.id}"

        # Generate objectives based on concept type
        objectives = []
        if concept.type == "theory":
            objectives = [
                f"Study the theory of {concept.name}",
                f"Understand key principles",
                f"Pass comprehension test"
            ]
        elif concept.type == "method":
            objectives = [
                f"Learn the {concept.name} method",
                f"Practice the technique",
                f"Demonstrate proficiency"
            ]
        elif concept.type == "algorithm":
            objectives = [
                f"Understand {concept.name} algorithm",
                f"Implement the algorithm",
                f"Optimize performance",
                f"Pass efficiency test"
            ]
        else:  # application
            objectives = [
                f"Learn about {concept.name}",
                f"Apply knowledge to real problem",
                f"Complete practical challenge"
            ]

        # Generate rewards based on difficulty
        level_range = self.difficulty_to_level_range[concept.difficulty]
        xp_reward = level_range[0] * 10

        rewards = [
            f"{xp_reward} Experience Points",
            f"{concept.name} Mastery Badge",
            f"Unlock: {concept.name} Ability"
        ]

        quest = MMOQuestNode(
            id=quest_id,
            title=f"Master {concept.name}",
            description=concept.description,
            objectives=objectives,
            rewards=rewards,
            difficulty=concept.difficulty,
            required_quests=[],  # Will be filled by prerequisites
            location="Unknown",
            npc="Quest Giver"
        )

        return quest

    def _build_quest_chains_from_relations(
        self,
        knowledge_graph: KnowledgeGraph,
        quests: Dict[str, MMOQuestNode]
    ) -> None:
        """Build quest dependencies from knowledge relations"""
        for relation in knowledge_graph.relations:
            if relation.relation_type == "prerequisite":
                # from_concept is prerequisite for to_concept
                from_quest_id = f"quest_{relation.from_concept}"
                to_quest_id = f"quest_{relation.to_concept}"

                if to_quest_id in quests and from_quest_id in quests:
                    if from_quest_id not in quests[to_quest_id].required_quests:
                        quests[to_quest_id].required_quests.append(from_quest_id)

    def _assign_quests_to_world(self, mmo_world: MMOWorld) -> None:
        """Assign quests to locations and NPCs"""
        for quest in mmo_world.quests.values():
            # Find matching location
            for location in mmo_world.locations.values():
                if quest.location.lower() in location.name.lower():
                    if quest.id not in location.quests:
                        location.quests.append(quest.id)
                    break

            # Find matching NPC
            for npc in mmo_world.characters.values():
                if quest.npc.lower() in npc.name.lower():
                    # NPC can give this quest (could track this in NPC structure)
                    break

    def _find_prerequisites_recursive(
        self,
        knowledge_graph: KnowledgeGraph,
        concept_id: str,
        visited: Optional[Set[str]] = None
    ) -> List[str]:
        """Find all prerequisites for a concept recursively"""
        if visited is None:
            visited = set()

        if concept_id not in knowledge_graph.concepts or concept_id in visited:
            return []

        visited.add(concept_id)
        concept = knowledge_graph.concepts[concept_id]
        prerequisites = []

        # Add direct prerequisites
        for prereq_id in concept.prerequisites:
            if prereq_id not in visited:
                # Recursively find prerequisites of prerequisites
                sub_prereqs = self._find_prerequisites_recursive(
                    knowledge_graph,
                    prereq_id,
                    visited
                )
                prerequisites.extend(sub_prereqs)
                prerequisites.append(prereq_id)

        return prerequisites


# ============================================================================
# Usage Example
# ============================================================================

def example_integration():
    """
    Example: Transform Machine Learning knowledge graph into MMO world
    """
    # Create sample knowledge graph
    ml_graph = KnowledgeGraph(
        concepts={
            "linear_regression": KnowledgeConcept(
                id="linear_regression",
                name="Linear Regression",
                description="Basic supervised learning for regression",
                type="method",
                difficulty=1,
                prerequisites=[],
                related_concepts=["logistic_regression"]
            ),
            "neural_network": KnowledgeConcept(
                id="neural_network",
                name="Neural Network",
                description="Multi-layer perceptron for complex patterns",
                type="algorithm",
                difficulty=3,
                prerequisites=["linear_regression"],
                related_concepts=["deep_learning"]
            ),
            "deep_learning": KnowledgeConcept(
                id="deep_learning",
                name="Deep Learning",
                description="Multi-layer neural networks",
                type="theory",
                difficulty=4,
                prerequisites=["neural_network"],
                related_concepts=[]
            )
        },
        relations=[
            KnowledgeRelation("linear_regression", "neural_network", "prerequisite"),
            KnowledgeRelation("neural_network", "deep_learning", "prerequisite")
        ],
        domain="machine_learning"
    )

    # Transform to MMO world
    integration = KnowledgeMMOIntegration()
    mmo_world = integration.transform_knowledge_graph_to_mmo(ml_graph)

    # Print results
    print("=" * 60)
    print("KNOWLEDGE → MMO INTEGRATION RESULT")
    print("=" * 60)

    print(f"\n🏰 LOCATIONS: {len(mmo_world.locations)}")
    for location in mmo_world.locations.values():
        print(f"  📍 {location.name} ({location.type})")
        print(f"     Quests: {len(location.quests)}")

    print(f"\n👥 CHARACTERS: {len(mmo_world.characters)}")
    for npc in mmo_world.characters.values():
        print(f"  👤 {npc.name} ({npc.role})")

    print(f"\n📜 QUESTS: {len(mmo_world.quests)}")
    for quest in mmo_world.quests.values():
        print(f"  🎯 {quest.title}")
        print(f"     Difficulty: {quest.difficulty}/5")
        print(f"     Prerequisites: {len(quest.required_quests)}")

    # Create learning path
    print(f"\n📚 LEARNING PATH to Deep Learning:")
    path = integration.create_learning_path(ml_graph, "deep_learning")
    for i, quest in enumerate(path, 1):
        print(f"  {i}. {quest.title} (Difficulty: {quest.difficulty})")


if __name__ == "__main__":
    example_integration()
