#!/usr/bin/env python3
"""
Simple TSP Benchmark - Standalone Performance Test
Простой бенчмарк TSP - Автономный тест производительности

Tests TSP algorithm performance without full system dependencies.

Author: AI Research Assistant
Date: 2026-02-04
"""

import time
import random
import math
import statistics
from typing import List, Tuple


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Евклидово расстояние"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def greedy_tsp(points: List[Tuple[float, float]]) -> Tuple[List[int], float]:
    """
    Greedy TSP algorithm
    Returns: (path as indices, total distance)
    """
    if not points:
        return [], 0.0

    n = len(points)
    if n == 1:
        return [0], 0.0

    # Start from point 0
    unvisited = set(range(n))
    current = 0
    path = [current]
    unvisited.remove(current)
    total_distance = 0.0

    while unvisited:
        # Find nearest unvisited point
        nearest = min(unvisited, key=lambda i: euclidean_distance(points[current], points[i]))
        distance = euclidean_distance(points[current], points[nearest])
        total_distance += distance

        path.append(nearest)
        current = nearest
        unvisited.remove(nearest)

    return path, total_distance


def benchmark_tsp(num_points_list: List[int], trials: int = 100) -> dict:
    """Бенчмарк TSP с разными размерами"""
    print("\n" + "="*80)
    print("TSP PERFORMANCE BENCHMARK")
    print("="*80 + "\n")

    results = {}

    for num_points in num_points_list:
        times = []

        for trial in range(trials):
            # Generate random points
            points = [(random.uniform(-100, 100), random.uniform(-100, 100))
                     for _ in range(num_points)]

            # Measure time
            start = time.perf_counter()
            path, distance = greedy_tsp(points)
            end = time.perf_counter()

            times.append((end - start) * 1000)  # ms

        results[num_points] = {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'min_ms': min(times),
            'max_ms': max(times),
            'p95_ms': sorted(times)[int(len(times) * 0.95)],
        }

        r = results[num_points]
        print(f"Points: {num_points:3d} | "
              f"Mean: {r['mean_ms']:8.4f}ms | "
              f"Median: {r['median_ms']:8.4f}ms | "
              f"P95: {r['p95_ms']:8.4f}ms | "
              f"StdDev: {r['stdev_ms']:7.4f}ms")

    return results


def analyze_complexity(results: dict):
    """Анализ временной сложности"""
    print("\n" + "="*80)
    print("COMPLEXITY ANALYSIS")
    print("="*80 + "\n")

    sizes = sorted(results.keys())

    # Check O(n²) characteristic
    print("Growth Analysis (O(n²) expected for greedy TSP):")
    print("-" * 80)

    for i in range(1, len(sizes)):
        size_prev = sizes[i-1]
        size_curr = sizes[i]
        time_prev = results[size_prev]['mean_ms']
        time_curr = results[size_curr]['mean_ms']

        size_ratio = size_curr / size_prev
        time_ratio = time_curr / time_prev
        expected_quadratic = size_ratio ** 2

        deviation = abs(time_ratio - expected_quadratic) / expected_quadratic * 100

        print(f"  {size_prev:3d} → {size_curr:3d} points:")
        print(f"    Size ratio: {size_ratio:.2f}x")
        print(f"    Time ratio: {time_ratio:.2f}x (expected {expected_quadratic:.2f}x for O(n²))")
        print(f"    Deviation:  {deviation:.1f}%")
        print()

    # Performance assessment
    print("="*80)
    print("PERFORMANCE ASSESSMENT")
    print("="*80 + "\n")

    typical_size = 35  # Typical quest log size
    if typical_size in results:
        typical_time = results[typical_size]['mean_ms']
        print(f"Typical use case ({typical_size} quests):")
        print(f"  Mean time: {typical_time:.3f}ms")
        print(f"  P95 time:  {results[typical_size]['p95_ms']:.3f}ms")

        if typical_time < 10:
            print(f"  ✅ EXCELLENT - Imperceptible to users (<10ms)")
        elif typical_time < 100:
            print(f"  ✅ EXCELLENT - Real-time capable (<100ms)")
        elif typical_time < 500:
            print(f"  ✓ GOOD - Acceptable for UI interaction (<500ms)")
        else:
            print(f"  ⚠️  SLOW - May cause UI lag (>{typical_time:.0f}ms)")

    # Throughput
    largest = max(sizes)
    largest_time = results[largest]['mean_ms'] / 1000  # to seconds
    throughput = 1 / largest_time if largest_time > 0 else float('inf')

    print(f"\nLargest test ({largest} points):")
    print(f"  Time: {results[largest]['mean_ms']:.3f}ms")
    print(f"  Throughput: {throughput:.1f} optimizations/second")

    # Scalability verdict
    print(f"\n{'='*80}")
    print("SCALABILITY VERDICT:")
    print("-" * 80)

    if results[largest]['mean_ms'] < 100:
        print("✅ EXCELLENT - Scales well even to large problem sizes")
    elif results[largest]['mean_ms'] < 500:
        print("✓ GOOD - Acceptable performance at scale")
    else:
        print("⚠️  Needs optimization for large-scale use")


def main():
    """Run benchmark"""
    print("\n" + "="*80)
    print("GREEDY TSP ALGORITHM PERFORMANCE ANALYSIS")
    print("="*80)
    print("\nTesting with 100 trials per size for statistical confidence...")

    # Test sizes matching typical MMO quest scenarios
    quest_sizes = [5, 10, 15, 20, 25, 30, 35, 40, 50]

    results = benchmark_tsp(quest_sizes, trials=100)
    analyze_complexity(results)

    print("\n" + "="*80)
    print("BENCHMARK COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
