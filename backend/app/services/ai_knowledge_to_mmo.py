"""
AI Knowledge to MMO Transformer

Transforms AI/ML research papers and concepts into MMO game content:
- Research papers → Quest chains
- ML concepts → Character classes & abilities
- Algorithms → Game mechanics
- Training processes → Leveling systems

Critical missing component identified in audit.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re


# ============================================================================
# Data Structures
# ============================================================================

class ContentType(Enum):
    """Type of MMO content"""
    QUEST = "quest"
    QUEST_CHAIN = "quest_chain"
    CHARACTER_CLASS = "character_class"
    ABILITY = "ability"
    ITEM = "item"
    NPC = "npc"
    LOCATION = "location"
    MECHANIC = "mechanic"


class Difficulty(Enum):
    """Content difficulty"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class AIKnowledge:
    """AI/ML knowledge to transform"""
    title: str
    content: str
    type: str  # "paper", "concept", "algorithm", "technique"
    difficulty: Difficulty
    keywords: List[str] = field(default_factory=list)
    sections: Dict[str, str] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class MMOQuest:
    """MMO Quest"""
    id: str
    title: str
    description: str
    objectives: List[str]
    rewards: List[str]
    difficulty: Difficulty
    prerequisites: List[str] = field(default_factory=list)
    npc_giver: Optional[str] = None
    location: Optional[str] = None
    lore: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class MMOCharacterClass:
    """MMO Character Class"""
    id: str
    name: str
    description: str
    abilities: List[str]
    strengths: List[str]
    weaknesses: List[str]
    playstyle: str
    lore: str = ""


@dataclass
class MMOAbility:
    """MMO Ability/Skill"""
    id: str
    name: str
    description: str
    effect: str
    cooldown: float = 0.0
    cost: float = 0.0
    visual_effect: str = ""


@dataclass
class TransformationResult:
    """Result of knowledge transformation"""
    quests: List[MMOQuest] = field(default_factory=list)
    character_classes: List[MMOCharacterClass] = field(default_factory=list)
    abilities: List[MMOAbility] = field(default_factory=list)
    npcs: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# AI Knowledge to MMO Transformer
# ============================================================================

class AIKnowledgeToMMO:
    """
    Transform AI knowledge into MMO content

    Patterns:
    1. Research Paper → Quest Chain
       - Introduction → Tutorial quest
       - Method → Learning quest
       - Experiment → Challenge quest
       - Results → Boss fight

    2. ML Concept → Character Class
       - Neural Network → "Connectionist" class
       - Decision Tree → "Branching Sage" class
       - Reinforcement Learning → "Explorer" class

    3. Algorithm → Game Mechanic
       - Backpropagation → "Error Reflection" ability
       - Gradient Descent → "Optimization" passive
       - Attention → "Focus" mechanic
    """

    def __init__(self):
        # Concept to fantasy mapping
        self.concept_mappings = {
            # ML Concepts
            "neural network": {"class": "Connectionist", "element": "Network"},
            "deep learning": {"class": "Deep Sage", "element": "Depth"},
            "transformer": {"class": "Attention Master", "element": "Focus"},
            "cnn": {"class": "Vision Monk", "element": "Sight"},
            "rnn": {"class": "Memory Keeper", "element": "Time"},
            "reinforcement learning": {"class": "Explorer", "element": "Reward"},
            "supervised learning": {"class": "Guided Scholar", "element": "Labels"},
            "unsupervised learning": {"class": "Pattern Seeker", "element": "Chaos"},

            # Algorithms
            "gradient descent": {"ability": "Optimization Step", "type": "movement"},
            "backpropagation": {"ability": "Error Reflection", "type": "damage"},
            "attention": {"ability": "Focus Beam", "type": "buff"},
            "dropout": {"ability": "Randomize", "type": "defensive"},
            "batch normalization": {"ability": "Stabilize", "type": "buff"},

            # Problems
            "overfitting": {"boss": "Memorization Demon", "weakness": "regularization"},
            "vanishing gradient": {"boss": "Fading Echo", "weakness": "residual"},
            "exploding gradient": {"boss": "Chaos Storm", "weakness": "clipping"},
        }

    def transform_paper(self, paper: AIKnowledge) -> TransformationResult:
        """
        Transform research paper into quest chain

        Example: "Attention Is All You Need" →
        - Quest 1: "The RNN Problem" (Introduction)
        - Quest 2: "Learn Self-Attention" (Method)
        - Quest 3: "Defeat Sequential Boss" (Experiment)
        - Quest 4: "Master Transformer" (Results)
        """
        result = TransformationResult()

        # Extract paper sections
        sections = self._extract_paper_sections(paper)

        # Create quest chain
        quest_chain = []

        # Introduction → Tutorial Quest
        if "introduction" in sections:
            intro_quest = self._create_intro_quest(
                paper.title,
                sections["introduction"],
                paper.difficulty
            )
            quest_chain.append(intro_quest)

        # Method → Learning Quest
        if "method" in sections or "methodology" in sections:
            method_text = sections.get("method", sections.get("methodology", ""))
            method_quest = self._create_method_quest(
                paper.title,
                method_text,
                paper.difficulty
            )
            if intro_quest.id in quest_chain:
                method_quest.prerequisites.append(intro_quest.id)
            quest_chain.append(method_quest)

        # Experiments → Challenge Quest
        if "experiments" in sections or "results" in sections:
            exp_text = sections.get("experiments", sections.get("results", ""))
            challenge_quest = self._create_challenge_quest(
                paper.title,
                exp_text,
                paper.difficulty
            )
            if method_quest.id in quest_chain:
                challenge_quest.prerequisites.append(method_quest.id)
            quest_chain.append(challenge_quest)

        # Conclusion → Master Quest (Boss)
        if "conclusion" in sections:
            boss_quest = self._create_boss_quest(
                paper.title,
                sections["conclusion"],
                paper.difficulty
            )
            if challenge_quest.id in quest_chain:
                boss_quest.prerequisites.append(challenge_quest.id)
            quest_chain.append(boss_quest)

        result.quests = quest_chain

        # Extract concepts and create character classes
        concepts = self._extract_concepts(paper)
        for concept in concepts:
            if concept in self.concept_mappings:
                char_class = self._create_character_class(concept)
                if char_class:
                    result.character_classes.append(char_class)

        # Extract algorithms and create abilities
        abilities = self._create_abilities_from_paper(paper)
        result.abilities = abilities

        result.metadata = {
            "source_paper": paper.title,
            "num_quests": len(quest_chain),
            "difficulty": paper.difficulty.value
        }

        return result

    def transform_concept(self, concept_name: str, description: str) -> TransformationResult:
        """
        Transform ML concept into character class

        Example: "Neural Network" → "Connectionist" class with abilities:
        - Forward Pass (attack)
        - Backpropagation (reflect damage)
        - Layer Stack (defense buff)
        """
        result = TransformationResult()

        concept_lower = concept_name.lower()

        # Create character class
        if concept_lower in self.concept_mappings:
            char_class = self._create_character_class(concept_lower)
            if char_class:
                result.character_classes.append(char_class)

                # Create abilities for this class
                abilities = self._create_abilities_for_concept(concept_lower, description)
                result.abilities = abilities

        result.metadata = {
            "source_concept": concept_name
        }

        return result

    def create_quest_from_problem(
        self,
        problem: str,
        solution: str,
        difficulty: Difficulty
    ) -> MMOQuest:
        """
        Create quest from AI problem-solution pair

        Example: Problem="Vanishing Gradient", Solution="Residual Connections"
        → Quest: "Defeat the Fading Echo" with "Residual Bridge" item reward
        """
        quest_id = f"quest_{problem.lower().replace(' ', '_')}"

        # Map problem to boss
        problem_lower = problem.lower()
        boss_name = self.concept_mappings.get(problem_lower, {}).get(
            "boss",
            f"{problem} Demon"
        )

        quest = MMOQuest(
            id=quest_id,
            title=f"Defeat the {boss_name}",
            description=f"The {boss_name} threatens the realm. Use {solution} to overcome it.",
            objectives=[
                f"Learn about {problem}",
                f"Acquire {solution} technique",
                f"Defeat the {boss_name}",
                "Report victory"
            ],
            rewards=[
                f"{solution} Mastery Badge",
                f"100 Experience Points",
                f"{solution} Ability Unlock"
            ],
            difficulty=difficulty,
            npc_giver="Professor AI",
            location="Training Grounds",
            lore=f"Long ago, {problem} was a common threat to neural architectures. "
                 f"Researchers discovered that {solution} could counter this menace."
        )

        return quest

    # Private helper methods

    def _extract_paper_sections(self, paper: AIKnowledge) -> Dict[str, str]:
        """Extract sections from paper"""
        if paper.sections:
            return paper.sections

        # Simple section extraction from content
        sections = {}
        content = paper.content.lower()

        # Common section markers
        section_markers = {
            "introduction": ["introduction", "intro", "background"],
            "method": ["method", "methodology", "approach", "architecture"],
            "experiments": ["experiments", "experimental", "evaluation"],
            "results": ["results", "findings", "performance"],
            "conclusion": ["conclusion", "conclusions", "discussion"]
        }

        for section_name, markers in section_markers.items():
            for marker in markers:
                if marker in content:
                    # Extract text around marker (simplified)
                    sections[section_name] = f"Content about {marker}"
                    break

        return sections

    def _extract_concepts(self, paper: AIKnowledge) -> List[str]:
        """Extract AI/ML concepts from paper"""
        concepts = []
        content = paper.content.lower()

        # Check for known concepts
        for concept in self.concept_mappings.keys():
            if concept in content or concept in paper.title.lower():
                concepts.append(concept)

        # Also use keywords
        concepts.extend([k.lower() for k in paper.keywords])

        return list(set(concepts))

    def _create_intro_quest(
        self,
        paper_title: str,
        intro_text: str,
        difficulty: Difficulty
    ) -> MMOQuest:
        """Create introduction quest"""
        quest_id = f"quest_intro_{paper_title.lower().replace(' ', '_')[:20]}"

        return MMOQuest(
            id=quest_id,
            title=f"Introduction: {paper_title}",
            description=f"Learn about the problem that {paper_title} addresses.",
            objectives=[
                "Read the introduction",
                "Understand the motivation",
                "Identify the problem",
                "Speak with Professor AI"
            ],
            rewards=[
                "10 Experience Points",
                "Knowledge Badge: Introduction",
                "Access to Method Quest"
            ],
            difficulty=difficulty,
            npc_giver="Professor AI",
            location="Library of Knowledge",
            lore=f"Every great discovery starts with understanding the problem. "
                 f"Study {paper_title} to begin your journey."
        )

    def _create_method_quest(
        self,
        paper_title: str,
        method_text: str,
        difficulty: Difficulty
    ) -> MMOQuest:
        """Create method/learning quest"""
        quest_id = f"quest_method_{paper_title.lower().replace(' ', '_')[:20]}"

        return MMOQuest(
            id=quest_id,
            title=f"Method: {paper_title}",
            description=f"Master the technique proposed in {paper_title}.",
            objectives=[
                "Study the methodology",
                "Practice the technique",
                "Demonstrate understanding",
                "Earn certification"
            ],
            rewards=[
                "30 Experience Points",
                "Technique Mastery Badge",
                "New Ability Unlock",
                "Access to Challenge Quest"
            ],
            difficulty=difficulty,
            npc_giver="Master Researcher",
            location="Training Grounds",
            lore=f"Theory meets practice. Apply the methods from {paper_title} "
                 f"to become a true master."
        )

    def _create_challenge_quest(
        self,
        paper_title: str,
        exp_text: str,
        difficulty: Difficulty
    ) -> MMOQuest:
        """Create challenge/experiment quest"""
        quest_id = f"quest_challenge_{paper_title.lower().replace(' ', '_')[:20]}"

        return MMOQuest(
            id=quest_id,
            title=f"Challenge: Validate {paper_title}",
            description=f"Test your knowledge by replicating the experiments from {paper_title}.",
            objectives=[
                "Set up experiment",
                "Run benchmark tests",
                "Achieve baseline performance",
                "Reach paper's results",
                "Document findings"
            ],
            rewards=[
                "50 Experience Points",
                "Experiment Badge",
                "Rare Item: Research Notes",
                "Access to Boss Quest"
            ],
            difficulty=difficulty,
            npc_giver="Senior Scientist",
            location="Experimental Lab",
            lore=f"Science demands validation. Prove the claims of {paper_title} "
                 f"through rigorous experimentation."
        )

    def _create_boss_quest(
        self,
        paper_title: str,
        conclusion_text: str,
        difficulty: Difficulty
    ) -> MMOQuest:
        """Create final boss quest"""
        quest_id = f"quest_boss_{paper_title.lower().replace(' ', '_')[:20]}"

        # Extract key term for boss name
        key_term = paper_title.split()[0] if paper_title else "Final"

        return MMOQuest(
            id=quest_id,
            title=f"Master Quest: Defeat the {key_term} Boss",
            description=f"Face the ultimate challenge and prove you've mastered {paper_title}.",
            objectives=[
                "Prepare for boss battle",
                "Enter the Boss Arena",
                f"Defeat the {key_term} Guardian",
                "Claim mastery"
            ],
            rewards=[
                "100 Experience Points",
                f"{paper_title} Master Badge",
                f"Legendary Item: {key_term} Crown",
                f"Character Class Unlock: {key_term} Sage"
            ],
            difficulty=difficulty,
            npc_giver="Grand Master AI",
            location="Summit of Knowledge",
            lore=f"Only by defeating the {key_term} Guardian can you prove "
                 f"complete mastery of {paper_title}. Are you ready?"
        )

    def _create_character_class(self, concept: str) -> Optional[MMOCharacterClass]:
        """Create character class from concept"""
        if concept not in self.concept_mappings:
            return None

        mapping = self.concept_mappings[concept]
        class_name = mapping.get("class", concept.title())
        element = mapping.get("element", "Unknown")

        class_id = f"class_{concept.replace(' ', '_')}"

        return MMOCharacterClass(
            id=class_id,
            name=class_name,
            description=f"A master of {concept}, wielding the power of {element}.",
            abilities=[
                f"{element} Strike",
                f"{element} Shield",
                f"{element} Mastery",
                f"Ultimate: {element} Storm"
            ],
            strengths=[f"High {element} affinity", "Versatile skills"],
            weaknesses=["Requires understanding", "Complex combos"],
            playstyle=f"Strategic {element} manipulation",
            lore=f"The {class_name} class was born from deep study of {concept}. "
                 f"Practitioners harness {element} to overcome challenges."
        )

    def _create_abilities_for_concept(
        self,
        concept: str,
        description: str
    ) -> List[MMOAbility]:
        """Create abilities for a concept"""
        abilities = []

        if concept not in self.concept_mappings:
            return abilities

        mapping = self.concept_mappings[concept]
        element = mapping.get("element", "Energy")

        # Basic attack
        abilities.append(MMOAbility(
            id=f"ability_{concept}_strike",
            name=f"{element} Strike",
            description=f"Channel {element} into a powerful attack",
            effect=f"Deal {element} damage to target",
            cooldown=2.0,
            cost=10.0,
            visual_effect=f"Glowing {element.lower()} burst"
        ))

        # Defense
        abilities.append(MMOAbility(
            id=f"ability_{concept}_shield",
            name=f"{element} Shield",
            description=f"Create a protective barrier of {element}",
            effect=f"Block incoming damage using {element}",
            cooldown=10.0,
            cost=20.0,
            visual_effect=f"Shimmering {element.lower()} barrier"
        ))

        # Passive
        abilities.append(MMOAbility(
            id=f"ability_{concept}_mastery",
            name=f"{element} Mastery",
            description=f"Passive: Enhanced {element} control",
            effect=f"+20% {element} effectiveness",
            cooldown=0.0,
            cost=0.0,
            visual_effect=f"Permanent {element.lower()} aura"
        ))

        # Ultimate
        abilities.append(MMOAbility(
            id=f"ability_{concept}_ultimate",
            name=f"Ultimate: {element} Storm",
            description=f"Unleash devastating {element} power",
            effect=f"Massive AoE {element} damage + special effect",
            cooldown=60.0,
            cost=100.0,
            visual_effect=f"Explosive {element.lower()} storm animation"
        ))

        return abilities

    def _create_abilities_from_paper(self, paper: AIKnowledge) -> List[MMOAbility]:
        """Create abilities from paper content"""
        abilities = []

        # Extract algorithm names
        content = paper.content.lower()

        for concept, mapping in self.concept_mappings.items():
            if "ability" in mapping and concept in content:
                ability_name = mapping["ability"]
                ability_type = mapping.get("type", "attack")

                ability = MMOAbility(
                    id=f"ability_{concept.replace(' ', '_')}",
                    name=ability_name,
                    description=f"Use {concept} technique",
                    effect=f"Apply {concept} effect",
                    cooldown=5.0 if ability_type == "attack" else 15.0,
                    cost=15.0,
                    visual_effect=f"{concept} animation"
                )
                abilities.append(ability)

        return abilities


# ============================================================================
# Usage Example
# ============================================================================

def example_transform_attention_paper():
    """
    Example: Transform "Attention Is All You Need" paper into MMO content
    """
    paper = AIKnowledge(
        title="Attention Is All You Need",
        content="""
        Introduction: Sequential models like RNNs have limitations.
        Method: We propose the Transformer architecture using self-attention.
        Experiments: Our model achieves state-of-the-art on translation tasks.
        Conclusion: Attention mechanisms are sufficient for sequence modeling.
        """,
        type="paper",
        difficulty=Difficulty.ADVANCED,
        keywords=["transformer", "attention", "self-attention", "neural network"],
        sections={
            "introduction": "RNN limitations...",
            "method": "Transformer architecture with self-attention...",
            "experiments": "BLEU scores on WMT...",
            "conclusion": "Attention is all you need..."
        }
    )

    transformer = AIKnowledgeToMMO()
    result = transformer.transform_paper(paper)

    print("=" * 60)
    print("TRANSFORMATION RESULT: Attention Is All You Need → MMO")
    print("=" * 60)

    print(f"\n📜 QUESTS CREATED: {len(result.quests)}")
    for quest in result.quests:
        print(f"\n  🎯 {quest.title}")
        print(f"     Difficulty: {quest.difficulty.value}")
        print(f"     Objectives: {len(quest.objectives)}")
        print(f"     Rewards: {', '.join(quest.rewards[:2])}")

    print(f"\n⚔️  CHARACTER CLASSES: {len(result.character_classes)}")
    for char_class in result.character_classes:
        print(f"\n  👤 {char_class.name}")
        print(f"     Abilities: {', '.join(char_class.abilities)}")

    print(f"\n✨ ABILITIES: {len(result.abilities)}")
    for ability in result.abilities[:3]:
        print(f"\n  🔮 {ability.name}")
        print(f"     {ability.description}")


if __name__ == "__main__":
    example_transform_attention_paper()
