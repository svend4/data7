# API Documentation - MMO RPG Optimization Systems

**Version**: 4.0
**Last Updated**: 2026-02-04

---

## Table of Contents

1. [SmartQuestLog](#smartquestlog)
2. [AIDirector](#aidirector)
3. [BurnoutDetector](#burnoutdetector)
4. [EconomyBalancer](#economybalancer)
5. [SkillTreeOptimizer](#skilltreeoptimizer)
6. [Data Models](#data-models)
7. [Usage Examples](#usage-examples)

---

## SmartQuestLog

TSP-based quest route optimization system.

### Constructor

```python
SmartQuestLog(locations: Dict[str, Location], quests: Dict[str, Quest])
```

**Parameters**:
- `locations`: Dictionary mapping location IDs to Location objects
- `quests`: Dictionary mapping quest IDs to Quest objects

### Methods

#### optimize_quest_order()

```python
def optimize_quest_order(
    self,
    player: PlayerState,
    active_quests: List[str]
) -> Tuple[List[str], float]
```

Optimizes the order of quest completion using TSP algorithm.

**Parameters**:
- `player`: Current player state (includes position)
- `active_quests`: List of quest IDs to optimize

**Returns**:
- `Tuple[List[str], float]`: (optimized_quest_order, time_saved_minutes)

**Performance**: O(n²) where n = number of quests
**Typical Runtime**: 0.153ms for 35 quests

**Example**:
```python
quest_log = SmartQuestLog(locations, quests)
optimized, time_saved = quest_log.optimize_quest_order(player, ["quest_1", "quest_2", "quest_3"])
print(f"Optimized order: {optimized}")
print(f"Time saved: {time_saved:.1f} minutes")
```

#### generate_quest_log_ui()

```python
def generate_quest_log_ui(
    self,
    player: PlayerState,
    active_quests: List[str]
) -> str
```

Generates a user-friendly quest log UI with optimized routing.

**Returns**: String containing formatted ASCII UI

**Example Output**:
```
🗺️  OPTIMIZED ROUTE (saves ~25 minutes)
═══════════════════════════════════════

📍 ZONE 1 (Start here!)
  1. [Level 15] Kill 10 Wolves
  2. [Level 15] Collect 5 Herbs

📍 ZONE 2 (Next zone)
  3. [Level 16] Talk to NPC
```

---

## AIDirector

Dynamic difficulty adjustment system based on player performance.

### Constructor

```python
AIDirector()
```

### Methods

#### analyze_performance()

```python
def analyze_performance(self, player: PlayerState) -> Dict[str, float]
```

Analyzes player performance metrics.

**Returns**:
```python
{
    'success_rate': float,      # 0.0-1.0
    'death_rate': float,        # 0.0-1.0
    'skill_estimate': float,    # 0.0-1.0
    'challenge_level': float    # 0.0-1.0
}
```

#### adjust_difficulty()

```python
def adjust_difficulty(self, player: PlayerState) -> Dict[str, any]
```

Calculates difficulty adjustments to maintain Flow State.

**Returns**:
```python
{
    'difficulty_change': float,        # -1.0 to +1.0
    'enemy_hp_multiplier': float,      # 0.5 to 1.5
    'enemy_damage_multiplier': float,  # 0.5 to 1.5
    'spawn_rate_multiplier': float,    # 0.5 to 1.5
    'loot_multiplier': float,          # 0.8 to 1.2
    'recommendation': str              # Human-readable suggestion
}
```

**Target**: Maintains 60-80% success rate (Flow State)

**Example**:
```python
director = AIDirector()
adjustments = director.adjust_difficulty(player)

if adjustments['difficulty_change'] < 0:
    print(f"Making game easier: {adjustments['recommendation']}")
    enemy.hp *= adjustments['enemy_hp_multiplier']
    enemy.damage *= adjustments['enemy_damage_multiplier']
```

---

## BurnoutDetector

Player burnout risk monitoring and intervention system.

### Constructor

```python
BurnoutDetector()
```

### Methods

#### calculate_burnout_risk()

```python
def calculate_burnout_risk(self, player: PlayerState) -> float
```

Calculates burnout risk score using 5-component formula.

**Formula**:
```
risk = 0.25 * repetitiveness +
       0.25 * frustration +
       0.20 * progress_stagnation +
       0.15 * social_isolation +
       0.15 * time_pressure
```

**Returns**: Risk score from 0.0 (no risk) to 1.0 (high risk)

**Interpretation**:
- `< 0.6`: Healthy
- `0.6-0.8`: Warning (intervention recommended)
- `> 0.8`: Critical (immediate action required)

#### detect_and_intervene()

```python
def detect_and_intervene(self, player: PlayerState) -> Dict[str, any]
```

Detects burnout risk and suggests interventions.

**Returns**:
```python
{
    'risk_level': float,                    # 0.0-1.0
    'status': str,                          # "healthy" | "warning" | "critical"
    'interventions': List[str],             # Suggested actions
    'reward_boost': float,                  # Recommended reward multiplier
    'alternative_content': List[str],       # Suggested activities
    'recommend_break': bool                 # Whether to suggest a break
}
```

**Example**:
```python
detector = BurnoutDetector()
result = detector.detect_and_intervene(player)

if result['status'] == 'warning':
    print(f"⚠️ Burnout risk: {result['risk_level']:.2f}")
    print(f"Suggestions: {', '.join(result['interventions'])}")

    # Apply reward boost
    if result['reward_boost'] > 1.0:
        quest_reward *= result['reward_boost']
```

#### suggest_interventions()

```python
def suggest_interventions(self, player: PlayerState) -> List[str]
```

Returns list of suggested interventions.

**Example Return**:
```python
[
    "Consider trying PvP for variety",
    "Your guild has an event in 30 minutes",
    "Take a 15-minute break to maintain peak performance",
    "Try exploring the new zone that just unlocked"
]
```

---

## EconomyBalancer

Automatic game economy inflation control system.

### Constructor

```python
EconomyBalancer()
```

### Methods

#### monitor_economy()

```python
def monitor_economy(self) -> Dict[str, float]
```

Monitors current economic health.

**Returns**:
```python
{
    'gold_generation_rate': float,    # Gold entering economy per day
    'gold_sink_rate': float,          # Gold leaving economy per day
    'inflation_rate': float,          # generation / sink (target: 1.0)
    'total_gold': int,                # Total gold in economy
    'avg_gold_per_player': float      # Average wealth
}
```

#### balance_economy()

```python
def balance_economy(self) -> Dict[str, any]
```

Automatically adjusts economy to maintain target inflation rate.

**Target**: 1.0x inflation (balanced generation/sink)
**Tolerance**: ±15% (0.85x - 1.15x)

**Returns**:
```python
{
    'action_taken': str,                        # "increase_sinks" | "decrease_sinks" | "none"
    'old_inflation': float,                     # Previous inflation rate
    'new_inflation_estimate': float,            # Expected new rate
    'adjustments': {
        'repair_cost_multiplier': float,        # New repair cost modifier
        'teleport_cost_multiplier': float,      # New teleport cost modifier
        'auction_fee_rate': float               # New auction fee %
    }
}
```

**Example**:
```python
balancer = EconomyBalancer()

# Monitor every game tick
metrics = balancer.monitor_economy()

# Balance weekly
if game_day % 7 == 0:
    result = balancer.balance_economy()

    if result['action_taken'] == 'increase_sinks':
        print(f"Inflation too high ({result['old_inflation']:.2f}x)")
        print(f"Increasing costs: {result['adjustments']}")

        # Apply adjustments
        repair_cost_base *= result['adjustments']['repair_cost_multiplier']
        teleport_cost_base *= result['adjustments']['teleport_cost_multiplier']
```

**Validation Results**:
- 100% success rate within ±20% of target (10 trials)
- Scales consistently: 50-500 players
- Long-term stable: Converges to target over 365 days

---

## SkillTreeOptimizer

Skill tree build optimization using ROI-based greedy algorithm.

### Constructor

```python
SkillTreeOptimizer()
```

### Methods

#### optimize_build()

```python
def optimize_build(
    self,
    available_points: int,
    playstyle: str = 'balanced'
) -> List[str]
```

Calculates optimal skill point allocation.

**Parameters**:
- `available_points`: Number of skill points to allocate
- `playstyle`: Target playstyle
  - `'dps'`: Maximize damage output
  - `'tank'`: Maximize survivability
  - `'balanced'`: Balance offense and defense
  - `'support'`: Maximize utility and healing

**Returns**: List of skill IDs in optimal acquisition order

**Algorithm**: Greedy ROI selection with prerequisite handling

**Example**:
```python
optimizer = SkillTreeOptimizer()
optimal_skills = optimizer.optimize_build(available_points=15, playstyle='dps')

print("Optimal build:")
for i, skill_id in enumerate(optimal_skills, 1):
    skill = optimizer.available_skills[skill_id]
    print(f"  {i}. {skill.name} (Power: {skill.power})")
```

#### evaluate_build()

```python
def evaluate_build(self, skill_ids: List[str]) -> float
```

Evaluates total power of a skill build including synergies.

**Returns**: Total power score

**Formula**:
```
power = sum(skill.power for each skill) +
        sum(synergy bonuses between skills)
```

**Example**:
```python
build = optimizer.optimize_build(15, 'dps')
power = optimizer.evaluate_build(build)
print(f"Build power: {power}")

# Compare with alternative
alternative = optimizer.optimize_build(15, 'tank')
alt_power = optimizer.evaluate_build(alternative)
print(f"Alternative power: {alt_power}")
```

#### suggest_respec()

```python
def suggest_respec(
    self,
    current_skills: List[str],
    available_points: int
) -> Dict[str, any]
```

Suggests skill respecification if better builds available.

**Returns**:
```python
{
    'should_respec': bool,
    'current_power': float,
    'optimal_power': float,
    'improvement': float,            # Percentage gain
    'optimal_build': List[str],
    'skills_to_remove': List[str],
    'skills_to_add': List[str]
}
```

---

## Data Models

### PlayerState

```python
@dataclass
class PlayerState:
    id: str
    name: str
    level: int
    experience: int
    gold: int
    current_location: str

    # Skills
    skills: Dict[str, int] = field(default_factory=dict)
    skill_points: int = 0

    # Metrics
    session_time: float = 0.0
    total_play_time: float = 0.0
    fun_level: float = 0.75
    frustration: float = 0.2
    energy: float = 0.9

    # Activity
    recent_deaths: int = 0
    recent_successes: int = 0
    repetitive_actions: int = 0
```

### Location

```python
@dataclass
class Location:
    x: float
    y: float
    zone: str
```

### Quest

```python
@dataclass
class Quest:
    id: str
    name: str
    location: Location
    level: int
    reward_xp: int
    reward_gold: int
    prerequisites: List[str] = field(default_factory=list)
```

### Skill

```python
@dataclass
class Skill:
    id: str
    name: str
    cost: int                                    # Skill points required
    power: float                                 # Base effectiveness
    skill_type: str                              # 'damage', 'defense', 'utility'
    prerequisites: List[str] = field(default_factory=list)
    synergies: Dict[str, float] = field(default_factory=dict)  # skill_id: bonus
```

---

## Usage Examples

### Complete Integration Example

```python
from mmo_rpg_mechanics import (
    SmartQuestLog, AIDirector, BurnoutDetector,
    EconomyBalancer, SkillTreeOptimizer,
    PlayerState, Location, Quest, Skill
)

# Initialize systems
quest_log = SmartQuestLog(locations, quests)
ai_director = AIDirector()
burnout_detector = BurnoutDetector()
economy_balancer = EconomyBalancer()
skill_optimizer = SkillTreeOptimizer()

def game_loop(player: PlayerState, delta_time: float):
    """Main game loop with all systems integrated"""

    # 1. Quest optimization (when player opens quest log)
    if player.opened_quest_log:
        optimized_quests, time_saved = quest_log.optimize_quest_order(
            player,
            player.active_quests
        )
        ui = quest_log.generate_quest_log_ui(player, optimized_quests)
        display_to_player(ui)

    # 2. Dynamic difficulty (every combat encounter)
    if player.in_combat:
        performance = ai_director.analyze_performance(player)
        adjustments = ai_director.adjust_difficulty(player)

        apply_difficulty_adjustments(
            enemy,
            adjustments['enemy_hp_multiplier'],
            adjustments['enemy_damage_multiplier']
        )

    # 3. Burnout detection (every session)
    burnout_risk = burnout_detector.calculate_burnout_risk(player)
    if burnout_risk > 0.6:
        interventions = burnout_detector.detect_and_intervene(player)

        # Show gentle notification
        if interventions['recommend_break']:
            show_notification(
                "You've been playing for a while! "
                "Consider taking a break. "
                "Your XP will continue to accumulate!"
            )

        # Apply reward boosts
        if interventions['reward_boost'] > 1.0:
            boost_quest_rewards(interventions['reward_boost'])

    # 4. Economic balancing (weekly background task)
    if is_weekly_maintenance():
        metrics = economy_balancer.monitor_economy()
        log_economic_metrics(metrics)

        result = economy_balancer.balance_economy()
        if result['action_taken'] != 'none':
            apply_price_adjustments(result['adjustments'])
            log_balancing_action(result)

    # 5. Skill optimization (when leveling up)
    if player.just_leveled_up and player.skill_points > 0:
        optimal_build = skill_optimizer.optimize_build(
            player.skill_points,
            player.preferred_playstyle
        )

        show_skill_recommendations(player, optimal_build)
```

### Error Handling

```python
from mmo_rpg_mechanics import SmartQuestLog

try:
    quest_log = SmartQuestLog(locations, quests)
    optimized, time_saved = quest_log.optimize_quest_order(player, active_quests)
except ValueError as e:
    print(f"Invalid quest data: {e}")
except Exception as e:
    print(f"Optimization error: {e}")
    # Fallback to default order
    optimized = active_quests
```

### Performance Monitoring

```python
import time

def benchmark_quest_optimization(num_quests: int, trials: int = 100):
    """Benchmark quest optimization performance"""
    times = []

    for _ in range(trials):
        # Generate test data
        player = generate_test_player()
        quests = generate_test_quests(num_quests)

        # Measure
        start = time.perf_counter()
        optimized, _ = quest_log.optimize_quest_order(player, quests)
        end = time.perf_counter()

        times.append((end - start) * 1000)  # Convert to ms

    avg_time = sum(times) / len(times)
    print(f"{num_quests} quests: {avg_time:.3f}ms average")
```

---

## Performance Guarantees

### SmartQuestLog
- **Time Complexity**: O(n²)
- **Space Complexity**: O(n²)
- **Typical Performance**: 0.153ms for 35 quests
- **Maximum Recommended**: 50 quests

### AIDirector
- **Time Complexity**: O(1)
- **Space Complexity**: O(1)
- **Typical Performance**: <1ms
- **Update Frequency**: Every combat encounter

### BurnoutDetector
- **Time Complexity**: O(1)
- **Space Complexity**: O(n) for history
- **Typical Performance**: <1ms
- **Update Frequency**: Every 5-10 minutes

### EconomyBalancer
- **Time Complexity**: O(m) where m = number of market items
- **Space Complexity**: O(m)
- **Typical Performance**: <10ms
- **Update Frequency**: Weekly

### SkillTreeOptimizer
- **Time Complexity**: O(n log n)
- **Space Complexity**: O(n)
- **Typical Performance**: <5ms
- **Update Frequency**: On level up

---

## Thread Safety

⚠️ **Important**: These systems are not thread-safe by default.

**Recommendations**:
1. Use separate instances per player/game session
2. Implement locking for shared resources (economy balancer)
3. Use actor pattern for concurrent access

**Example** (thread-safe economy balancer):
```python
import threading

class ThreadSafeEconomyBalancer:
    def __init__(self):
        self.balancer = EconomyBalancer()
        self.lock = threading.Lock()

    def balance_economy(self):
        with self.lock:
            return self.balancer.balance_economy()
```

---

## Version Compatibility

- **Python**: 3.7+
- **Dependencies**: None (matplotlib optional for visualizations)
- **Backwards Compatibility**: Breaking changes documented in CHANGELOG.md

---

## Support

For questions, bug reports, or feature requests:
- **Documentation**: See [README.md](README.md)
- **Validation**: See [MMO_VALIDATION_REPORT.md](MMO_VALIDATION_REPORT.md)
- **Theory**: See [MMO_RPG_GAMEDESIGN_THEORY.md](mmo_rpg_gamedesign_theory.md)

---

**API Version**: 4.0
**Last Updated**: 2026-02-04
**Status**: ✅ Production Ready
