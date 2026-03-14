"""
MMO Unified System - Simple Integration Demo
Demonstrates all 5 mechanics working together
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple

# ==================== DATA MODELS ====================

@dataclass
class SimpleQuest:
    id: int
    name: str
    location: Tuple[float, float]
    difficulty: float
    reward_xp: int
    reward_gold: int

@dataclass  
class Player:
    name: str
    level: int
    x: float
    y: float
    gold: int
    energy: float
    stress: float
    combats_won: int = 0
    deaths: int = 0

# ==================== MECHANICS ====================

class QuestOptimizer:
    """1. SmartQuestLog - TSP optimization"""
    
    def optimize_route(self, quests: List[SimpleQuest], player: Player) -> List[SimpleQuest]:
        """Find shortest route through quests"""
        if not quests:
            return []
        
        # Simple nearest-neighbor algorithm
        remaining = quests.copy()
        route = []
        current_x, current_y = player.x, player.y
        
        while remaining:
            # Find nearest quest
            nearest = min(remaining, key=lambda q: math.dist((current_x, current_y), q.location))
            route.append(nearest)
            current_x, current_y = nearest.location
            remaining.remove(nearest)
        
        return route

class DifficultyDirector:
    """2. AIDirector - Dynamic difficulty"""
    
    def adjust(self, base_difficulty: float, player: Player) -> float:
        """Adjust difficulty based on player performance"""
        win_rate = player.combats_won / max(1, player.combats_won + player.deaths)
        
        if win_rate > 0.8:  # Too easy
            return min(1.0, base_difficulty * 1.2)
        elif win_rate < 0.4:  # Too hard
            return max(0.3, base_difficulty * 0.8)
        else:
            return base_difficulty

class WellnessMonitor:
    """3. BurnoutDetector"""
    
    def check_burnout(self, player: Player, session_minutes: int) -> float:
        """Return burnout risk 0-1"""
        risk = 0.0
        risk += min(0.4, session_minutes / 300)  # Long sessions
        risk += min(0.3, player.stress / 100)     # High stress
        risk += min(0.3, (100 - player.energy) / 100)  # Low energy
        return risk

class EconomyManager:
    """4. EconomyBalancer"""
    
    def __init__(self):
        self.inflation = 1.0
    
    def adjust_prices(self, gold_generated: int, gold_spent: int):
        """Adjust economy based on gold flow"""
        if gold_spent == 0:
            return
        
        ratio = gold_generated / gold_spent
        
        if ratio > 1.15:  # Inflation
            self.inflation *= 1.1
        elif ratio < 0.85:  # Deflation
            self.inflation *= 0.95

class SkillAdvisor:
    """5. SkillTreeOptimizer"""
    
    def recommend(self, player: Player) -> str:
        """Recommend skill to upgrade"""
        if player.deaths > player.combats_won * 0.3:
            return "Combat (survival)"
        elif player.gold < 1000:
            return "Trading (wealth)"
        else:
            return "Navigation (efficiency)"

# ==================== GAME SESSION ====================

class GameSession:
    def __init__(self, player: Player):
        self.player = player
        self.quest_optimizer = QuestOptimizer()
        self.difficulty_director = DifficultyDirector()
        self.wellness_monitor = WellnessMonitor()
        self.economy = EconomyManager()
        self.skill_advisor = SkillAdvisor()
        
        self.session_time = 0
        self.total_xp = 0
        self.total_gold = 0
        self.events = []
    
    def generate_quests(self, count: int) -> List[SimpleQuest]:
        """Generate random quests"""
        quests = []
        for i in range(count):
            x, y = random.uniform(10, 40), random.uniform(10, 40)
            diff = random.uniform(0.4, 0.8)
            quests.append(SimpleQuest(
                id=i+1,
                name=f"Quest {i+1}",
                location=(x, y),
                difficulty=diff,
                reward_xp=int(100 * diff),
                reward_gold=int(50 * diff)
            ))
        return quests
    
    def run_session(self, quest_count: int = 5):
        """Run complete game session"""
        print(f"\n{'='*70}")
        print(f"SESSION START: {self.player.name} (Level {self.player.level})")
        print(f"{'='*70}\n")
        
        # Generate and optimize quests
        quests = self.generate_quests(quest_count)
        print(f"🗺️  Generating {quest_count} quests...")
        
        optimized = self.quest_optimizer.optimize_route(quests, self.player)
        print(f"✅ Route optimized: {[q.id for q in optimized]}\n")
        
        # Execute quests
        for quest in optimized:
            self.execute_quest(quest)
            
            # Check wellness every quest
            burnout_risk = self.wellness_monitor.check_burnout(self.player, self.session_time)
            if burnout_risk > 0.6:
                print(f"⚠️  WARNING: High burnout risk ({burnout_risk:.2f})\n")
                break
        
        # Final report
        self.print_report()
    
    def execute_quest(self, quest: SimpleQuest):
        """Execute one quest"""
        print(f"📜 {quest.name} (Difficulty: {quest.difficulty:.2f})")
        
        # Travel
        dist = math.dist((self.player.x, self.player.y), quest.location)
        travel_time = int(dist * 0.5)
        print(f"   🚶 Travel: {dist:.1f} units ({travel_time} min)")
        
        self.player.x, self.player.y = quest.location
        self.session_time += travel_time
        
        # Adjust difficulty
        adjusted_diff = self.difficulty_director.adjust(quest.difficulty, self.player)
        print(f"   ⚖️  Difficulty: {quest.difficulty:.2f} → {adjusted_diff:.2f}")
        
        # Combat
        success_chance = max(0.3, 1.0 - adjusted_diff)
        success = random.random() < success_chance
        
        if success:
            print(f"   ✅ Success! +{quest.reward_xp} XP, +{quest.reward_gold} gold")
            self.player.combats_won += 1
            self.total_xp += quest.reward_xp
            self.total_gold += quest.reward_gold
            self.player.gold += quest.reward_gold
            self.player.energy -= 10
            self.player.stress += 5
        else:
            print(f"   ❌ Failed!")
            self.player.deaths += 1
            self.player.energy -= 20
            self.player.stress += 20
        
        self.session_time += 10  # Quest time
        print()
    
    def print_report(self):
        """Print final report"""
        print(f"{'='*70}")
        print(f"SESSION COMPLETE")
        print(f"{'='*70}")
        
        burnout = self.wellness_monitor.check_burnout(self.player, self.session_time)
        
        print(f"\n📊 Stats:")
        print(f"   Duration: {self.session_time} min")
        print(f"   Total XP: {self.total_xp}")
        print(f"   Total Gold: {self.total_gold}")
        print(f"   Win Rate: {self.player.combats_won}/{self.player.combats_won + self.player.deaths}")
        print(f"   Energy: {self.player.energy:.0f}/100")
        print(f"   Stress: {self.player.stress:.0f}/100")
        print(f"   Burnout Risk: {burnout:.2f}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        skill_rec = self.skill_advisor.recommend(self.player)
        print(f"   - Upgrade: {skill_rec}")
        
        if burnout > 0.6:
            print(f"   - Take a break!")
        elif self.session_time > 120:
            print(f"   - Session too long - aim for 60-90 min")
        
        self.economy.adjust_prices(self.total_gold, 0)
        print(f"   - Economy inflation: {self.economy.inflation:.2f}x")
        
        print(f"\n{'='*70}\n")

# ==================== DEMO ====================

def main():
    print("\n" + "="*70)
    print("MMO UNIFIED SYSTEM - All 5 Mechanics Integration")
    print("="*70)
    print("\nMechanics:")
    print("  1. QuestOptimizer - TSP route optimization")
    print("  2. DifficultyDirector - Adaptive challenge")
    print("  3. WellnessMonitor - Burnout detection")
    print("  4. EconomyManager - Inflation control")
    print("  5. SkillAdvisor - Build optimization")
    print("="*70)
    
    # Demo 1: Casual player
    casual = Player(
        name="CasualGamer",
        level=5,
        x=0.0, y=0.0,
        gold=500,
        energy=100.0,
        stress=10.0
    )
    
    session1 = GameSession(casual)
    session1.run_session(quest_count=4)
    
    # Demo 2: Hardcore player
    hardcore = Player(
        name="HardcoreGrinder",
        level=10,
        x=0.0, y=0.0,
        gold=2000,
        energy=100.0,
        stress=20.0
    )
    
    session2 = GameSession(hardcore)
    session2.run_session(quest_count=8)
    
    print("="*70)
    print("✅ ALL 5 MECHANICS SUCCESSFULLY INTEGRATED")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
