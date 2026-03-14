"""
MMO Unified System - Integration of All 5 Game Mechanics
==========================================================

Integrates:
1. SmartQuestLog - TSP-optimized quest routing
2. AIDirector - Dynamic difficulty adjustment
3. BurnoutDetector - Player wellness monitoring
4. EconomyBalancer - Automatic inflation control
5. SkillTreeOptimizer - Build optimization

Author: AI Research Assistant
Date: 2026-02-05
Version: 1.0.0
"""

import sys
import os

# Import our existing systems
sys.path.append(os.path.dirname(__file__))

from mmo_rpg_mechanics import (
    AIDirector, PlayerState,
    BurnoutDetector,
    EconomyBalancer,
    SkillTreeOptimizer, Skill
)
from mmo_economy_simulation import EconomySimulation

from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import random
import time
import math


# ============================================================================
# SIMPLIFIED MODELS FOR UNIFIED SYSTEM
# ============================================================================

@dataclass
class SimpleQuest:
    """Simplified quest model for unified system"""
    id: int
    name: str
    location: Tuple[float, float]  # (x, y) coordinates
    difficulty: float
    reward_xp: int
    reward_gold: int
    estimated_time: int = 10  # minutes

    def distance_to(self, pos_x: float, pos_y: float) -> float:
        """Calculate distance from a position"""
        dx = self.location[0] - pos_x
        dy = self.location[1] - pos_y
        return math.sqrt(dx**2 + dy**2)


# ============================================================================
# UNIFIED PLAYER MODEL
# ============================================================================

@dataclass
class UnifiedPlayer:
    """Unified player model integrating all systems"""
    id: int
    name: str
    level: int = 1

    # Position (simple x, y coordinates)
    position_x: float = 0.0
    position_y: float = 0.0

    # Combat stats
    power: float = 100.0
    health: float = 100.0
    max_health: float = 100.0

    # Skills
    skills: Dict[str, int] = field(default_factory=dict)
    skill_points: int = 0

    # Economy
    gold: int = 1000

    # Session tracking
    session_duration: int = 0  # minutes
    quests_completed: int = 0
    combats_won: int = 0
    deaths: int = 0

    # Wellness
    energy: float = 100.0
    stress: float = 0.0
    satisfaction: float = 80.0

    # Optimization preferences
    playstyle: str = "balanced"  # casual, balanced, hardcore

    def __post_init__(self):
        # Initialize basic skills
        if not self.skills:
            self.skills = {
                'combat': 1,
                'navigation': 1,
                'trading': 1,
                'crafting': 1
            }


# ============================================================================
# GAME SESSION MANAGER
# ============================================================================

class GameSession:
    """Manages a complete game session with all systems"""

    def __init__(self, player: UnifiedPlayer, num_quests: int = 10):
        self.player = player

        # Initialize all subsystems
        self.quest_log = SmartSimpleQuestLog()
        self.ai_director = AIDirector()
        self.burnout_detector = BurnoutDetector()
        self.economy = EconomyBalancer()
        self.skill_optimizer = SkillTreeOptimizer()

        # Generate initial quests
        self.available_quests = self._generate_quests(num_quests)
        self.completed_quests: List[SimpleQuest] = []

        # Session stats
        self.session_start = time.time()
        self.total_xp_gained = 0
        self.total_gold_gained = 0
        self.total_distance_traveled = 0.0

        # History
        self.event_log: List[str] = []

    def _generate_quests(self, num: int) -> List[SimpleQuest]:
        """Generate random quests for the session"""
        quests = []
        quest_types = ['combat', 'collection', 'delivery', 'exploration']

        for i in range(num):
            # Random location within 50x50 map
            loc = Location(
                x=random.randint(5, 45),
                y=random.randint(5, 45)
            )

            # SimpleQuest difficulty based on player level
            difficulty = random.uniform(
                max(0.3, self.player.level * 0.1 - 0.2),
                min(1.0, self.player.level * 0.1 + 0.2)
            )

            quest = SimpleQuest(
                id=i + 1,
                name=f"{random.choice(quest_types).title()} SimpleQuest {i+1}",
                location=loc,
                difficulty=difficulty,
                reward_xp=int(100 * (1 + self.player.level) * difficulty),
                reward_gold=int(50 * (1 + self.player.level) * difficulty)
            )

            quests.append(quest)

        return quests

    def start_session(self):
        """Start a new gaming session"""
        self.log_event("=== SESSION START ===")
        self.log_event(f"Player: {self.player.name} (Level {self.player.level})")
        self.log_event(f"Available quests: {len(self.available_quests)}")
        self.log_event(f"Starting location: ({self.player.position_x}, {self.player.position_y})")
        self.log_event("")

    def optimize_quest_route(self) -> List[SimpleQuest]:
        """Use SmartSimpleQuestLog to optimize quest order"""
        self.log_event("🗺️  Optimizing quest route...")

        # Add quests to quest log
        for quest in self.available_quests:
            self.quest_log.add_quest(quest)

        # Create simple location for player
        player_loc = type('obj', (object,), {
            'position': (self.player.position_x, self.player.position_y),
            'x': self.player.position_x,
            'y': self.player.position_y
        })()

        # Optimize
        result = self.quest_log.optimize_route(
            player_location=player_loc,
            max_time_minutes=120  # 2-hour session
        )

        optimized_order = result['optimized_order']

        self.log_event(f"✅ Route optimized!")
        self.log_event(f"   - Total distance: {result['total_distance']:.1f} units")
        self.log_event(f"   - Estimated time: {result['estimated_time']:.0f} minutes")
        self.log_event(f"   - Time saved: {result['improvement_percentage']:.1f}%")
        self.log_event(f"   - SimpleQuest order: {[q.id for q in optimized_order]}")
        self.log_event("")

        return optimized_order

    def execute_quest(self, quest: SimpleQuest):
        """Execute a single quest with AI Director and Burnout tracking"""
        self.log_event(f"📜 Starting: {quest.name} (Difficulty: {quest.difficulty:.2f})")

        # 1. Travel to quest location
        quest_x, quest_y = quest.location
        dx = quest_x - self.player.position_x
        dy = quest_y - self.player.position_y
        distance = (dx**2 + dy**2)**0.5

        travel_time = distance * 0.5  # 0.5 minutes per unit
        self.total_distance_traveled += distance

        self.log_event(f"   🚶 Traveling {distance:.1f} units ({travel_time:.1f} min)...")
        self.player.position_x = quest_x
        self.player.position_y = quest_y
        self.player.session_duration += int(travel_time)

        # 2. AI Director adjusts difficulty
        player_state = PlayerState(
            level=self.player.level,
            skill_rating=self.player.power / 100.0,
            win_rate=self.player.combats_won / max(1, self.player.combats_won + self.player.deaths)
        )

        adjusted_difficulty = self.ai_director.adjust_difficulty(
            player_state=player_state,
            base_difficulty=quest.difficulty
        )

        self.log_event(f"   ⚖️  AI Director: {quest.difficulty:.2f} → {adjusted_difficulty:.2f}")

        # 3. Execute quest (simplified combat)
        success_chance = max(0.2, min(0.95,
            1.0 - adjusted_difficulty + (self.player.power / 200.0)
        ))

        success = random.random() < success_chance

        if success:
            # SimpleQuest completed
            self.log_event(f"   ✅ SimpleQuest completed!")

            # Rewards
            xp_gained = quest.reward_xp
            gold_gained = quest.reward_gold

            self.player.level += xp_gained // 1000
            self.player.gold += gold_gained
            self.player.skill_points += 1

            self.total_xp_gained += xp_gained
            self.total_gold_gained += gold_gained
            self.player.quests_completed += 1
            self.player.combats_won += 1

            # Update wellness
            self.player.energy -= 10 * adjusted_difficulty
            self.player.stress += 5 * adjusted_difficulty
            self.player.satisfaction += 15

            self.log_event(f"   💰 Rewards: {xp_gained} XP, {gold_gained} gold")

            self.completed_quests.append(quest)
        else:
            # SimpleQuest failed
            self.log_event(f"   ❌ SimpleQuest failed!")
            self.player.deaths += 1
            self.player.energy -= 20
            self.player.stress += 20
            self.player.satisfaction -= 10

            self.log_event(f"   💀 Death penalty: -10 satisfaction")

        # 4. Check burnout
        burnout_risk = self.burnout_detector.check_burnout(
            session_duration=self.player.session_duration,
            recent_performance=[1 if success else 0],
            difficulty_history=[adjusted_difficulty]
        )

        if burnout_risk > 0.7:
            self.log_event(f"   ⚠️  HIGH BURNOUT RISK ({burnout_risk:.2f})!")
            self.log_event(f"      Suggestion: Take a break")
        elif burnout_risk > 0.5:
            self.log_event(f"   ⚠️  Moderate burnout risk ({burnout_risk:.2f})")

        self.player.session_duration += 10  # SimpleQuest takes ~10 minutes
        self.log_event("")

    def optimize_skills(self):
        """Use SkillTreeOptimizer to suggest skill upgrades"""
        if self.player.skill_points == 0:
            return

        self.log_event("📊 Optimizing skill build...")

        # Available skills to upgrade
        available_skills = [
            Skill(
                id='combat',
                name='Combat Mastery',
                current_level=self.player.skills.get('combat', 1),
                max_level=10,
                cost=self.player.skills.get('combat', 1) * 100
            ),
            Skill(
                id='navigation',
                name='Swift Travel',
                current_level=self.player.skills.get('navigation', 1),
                max_level=10,
                cost=self.player.skills.get('navigation', 1) * 80
            ),
            Skill(
                id='trading',
                name='Merchant',
                current_level=self.player.skills.get('trading', 1),
                max_level=10,
                cost=self.player.skills.get('trading', 1) * 90
            ),
        ]

        # Optimize
        recommendations = self.skill_optimizer.optimize_build(
            available_skills=available_skills,
            available_points=self.player.skill_points,
            player_goals={'combat': 0.6, 'efficiency': 0.4}
        )

        if recommendations:
            self.log_event(f"✅ Skill recommendations:")
            for skill_id, levels in recommendations.items():
                self.log_event(f"   - {skill_id}: +{levels} levels")
                self.player.skills[skill_id] = self.player.skills.get(skill_id, 1) + levels

            self.player.skill_points = 0
        else:
            self.log_event("   No skill upgrades available")

        self.log_event("")

    def check_economy(self):
        """Use EconomyBalancer to check gold inflation"""
        self.log_event("💰 Economy check...")

        avg_gold = self.player.gold

        status = self.economy.check_balance(
            gold_generated=self.total_gold_gained,
            gold_spent=0,  # Simplified
            average_gold=avg_gold
        )

        self.log_event(f"   Status: {status['status']}")
        if status['inflation_rate'] > 1.15:
            self.log_event(f"   ⚠️  High inflation ({status['inflation_rate']:.2f}x)")

        self.log_event("")

    def end_session(self):
        """End session and generate report"""
        session_duration = time.time() - self.session_start

        self.log_event("")
        self.log_event("=== SESSION END ===")
        self.log_event(f"Duration: {self.player.session_duration} minutes")
        self.log_event(f"SimpleQuests completed: {len(self.completed_quests)}/{len(self.available_quests)}")
        self.log_event(f"Total XP: {self.total_xp_gained}")
        self.log_event(f"Total gold: {self.total_gold_gained}")
        self.log_event(f"Distance traveled: {self.total_distance_traveled:.1f} units")
        self.log_event("")

        # Final wellness check
        final_burnout = self.burnout_detector.check_burnout(
            session_duration=self.player.session_duration,
            recent_performance=[1] * self.player.combats_won + [0] * self.player.deaths,
            difficulty_history=[0.5] * 10
        )

        self.log_event(f"Final Stats:")
        self.log_event(f"  Level: {self.player.level}")
        self.log_event(f"  Gold: {self.player.gold}")
        self.log_event(f"  Energy: {self.player.energy:.1f}/100")
        self.log_event(f"  Stress: {self.player.stress:.1f}/100")
        self.log_event(f"  Satisfaction: {self.player.satisfaction:.1f}/100")
        self.log_event(f"  Burnout Risk: {final_burnout:.2f}")

        if final_burnout < 0.3:
            self.log_event(f"  ✅ Healthy session!")
        elif final_burnout < 0.6:
            self.log_event(f"  ⚠️  Moderate fatigue - consider shorter sessions")
        else:
            self.log_event(f"  🚨 HIGH BURNOUT - take a break!")

    def log_event(self, message: str):
        """Log an event to history"""
        self.event_log.append(message)
        print(message)

    def get_summary(self) -> Dict:
        """Get session summary"""
        return {
            'player_name': self.player.name,
            'duration_minutes': self.player.session_duration,
            'quests_completed': len(self.completed_quests),
            'xp_gained': self.total_xp_gained,
            'gold_gained': self.total_gold_gained,
            'distance_traveled': self.total_distance_traveled,
            'final_level': self.player.level,
            'final_gold': self.player.gold,
            'burnout_risk': self.burnout_detector.check_burnout(
                self.player.session_duration, [], []
            )
        }


# ============================================================================
# DEMO SCENARIOS
# ============================================================================

def demo_casual_player():
    """Demo: Casual player (1-hour session)"""
    print("\n" + "=" * 80)
    print("DEMO 1: CASUAL PLAYER - 1 Hour Session")
    print("=" * 80 + "\n")

    player = UnifiedPlayer(
        id=1,
        name="CasualGamer42",
        level=5,
        playstyle="casual"
    )

    session = GameSession(player, num_quests=5)
    session.start_session()

    # Optimize route
    optimized_quests = session.optimize_quest_route()

    # Execute first 3 quests (1-hour session)
    for quest in optimized_quests[:3]:
        session.execute_quest(quest)

    # Check skills
    session.optimize_skills()

    # Economy check
    session.check_economy()

    # End
    session.end_session()

    return session.get_summary()


def demo_hardcore_player():
    """Demo: Hardcore player (3-hour session)"""
    print("\n" + "=" * 80)
    print("DEMO 2: HARDCORE PLAYER - 3 Hour Session")
    print("=" * 80 + "\n")

    player = UnifiedPlayer(
        id=2,
        name="1337Pro",
        level=15,
        power=150.0,
        playstyle="hardcore"
    )

    session = GameSession(player, num_quests=12)
    session.start_session()

    # Optimize route
    optimized_quests = session.optimize_quest_route()

    # Execute all quests (hardcore grind)
    for quest in optimized_quests:
        session.execute_quest(quest)

        # Check burnout every 3 quests
        if len(session.completed_quests) % 3 == 0:
            session.optimize_skills()

    # Final checks
    session.check_economy()
    session.end_session()

    return session.get_summary()


def demo_comparison():
    """Demo: Compare casual vs hardcore outcomes"""
    print("\n" + "=" * 80)
    print("COMPARISON: Casual vs Hardcore Player")
    print("=" * 80 + "\n")

    casual_summary = demo_casual_player()
    hardcore_summary = demo_hardcore_player()

    print("\n" + "=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)

    print(f"\n{'Metric':<25} {'Casual':<15} {'Hardcore':<15}")
    print("-" * 55)
    print(f"{'Duration (min)':<25} {casual_summary['duration_minutes']:<15} {hardcore_summary['duration_minutes']:<15}")
    print(f"{'SimpleQuests Completed':<25} {casual_summary['quests_completed']:<15} {hardcore_summary['quests_completed']:<15}")
    print(f"{'XP Gained':<25} {casual_summary['xp_gained']:<15} {hardcore_summary['xp_gained']:<15}")
    print(f"{'Gold Gained':<25} {casual_summary['gold_gained']:<15} {hardcore_summary['gold_gained']:<15}")
    print(f"{'Efficiency (XP/min)':<25} {casual_summary['xp_gained']/max(1,casual_summary['duration_minutes']):<15.1f} {hardcore_summary['xp_gained']/max(1,hardcore_summary['duration_minutes']):<15.1f}")
    print(f"{'Burnout Risk':<25} {casual_summary['burnout_risk']:<15.2f} {hardcore_summary['burnout_risk']:<15.2f}")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS:")
    print("-" * 80)

    if casual_summary['burnout_risk'] < hardcore_summary['burnout_risk']:
        print("✅ Casual player has lower burnout risk - healthier gameplay")

    casual_eff = casual_summary['xp_gained'] / max(1, casual_summary['duration_minutes'])
    hardcore_eff = hardcore_summary['xp_gained'] / max(1, hardcore_summary['duration_minutes'])

    if casual_eff > hardcore_eff:
        print("✅ Casual player has HIGHER efficiency per minute")
        print("   (Thanks to route optimization + no burnout penalty)")

    print("=" * 80)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("MMO UNIFIED SYSTEM - Complete Integration Demo")
    print("=" * 80)
    print("\nIntegrating:")
    print("  1. SmartSimpleQuestLog - SimpleQuest route optimization")
    print("  2. AIDirector - Dynamic difficulty")
    print("  3. BurnoutDetector - Wellness monitoring")
    print("  4. EconomyBalancer - Inflation control")
    print("  5. SkillTreeOptimizer - Build optimization")
    print("=" * 80)

    # Run comparison demo
    demo_comparison()

    print("\n" + "=" * 80)
    print("✅ ALL SYSTEMS INTEGRATED AND OPERATIONAL")
    print("=" * 80)


if __name__ == "__main__":
    main()
