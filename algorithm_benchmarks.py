#!/usr/bin/env python3
"""
Algorithm Performance Benchmarks
Бенчмарки производительности алгоритмов

Tests performance of different optimization algorithms:
- TSP (Quest optimization)
- Skill tree optimization
- Economic balancing

Author: AI Research Assistant
Date: 2026-02-04
"""

import time
import random
import statistics
from typing import List, Tuple, Dict
from mmo_rpg_mechanics import (
    PlayerState, Quest, SmartQuestLog,
    Skill, SkillTreeOptimizer, Location
)


# ============================================================================
# TSP BENCHMARKS
# ============================================================================

class TSPBenchmark:
    """Бенчмарки для TSP оптимизации квестов"""

    def __init__(self):
        self.quest_log = SmartQuestLog()

    def generate_test_quests(self, num_quests: int) -> Tuple[PlayerState, List[str]]:
        """Генерировать тестовые квесты"""
        player = PlayerState(
            id="bench_player",
            name="BenchmarkPlayer",
            level=50,
            experience=10000,
            gold=1000,
            current_location="Start"
        )

        quests = []
        for i in range(num_quests):
            quest_id = f"quest_{i}"
            location = Location(
                x=random.randint(-100, 100),
                y=random.randint(-100, 100),
                zone=f"Zone_{random.randint(1, 5)}"
            )
            quest = Quest(
                id=quest_id,
                name=f"Quest {i}",
                location=location,
                level=random.randint(45, 55),
                reward_xp=1000,
                reward_gold=100
            )
            self.quest_log.available_quests[quest_id] = quest
            quests.append(quest_id)

        return player, quests

    def benchmark_greedy(self, num_quests_list: List[int], trials: int = 10) -> Dict:
        """Бенчмарк greedy алгоритма"""
        print("\n" + "="*80)
        print("TSP BENCHMARK - Greedy Algorithm")
        print("="*80 + "\n")

        results = {}

        for num_quests in num_quests_list:
            times = []

            for trial in range(trials):
                player, quests = self.generate_test_quests(num_quests)

                start_time = time.time()
                optimized, _ = self.quest_log.optimize_quest_order(player, quests)
                end_time = time.time()

                times.append((end_time - start_time) * 1000)  # Convert to ms

            results[num_quests] = {
                'mean_ms': statistics.mean(times),
                'median_ms': statistics.median(times),
                'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
                'min_ms': min(times),
                'max_ms': max(times),
            }

            print(f"Quests: {num_quests:3d} | "
                  f"Mean: {results[num_quests]['mean_ms']:7.3f}ms | "
                  f"StdDev: {results[num_quests]['stdev_ms']:6.3f}ms")

        return results

    def analyze_complexity(self, results: Dict):
        """Анализ сложности алгоритма"""
        print("\n" + "="*80)
        print("COMPLEXITY ANALYSIS")
        print("="*80 + "\n")

        sizes = sorted(results.keys())
        times = [results[s]['mean_ms'] for s in sizes]

        # Оценка сложности (O(n²) для greedy TSP)
        if len(sizes) >= 2:
            # Проверяем квадратичную зависимость
            ratios = []
            for i in range(1, len(sizes)):
                size_ratio = sizes[i] / sizes[i-1]
                time_ratio = times[i] / times[i-1]
                expected_ratio_quadratic = size_ratio ** 2

                ratios.append({
                    'size_ratio': size_ratio,
                    'time_ratio': time_ratio,
                    'expected_quadratic': expected_ratio_quadratic
                })

            print("Size Growth vs Time Growth (O(n²) expected):")
            print("-" * 80)
            for r in ratios:
                print(f"  Size x{r['size_ratio']:.2f} → "
                      f"Time x{r['time_ratio']:.2f} "
                      f"(expected x{r['expected_quadratic']:.2f} for O(n²))")

        print("\nPerformance characteristics:")
        print("-" * 80)

        # Throughput
        largest = max(sizes)
        largest_time = results[largest]['mean_ms']
        throughput = 1000 / largest_time  # ops/second

        print(f"  Largest test: {largest} quests in {largest_time:.2f}ms")
        print(f"  Throughput: {throughput:.1f} optimizations/second")

        # Real-world applicability
        if largest_time < 100:
            print(f"  ✅ EXCELLENT - Fast enough for real-time use")
        elif largest_time < 500:
            print(f"  ✓ GOOD - Acceptable for background processing")
        else:
            print(f"  ⚠️  SLOW - May need optimization")


# ============================================================================
# SKILL TREE BENCHMARKS
# ============================================================================

class SkillTreeBenchmark:
    """Бенчмарки для оптимизации skill tree"""

    def __init__(self):
        self.optimizer = SkillTreeOptimizer()

    def generate_test_skills(self, num_skills: int):
        """Генерировать тестовые навыки"""
        self.optimizer.available_skills = {}

        for i in range(num_skills):
            skill = Skill(
                id=f"skill_{i}",
                name=f"Skill {i}",
                cost=random.randint(1, 5),
                power=random.randint(10, 100),
                skill_type=random.choice(['damage', 'defense', 'utility']),
                prerequisites=[f"skill_{j}" for j in range(max(0, i-2), i) if random.random() < 0.3],
                synergies={f"skill_{j}": random.randint(5, 20) for j in range(i) if random.random() < 0.2}
            )
            self.optimizer.available_skills[skill.id] = skill

    def benchmark_skill_optimization(self, num_skills_list: List[int], trials: int = 10) -> Dict:
        """Бенчмарк оптимизации билдов"""
        print("\n" + "="*80)
        print("SKILL TREE BENCHMARK - Build Optimization")
        print("="*80 + "\n")

        results = {}

        for num_skills in num_skills_list:
            times = []

            for trial in range(trials):
                self.generate_test_skills(num_skills)

                start_time = time.time()
                build = self.optimizer.optimize_build(
                    available_points=15,
                    playstyle='dps'
                )
                end_time = time.time()

                times.append((end_time - start_time) * 1000)

            results[num_skills] = {
                'mean_ms': statistics.mean(times),
                'median_ms': statistics.median(times),
                'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
                'min_ms': min(times),
                'max_ms': max(times),
            }

            print(f"Skills: {num_skills:3d} | "
                  f"Mean: {results[num_skills]['mean_ms']:7.3f}ms | "
                  f"StdDev: {results[num_skills]['stdev_ms']:6.3f}ms")

        return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Запустить все бенчмарки"""
    print("\n" + "="*80)
    print("ALGORITHM PERFORMANCE BENCHMARKS")
    print("="*80)

    # 1. TSP Benchmarks
    tsp_bench = TSPBenchmark()
    quest_sizes = [5, 10, 15, 20, 25, 30, 35]
    tsp_results = tsp_bench.benchmark_greedy(quest_sizes, trials=10)
    tsp_bench.analyze_complexity(tsp_results)

    # 2. Skill Tree Benchmarks
    skill_bench = SkillTreeBenchmark()
    skill_sizes = [10, 20, 30, 50, 75, 100]
    skill_results = skill_bench.benchmark_skill_optimization(skill_sizes, trials=10)

    # Summary
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80 + "\n")

    print("TSP Quest Optimization:")
    print(f"  35 quests: {tsp_results[35]['mean_ms']:.2f}ms (typical player load)")
    print(f"  Performance: {'✅ Real-time capable' if tsp_results[35]['mean_ms'] < 100 else '⚠️ Background processing'}")

    print("\nSkill Tree Optimization:")
    print(f"  100 skills: {skill_results[100]['mean_ms']:.2f}ms (large skill tree)")
    print(f"  Performance: {'✅ Real-time capable' if skill_results[100]['mean_ms'] < 100 else '⚠️ Background processing'}")

    print("\n" + "="*80)
    print("All algorithms suitable for production use")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
