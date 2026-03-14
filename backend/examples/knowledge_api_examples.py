"""
Knowledge Transformation API Usage Examples

Demonstrates how to use the Knowledge API endpoints:
- Transform research papers into quest chains
- Convert ML concepts into character classes
- Generate complete MMO worlds from knowledge graphs
- Create optimized learning paths
"""

import asyncio
import httpx
from typing import Dict, List


# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000/api/knowledge"


# ============================================================================
# Example 1: Transform Research Paper to Quest Chain
# ============================================================================

async def example_paper_to_quests():
    """
    Example: Transform "Attention Is All You Need" paper into game quests

    This demonstrates how AI research papers can become educational quests
    that teach concepts through gameplay.
    """
    print("\n" + "="*80)
    print("Example 1: Research Paper → Quest Chain")
    print("="*80)

    # Simplified version of the Transformer paper
    payload = {
        "title": "Attention Is All You Need",
        "content": """
        The dominant sequence transduction models are based on complex recurrent
        or convolutional neural networks. We propose the Transformer, a model
        architecture based entirely on attention mechanisms, dispensing with
        recurrence and convolutions entirely.
        """,
        "type": "paper",
        "difficulty": "advanced",
        "keywords": ["transformer", "attention", "sequence-to-sequence", "neural networks"],
        "sections": {
            "introduction": "Recurrent models face challenges with sequential computation",
            "method": "Self-attention mechanism allows parallel computation",
            "experiments": "Transformer achieves state-of-the-art on machine translation",
            "conclusion": "Attention mechanisms can replace recurrence entirely"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/paper-to-quests",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully transformed paper into {len(result['quests'])} quests!")

            print("\n📜 Quest Chain:")
            for i, quest in enumerate(result['quests'], 1):
                print(f"\nQuest {i}: {quest['title']}")
                print(f"  Difficulty: {quest['difficulty']}")
                print(f"  Description: {quest['description']}")
                print(f"  Objectives:")
                for obj in quest['objectives']:
                    print(f"    - {obj}")
                print(f"  Rewards:")
                for reward in quest['rewards']:
                    print(f"    - {reward}")

            if result['character_classes']:
                print(f"\n🎭 Character Classes Created: {len(result['character_classes'])}")
                for char_class in result['character_classes']:
                    print(f"\n  {char_class['name']}")
                    print(f"    {char_class['description']}")

            if result['abilities']:
                print(f"\n⚡ Abilities Created: {len(result['abilities'])}")
                for ability in result['abilities'][:3]:  # Show first 3
                    print(f"  - {ability['name']}: {ability['description']}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 2: Transform ML Concept to Character Class
# ============================================================================

async def example_concept_to_class():
    """
    Example: Transform "Neural Network" concept into playable character class

    This shows how AI/ML concepts can become game mechanics.
    """
    print("\n" + "="*80)
    print("Example 2: ML Concept → Character Class")
    print("="*80)

    payload = {
        "name": "Neural Network",
        "description": """
        A computational model inspired by biological neural networks.
        Consists of interconnected nodes (neurons) that process information
        through weighted connections. Learns patterns through backpropagation.
        """
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/concept-to-class",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully created character class!")

            for char_class in result['character_classes']:
                print(f"\n🎭 Class: {char_class['name']}")
                print(f"Description: {char_class['description']}")
                print(f"Playstyle: {char_class['playstyle']}")

                print(f"\n💪 Strengths:")
                for strength in char_class['strengths']:
                    print(f"  - {strength}")

                print(f"\n⚠️  Weaknesses:")
                for weakness in char_class['weaknesses']:
                    print(f"  - {weakness}")

            if result['abilities']:
                print(f"\n⚡ Class Abilities ({len(result['abilities'])}):")
                for ability in result['abilities']:
                    print(f"\n  {ability['name']}")
                    print(f"    Effect: {ability['effect']}")
                    print(f"    Description: {ability['description']}")
                    if ability['cooldown'] > 0:
                        print(f"    Cooldown: {ability['cooldown']}s")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 3: Transform Knowledge Graph to MMO World
# ============================================================================

async def example_knowledge_graph_to_mmo():
    """
    Example: Transform Machine Learning curriculum into complete MMO world

    This creates an entire game world from an educational knowledge graph.
    """
    print("\n" + "="*80)
    print("Example 3: Knowledge Graph → Complete MMO World")
    print("="*80)

    # Define ML curriculum as knowledge graph
    payload = {
        "domain": "Machine Learning",
        "concepts": [
            {
                "id": "linear_regression",
                "name": "Linear Regression",
                "description": "Predict continuous values using linear relationships",
                "type": "theory",
                "difficulty": 1,
                "prerequisites": [],
                "related_concepts": ["statistics", "optimization"]
            },
            {
                "id": "logistic_regression",
                "name": "Logistic Regression",
                "description": "Binary classification using logistic function",
                "type": "theory",
                "difficulty": 2,
                "prerequisites": ["linear_regression"],
                "related_concepts": ["classification"]
            },
            {
                "id": "neural_network",
                "name": "Neural Network",
                "description": "Multi-layer network of neurons",
                "type": "method",
                "difficulty": 3,
                "prerequisites": ["logistic_regression"],
                "related_concepts": ["backpropagation", "deep_learning"]
            },
            {
                "id": "cnn",
                "name": "Convolutional Neural Network",
                "description": "Neural network for image processing",
                "type": "method",
                "difficulty": 4,
                "prerequisites": ["neural_network"],
                "related_concepts": ["computer_vision"]
            },
            {
                "id": "transformer",
                "name": "Transformer",
                "description": "Attention-based architecture",
                "type": "algorithm",
                "difficulty": 5,
                "prerequisites": ["neural_network"],
                "related_concepts": ["attention", "nlp"]
            },
            {
                "id": "reinforcement_learning",
                "name": "Reinforcement Learning",
                "description": "Learn through rewards and penalties",
                "type": "theory",
                "difficulty": 4,
                "prerequisites": ["neural_network"],
                "related_concepts": ["game_theory", "optimization"]
            },
        ],
        "relations": [
            {
                "from_concept": "linear_regression",
                "to_concept": "logistic_regression",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
            {
                "from_concept": "logistic_regression",
                "to_concept": "neural_network",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
            {
                "from_concept": "neural_network",
                "to_concept": "cnn",
                "relation_type": "prerequisite",
                "strength": 0.8
            },
            {
                "from_concept": "neural_network",
                "to_concept": "transformer",
                "relation_type": "prerequisite",
                "strength": 0.9
            },
            {
                "from_concept": "neural_network",
                "to_concept": "reinforcement_learning",
                "relation_type": "prerequisite",
                "strength": 0.7
            },
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/graph-to-mmo",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully created MMO world!")

            print(f"\n🌍 World: {payload['domain']}")
            print(f"Total Quests: {len(result['quests'])}")
            print(f"Total NPCs: {len(result['characters'])}")
            print(f"Total Locations: {len(result['locations'])}")

            # Show locations
            print(f"\n📍 Locations:")
            for location in result['locations']:
                print(f"\n  {location['name']} ({location['type']})")
                print(f"    {location['description']}")
                print(f"    Quests: {len(location['quests'])}")
                print(f"    NPCs: {len(location['npcs'])}")

            # Show NPCs
            print(f"\n👤 NPCs:")
            for npc in result['characters'][:3]:  # Show first 3
                print(f"\n  {npc['name']} - {npc['role']}")
                print(f"    Domain: {npc['knowledge_domain']}")
                if npc['dialogue']:
                    print(f"    Says: \"{npc['dialogue'][0]}\"")

            # Show some quests
            print(f"\n📜 Sample Quests:")
            for quest_id, quest in list(result['quests'].items())[:3]:
                print(f"\n  {quest['title']} (Level {quest['difficulty']})")
                print(f"    {quest['description']}")
                print(f"    Location: {quest.get('location', 'Unknown')}")
                if quest['prerequisites']:
                    print(f"    Prerequisites: {', '.join(quest['prerequisites'])}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 4: Create Learning Path
# ============================================================================

async def example_create_learning_path():
    """
    Example: Create optimal learning path to master "Deep Learning"

    This finds the best quest order to reach a target concept.
    """
    print("\n" + "="*80)
    print("Example 4: Generate Optimal Learning Path")
    print("="*80)

    # Same ML knowledge graph from Example 3
    graph_payload = {
        "domain": "Machine Learning",
        "concepts": [
            {
                "id": "linear_regression",
                "name": "Linear Regression",
                "description": "Predict continuous values",
                "type": "theory",
                "difficulty": 1,
                "prerequisites": [],
                "related_concepts": []
            },
            {
                "id": "logistic_regression",
                "name": "Logistic Regression",
                "description": "Binary classification",
                "type": "theory",
                "difficulty": 2,
                "prerequisites": ["linear_regression"],
                "related_concepts": []
            },
            {
                "id": "neural_network",
                "name": "Neural Network",
                "description": "Multi-layer network",
                "type": "method",
                "difficulty": 3,
                "prerequisites": ["logistic_regression"],
                "related_concepts": []
            },
            {
                "id": "deep_learning",
                "name": "Deep Learning",
                "description": "Deep neural networks",
                "type": "method",
                "difficulty": 5,
                "prerequisites": ["neural_network"],
                "related_concepts": []
            },
        ],
        "relations": [
            {
                "from_concept": "linear_regression",
                "to_concept": "logistic_regression",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
            {
                "from_concept": "logistic_regression",
                "to_concept": "neural_network",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
            {
                "from_concept": "neural_network",
                "to_concept": "deep_learning",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
        ]
    }

    # Request learning path to Deep Learning
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/learning-path",
            json={
                "graph": graph_payload,
                "target_concept": "deep_learning",
                "player_level": 1
            },
            timeout=30.0
        )

        if response.status_code == 200:
            quests = response.json()
            print(f"\n✅ Created optimal learning path!")
            print(f"\n🎯 Target: Deep Learning")
            print(f"Total Quests: {len(quests)}")

            print(f"\n📚 Learning Path:")
            for i, quest in enumerate(quests, 1):
                print(f"\n  Step {i}: {quest['title']}")
                print(f"    Difficulty: {quest['difficulty']}")
                print(f"    Description: {quest['description']}")
                print(f"    Objectives:")
                for obj in quest['objectives'][:2]:  # Show first 2
                    print(f"      - {obj}")

            print(f"\n💡 Follow this quest order to master Deep Learning!")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 5: List Available Transformations
# ============================================================================

async def example_list_transformations():
    """List all available knowledge transformations"""
    print("\n" + "="*80)
    print("Example 5: Available Knowledge Transformations")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/transformations",
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()
            print("\n✅ Available Transformations:")

            for transformation in data['transformations']:
                print(f"\n🔄 {transformation['name']}")
                print(f"   ID: {transformation['id']}")
                print(f"   Input: {transformation['input']}")
                print(f"   Output: {transformation['output']}")
                print(f"   Use Case: {transformation['use_case']}")
                print(f"\n   Example:")
                print(f"     Input:  {transformation['example']['input']}")
                print(f"     Output: {transformation['example']['output']}")

            # Show transformation patterns
            print("\n\n📐 Transformation Patterns:")

            print("\n  Paper Sections:")
            for section, quest_type in data['patterns']['paper_sections'].items():
                print(f"    {section:15} → {quest_type}")

            print("\n  Concept Types:")
            for concept_type, location in data['patterns']['concept_types'].items():
                print(f"    {concept_type:15} → {location}")

            print("\n  ML Concepts:")
            for concept, char_class in data['patterns']['ml_concepts'].items():
                print(f"    {concept:25} → {char_class}")

        else:
            print(f"❌ Error: {response.status_code}")


# ============================================================================
# Example 6: Complete Workflow - Curriculum to Playable Game
# ============================================================================

async def example_complete_workflow():
    """
    Example: Complete workflow from curriculum to playable game

    This demonstrates the full pipeline:
    1. Define curriculum as knowledge graph
    2. Transform to MMO world
    3. Create learning path for specific goal
    4. Transform individual papers for deep dives
    """
    print("\n" + "="*80)
    print("Example 6: Complete Workflow - Curriculum → Playable Game")
    print("="*80)

    print("\n📚 Step 1: Define AI/ML Curriculum")
    print("Creating knowledge graph with 6 concepts...")

    # Step 1: Define curriculum
    curriculum = {
        "domain": "AI/ML Fundamentals",
        "concepts": [
            {
                "id": "basics",
                "name": "ML Basics",
                "description": "Introduction to machine learning",
                "type": "theory",
                "difficulty": 1,
                "prerequisites": [],
                "related_concepts": []
            },
            {
                "id": "supervised",
                "name": "Supervised Learning",
                "description": "Learning from labeled data",
                "type": "method",
                "difficulty": 2,
                "prerequisites": ["basics"],
                "related_concepts": []
            },
            {
                "id": "unsupervised",
                "name": "Unsupervised Learning",
                "description": "Learning from unlabeled data",
                "type": "method",
                "difficulty": 2,
                "prerequisites": ["basics"],
                "related_concepts": []
            },
        ],
        "relations": [
            {
                "from_concept": "basics",
                "to_concept": "supervised",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
            {
                "from_concept": "basics",
                "to_concept": "unsupervised",
                "relation_type": "prerequisite",
                "strength": 1.0
            },
        ]
    }

    print("\n🌍 Step 2: Generate MMO World")
    print("Transforming curriculum into game world...")

    async with httpx.AsyncClient() as client:
        # Generate world
        world_response = await client.post(
            f"{API_BASE_URL}/graph-to-mmo",
            json=curriculum,
            timeout=30.0
        )

        if world_response.status_code == 200:
            world = world_response.json()
            print(f"✅ Created world with {len(world['quests'])} quests, "
                  f"{len(world['locations'])} locations, {len(world['characters'])} NPCs")

            # Step 3: Create learning path
            print("\n🎯 Step 3: Create Learning Path")
            print("Generating optimal quest order...")

            path_response = await client.post(
                f"{API_BASE_URL}/learning-path",
                json={
                    "graph": curriculum,
                    "target_concept": "supervised",
                    "player_level": 1
                },
                timeout=30.0
            )

            if path_response.status_code == 200:
                path = path_response.json()
                print(f"✅ Created learning path with {len(path)} quests")

                print("\n📜 Your Quest Journey:")
                for i, quest in enumerate(path, 1):
                    print(f"  {i}. {quest['title']}")

            # Step 4: Deep dive into specific paper
            print("\n📄 Step 4: Add Deep Dive Content")
            print("Transforming research paper for advanced players...")

            paper_response = await client.post(
                f"{API_BASE_URL}/paper-to-quests",
                json={
                    "title": "Introduction to Neural Networks",
                    "content": "Basic concepts of neural networks",
                    "type": "paper",
                    "difficulty": "intermediate",
                    "keywords": ["neural", "network"],
                    "sections": {
                        "introduction": "What is a neural network?",
                        "method": "How do neurons connect?",
                        "experiments": "Training a simple network",
                        "conclusion": "Applications of neural networks"
                    }
                },
                timeout=30.0
            )

            if paper_response.status_code == 200:
                paper_quests = paper_response.json()
                print(f"✅ Created {len(paper_quests['quests'])} additional quests from paper")

            print("\n" + "="*80)
            print("✅ Complete Workflow Finished!")
            print("="*80)
            print("\n🎮 You now have a playable educational MMO with:")
            print(f"  • {len(world['quests'])} quests teaching ML concepts")
            print(f"  • {len(world['locations'])} themed locations")
            print(f"  • {len(world['characters'])} NPC teachers")
            print(f"  • Optimized learning paths for different goals")
            print(f"  • Deep-dive content from research papers")
            print("\nReady to start learning through gameplay! 🚀")

        else:
            print(f"❌ Error: {world_response.status_code}")


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("Knowledge Transformation API Examples")
    print("="*80)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")

    try:
        # Run all examples
        await example_list_transformations()
        await example_paper_to_quests()
        await example_concept_to_class()
        await example_knowledge_graph_to_mmo()
        await example_create_learning_path()
        await example_complete_workflow()

        print("\n" + "="*80)
        print("✅ All examples completed!")
        print("="*80)

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
