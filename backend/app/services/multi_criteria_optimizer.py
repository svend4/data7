"""
Multi-Criteria Optimization using NSGA-II

Implements Non-dominated Sorting Genetic Algorithm II for optimizing
multiple conflicting objectives simultaneously.

Use case: Balance readability, comprehensiveness, engagement, and time
in dissertation optimization, knowledge transformation, etc.
"""

from typing import List, Dict, Tuple, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import math
from datetime import datetime


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Objective:
    """Optimization objective"""
    name: str
    minimize: bool = True  # True = minimize, False = maximize
    weight: float = 1.0  # Relative importance


@dataclass
class Solution:
    """Solution in multi-objective space"""
    id: str
    genes: List[float]  # Decision variables
    objectives: Dict[str, float]  # Objective values
    rank: int = 0  # Pareto rank (0 = non-dominated)
    crowding_distance: float = 0.0  # Diversity metric
    metadata: Dict = field(default_factory=dict)


@dataclass
class ParetoFront:
    """Pareto-optimal solutions"""
    solutions: List[Solution]
    objectives: List[Objective]
    generation: int
    hypervolume: float = 0.0  # Quality metric
    metadata: Dict = field(default_factory=dict)


class OptimizationObjective(Enum):
    """Common optimization objectives"""
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_QUALITY = "maximize_quality"
    MAXIMIZE_READABILITY = "maximize_readability"
    MAXIMIZE_ENGAGEMENT = "maximize_engagement"
    MINIMIZE_COMPLEXITY = "minimize_complexity"


# ============================================================================
# NSGA-II Implementation
# ============================================================================

class NSGAII:
    """
    Non-dominated Sorting Genetic Algorithm II

    Multi-objective evolutionary algorithm that finds Pareto-optimal
    solutions balancing multiple conflicting objectives.

    Key features:
    - Fast non-dominated sorting
    - Crowding distance for diversity
    - Elite preservation
    """

    def __init__(
        self,
        objectives: List[Objective],
        population_size: int = 100,
        num_generations: int = 100,
        crossover_prob: float = 0.9,
        mutation_prob: float = 0.1,
        mutation_strength: float = 0.1
    ):
        self.objectives = objectives
        self.population_size = population_size
        self.num_generations = num_generations
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.mutation_strength = mutation_strength

    def optimize(
        self,
        evaluate_fn: Callable[[List[float]], Dict[str, float]],
        gene_bounds: List[Tuple[float, float]],
        initial_population: Optional[List[List[float]]] = None
    ) -> ParetoFront:
        """
        Run NSGA-II optimization

        Args:
            evaluate_fn: Function that evaluates solution genes -> objectives
            gene_bounds: Bounds for each gene [(min, max), ...]
            initial_population: Optional initial population

        Returns:
            ParetoFront with non-dominated solutions
        """
        # Initialize population
        if initial_population:
            population = self._create_population_from_genes(
                initial_population, evaluate_fn
            )
        else:
            population = self._initialize_population(gene_bounds, evaluate_fn)

        # Evolution loop
        for generation in range(self.num_generations):
            # Create offspring
            offspring = self._create_offspring(population, gene_bounds)

            # Evaluate offspring
            for solution in offspring:
                solution.objectives = evaluate_fn(solution.genes)

            # Combine parent and offspring
            combined = population + offspring

            # Non-dominated sorting
            fronts = self._fast_non_dominated_sort(combined)

            # Calculate crowding distance
            for front in fronts:
                self._calculate_crowding_distance(front)

            # Select next generation
            population = self._select_next_generation(fronts, self.population_size)

        # Extract final Pareto front
        fronts = self._fast_non_dominated_sort(population)
        pareto_front = fronts[0] if fronts else []

        # Calculate hypervolume
        hypervolume = self._calculate_hypervolume(pareto_front)

        return ParetoFront(
            solutions=pareto_front,
            objectives=self.objectives,
            generation=self.num_generations,
            hypervolume=hypervolume,
            metadata={
                "population_size": self.population_size,
                "final_population_size": len(population)
            }
        )

    # Private methods

    def _initialize_population(
        self,
        gene_bounds: List[Tuple[float, float]],
        evaluate_fn: Callable[[List[float]], Dict[str, float]]
    ) -> List[Solution]:
        """Initialize random population"""
        population = []

        for i in range(self.population_size):
            # Random genes within bounds
            genes = [
                random.uniform(low, high)
                for low, high in gene_bounds
            ]

            # Evaluate
            objectives = evaluate_fn(genes)

            solution = Solution(
                id=f"sol_{i}",
                genes=genes,
                objectives=objectives
            )
            population.append(solution)

        return population

    def _create_population_from_genes(
        self,
        genes_list: List[List[float]],
        evaluate_fn: Callable[[List[float]], Dict[str, float]]
    ) -> List[Solution]:
        """Create population from gene list"""
        population = []

        for i, genes in enumerate(genes_list):
            objectives = evaluate_fn(genes)
            solution = Solution(
                id=f"sol_{i}",
                genes=genes,
                objectives=objectives
            )
            population.append(solution)

        return population

    def _create_offspring(
        self,
        population: List[Solution],
        gene_bounds: List[Tuple[float, float]]
    ) -> List[Solution]:
        """Create offspring through crossover and mutation"""
        offspring = []

        for i in range(len(population)):
            # Select parents using binary tournament
            parent1 = self._binary_tournament(population)
            parent2 = self._binary_tournament(population)

            # Crossover
            if random.random() < self.crossover_prob:
                child_genes = self._crossover(parent1.genes, parent2.genes)
            else:
                child_genes = parent1.genes[:]

            # Mutation
            if random.random() < self.mutation_prob:
                child_genes = self._mutate(child_genes, gene_bounds)

            child = Solution(
                id=f"child_{i}",
                genes=child_genes,
                objectives={}  # Will be evaluated later
            )
            offspring.append(child)

        return offspring

    def _binary_tournament(self, population: List[Solution]) -> Solution:
        """Select solution using binary tournament"""
        candidate1 = random.choice(population)
        candidate2 = random.choice(population)

        # Select based on rank and crowding distance
        if candidate1.rank < candidate2.rank:
            return candidate1
        elif candidate1.rank > candidate2.rank:
            return candidate2
        else:
            # Same rank, select based on crowding distance
            if candidate1.crowding_distance > candidate2.crowding_distance:
                return candidate1
            else:
                return candidate2

    def _crossover(
        self,
        genes1: List[float],
        genes2: List[float]
    ) -> List[float]:
        """Simulated Binary Crossover (SBX)"""
        child = []
        eta = 20.0  # Distribution index

        for g1, g2 in zip(genes1, genes2):
            if random.random() < 0.5:
                beta = (2 * random.random()) ** (1.0 / (eta + 1))
            else:
                beta = (1.0 / (2 * (1 - random.random()))) ** (1.0 / (eta + 1))

            child_gene = 0.5 * ((1 + beta) * g1 + (1 - beta) * g2)
            child.append(child_gene)

        return child

    def _mutate(
        self,
        genes: List[float],
        gene_bounds: List[Tuple[float, float]]
    ) -> List[float]:
        """Polynomial mutation"""
        mutated = []
        eta = 20.0  # Distribution index

        for gene, (low, high) in zip(genes, gene_bounds):
            if random.random() < 1.0 / len(genes):
                delta = min(gene - low, high - gene) / (high - low)
                rand = random.random()

                if rand < 0.5:
                    delta_q = (2 * rand) ** (1.0 / (eta + 1)) - 1
                else:
                    delta_q = 1 - (2 * (1 - rand)) ** (1.0 / (eta + 1))

                mutated_gene = gene + delta_q * (high - low) * self.mutation_strength
                mutated_gene = max(low, min(high, mutated_gene))
                mutated.append(mutated_gene)
            else:
                mutated.append(gene)

        return mutated

    def _fast_non_dominated_sort(
        self,
        population: List[Solution]
    ) -> List[List[Solution]]:
        """
        Fast non-dominated sorting

        Returns list of fronts, where front[0] is Pareto-optimal
        """
        # For each solution, find domination relationships
        domination_count = {sol.id: 0 for sol in population}
        dominated_solutions = {sol.id: [] for sol in population}

        for i, sol1 in enumerate(population):
            for sol2 in population[i+1:]:
                dominance = self._dominates(sol1, sol2)
                if dominance == 1:  # sol1 dominates sol2
                    dominated_solutions[sol1.id].append(sol2)
                    domination_count[sol2.id] += 1
                elif dominance == -1:  # sol2 dominates sol1
                    dominated_solutions[sol2.id].append(sol1)
                    domination_count[sol1.id] += 1

        # Build fronts
        fronts = []
        current_front = []

        # First front: non-dominated solutions
        for sol in population:
            if domination_count[sol.id] == 0:
                sol.rank = 0
                current_front.append(sol)

        fronts.append(current_front)

        # Build subsequent fronts
        i = 0
        while i < len(fronts) and fronts[i]:
            next_front = []
            for sol in fronts[i]:
                for dominated_sol in dominated_solutions[sol.id]:
                    domination_count[dominated_sol.id] -= 1
                    if domination_count[dominated_sol.id] == 0:
                        dominated_sol.rank = i + 1
                        next_front.append(dominated_sol)

            if next_front:
                fronts.append(next_front)
            i += 1

        return fronts

    def _dominates(self, sol1: Solution, sol2: Solution) -> int:
        """
        Check if sol1 dominates sol2

        Returns:
            1 if sol1 dominates sol2
            -1 if sol2 dominates sol1
            0 if neither dominates
        """
        better_count = 0
        worse_count = 0

        for obj in self.objectives:
            val1 = sol1.objectives.get(obj.name, 0.0)
            val2 = sol2.objectives.get(obj.name, 0.0)

            if obj.minimize:
                if val1 < val2:
                    better_count += 1
                elif val1 > val2:
                    worse_count += 1
            else:  # maximize
                if val1 > val2:
                    better_count += 1
                elif val1 < val2:
                    worse_count += 1

        if better_count > 0 and worse_count == 0:
            return 1  # sol1 dominates
        elif worse_count > 0 and better_count == 0:
            return -1  # sol2 dominates
        else:
            return 0  # Non-dominated

    def _calculate_crowding_distance(self, front: List[Solution]) -> None:
        """Calculate crowding distance for solutions in front"""
        if len(front) <= 2:
            for sol in front:
                sol.crowding_distance = float('inf')
            return

        # Initialize
        for sol in front:
            sol.crowding_distance = 0.0

        # For each objective
        for obj in self.objectives:
            # Sort by objective
            front.sort(key=lambda s: s.objectives.get(obj.name, 0.0))

            # Boundary solutions get infinite distance
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')

            # Calculate range
            obj_min = front[0].objectives.get(obj.name, 0.0)
            obj_max = front[-1].objectives.get(obj.name, 0.0)
            obj_range = obj_max - obj_min

            if obj_range == 0:
                continue

            # Calculate crowding distance
            for i in range(1, len(front) - 1):
                if front[i].crowding_distance != float('inf'):
                    distance = (
                        front[i+1].objectives.get(obj.name, 0.0) -
                        front[i-1].objectives.get(obj.name, 0.0)
                    ) / obj_range
                    front[i].crowding_distance += distance

    def _select_next_generation(
        self,
        fronts: List[List[Solution]],
        population_size: int
    ) -> List[Solution]:
        """Select next generation from fronts"""
        next_generation = []

        for front in fronts:
            if len(next_generation) + len(front) <= population_size:
                # Add entire front
                next_generation.extend(front)
            else:
                # Add part of front based on crowding distance
                remaining = population_size - len(next_generation)
                front.sort(key=lambda s: s.crowding_distance, reverse=True)
                next_generation.extend(front[:remaining])
                break

        return next_generation

    def _calculate_hypervolume(self, pareto_front: List[Solution]) -> float:
        """
        Calculate hypervolume (quality metric for Pareto front)

        Simplified calculation for 2-3 objectives
        """
        if not pareto_front:
            return 0.0

        # Reference point (worst values)
        reference = {}
        for obj in self.objectives:
            values = [s.objectives.get(obj.name, 0.0) for s in pareto_front]
            if obj.minimize:
                reference[obj.name] = max(values) * 1.1
            else:
                reference[obj.name] = min(values) * 0.9

        # Calculate hypervolume (simplified for 2D)
        if len(self.objectives) == 2:
            # Sort by first objective
            obj1_name = self.objectives[0].name
            sorted_front = sorted(
                pareto_front,
                key=lambda s: s.objectives.get(obj1_name, 0.0)
            )

            hypervolume = 0.0
            for sol in sorted_front:
                obj1_val = sol.objectives.get(self.objectives[0].name, 0.0)
                obj2_val = sol.objectives.get(self.objectives[1].name, 0.0)

                width = abs(obj1_val - reference[self.objectives[0].name])
                height = abs(obj2_val - reference[self.objectives[1].name])
                hypervolume += width * height

            return hypervolume
        else:
            # For more objectives, use approximate calculation
            return float(len(pareto_front))


# ============================================================================
# Application: Dissertation Optimization
# ============================================================================

class DissertationMultiObjectiveOptimizer:
    """
    Apply multi-criteria optimization to dissertation structure

    Objectives:
    1. Minimize reading time
    2. Maximize readability (coherence)
    3. Maximize comprehensiveness (coverage)
    4. Maximize engagement (interesting factor)
    """

    def __init__(self):
        self.objectives = [
            Objective(name="time", minimize=True, weight=1.0),
            Objective(name="readability", minimize=False, weight=1.0),
            Objective(name="comprehensiveness", minimize=False, weight=0.8),
            Objective(name="engagement", minimize=False, weight=0.9)
        ]

    def optimize_structure(
        self,
        sections: List[str],
        section_times: Dict[str, float],
        section_scores: Dict[str, Dict[str, float]]
    ) -> ParetoFront:
        """
        Optimize dissertation structure

        Genes: Binary vector indicating which sections to include

        Args:
            sections: List of section IDs
            section_times: Reading time per section
            section_scores: Scores per section {section_id: {metric: score}}

        Returns:
            ParetoFront with optimal structures
        """
        # Define evaluation function
        def evaluate(genes: List[float]) -> Dict[str, float]:
            # Genes are [0, 1] values, threshold at 0.5
            included = [sections[i] for i, g in enumerate(genes) if g > 0.5]

            if not included:
                return {
                    "time": float('inf'),
                    "readability": 0.0,
                    "comprehensiveness": 0.0,
                    "engagement": 0.0
                }

            # Calculate objectives
            time = sum(section_times.get(s, 5.0) for s in included)
            readability = sum(
                section_scores.get(s, {}).get("readability", 0.5)
                for s in included
            ) / len(included)
            comprehensiveness = len(included) / len(sections)
            engagement = sum(
                section_scores.get(s, {}).get("engagement", 0.5)
                for s in included
            ) / len(included)

            return {
                "time": time,
                "readability": readability,
                "comprehensiveness": comprehensiveness,
                "engagement": engagement
            }

        # Run NSGA-II
        nsga = NSGAII(
            objectives=self.objectives,
            population_size=50,
            num_generations=50
        )

        gene_bounds = [(0.0, 1.0) for _ in sections]
        pareto_front = nsga.optimize(evaluate, gene_bounds)

        return pareto_front


# ============================================================================
# Usage Example
# ============================================================================

def example_dissertation_optimization():
    """Example: Optimize dissertation structure"""
    # Sample data
    sections = [f"section_{i}" for i in range(20)]
    section_times = {s: 5.0 + random.uniform(-2, 2) for s in sections}
    section_scores = {
        s: {
            "readability": random.uniform(0.5, 1.0),
            "engagement": random.uniform(0.4, 0.9)
        }
        for s in sections
    }

    # Optimize
    optimizer = DissertationMultiObjectiveOptimizer()
    pareto_front = optimizer.optimize_structure(
        sections, section_times, section_scores
    )

    print(f"Found {len(pareto_front.solutions)} Pareto-optimal structures")
    print(f"Hypervolume: {pareto_front.hypervolume:.2f}")

    # Show top 3 solutions
    for i, sol in enumerate(pareto_front.solutions[:3]):
        print(f"\nSolution {i+1}:")
        print(f"  Time: {sol.objectives['time']:.1f} min")
        print(f"  Readability: {sol.objectives['readability']:.2f}")
        print(f"  Comprehensiveness: {sol.objectives['comprehensiveness']:.2f}")
        print(f"  Engagement: {sol.objectives['engagement']:.2f}")


if __name__ == "__main__":
    example_dissertation_optimization()
