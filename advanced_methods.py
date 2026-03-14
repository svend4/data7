"""
Advanced Methods for Dissertation Optimization
Продвинутые методы оптимизации структуры диссертации

Включает:
- ML-based distance computation (BERT, embeddings)
- Genetic Algorithm with advanced operators
- Multi-objective optimization
- Adaptive learning from writing process

Author: AI Research Assistant
Date: 2026-02-04
"""

import numpy as np
import random
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# ML-BASED SEMANTIC DISTANCE COMPUTATION
# ============================================================================

class SemanticDistanceCalculator:
    """Вычисление семантических дистанций с использованием ML"""

    def __init__(self, model_type: str = 'tfidf'):
        """
        Parameters:
        -----------
        model_type: 'tfidf', 'word2vec', 'bert', 'sentence-transformers'
        """
        self.model_type = model_type
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Инициализация модели"""
        if self.model_type == 'tfidf':
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.model = TfidfVectorizer(max_features=1000, stop_words='english')

        elif self.model_type == 'sentence-transformers':
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                print("⚠ sentence-transformers not installed, falling back to TF-IDF")
                self.model_type = 'tfidf'
                self._initialize_model()

        elif self.model_type == 'bert':
            try:
                from transformers import AutoTokenizer, AutoModel
                self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
                self.model = AutoModel.from_pretrained('bert-base-uncased')
            except ImportError:
                print("⚠ transformers not installed, falling back to TF-IDF")
                self.model_type = 'tfidf'
                self._initialize_model()

    def compute_distance_matrix(self, texts: List[str]) -> np.ndarray:
        """
        Вычисляет матрицу семантических дистанций для текстов

        Parameters:
        -----------
        texts: список текстов глав

        Returns:
        --------
        distance_matrix: NxN матрица дистанций
        """
        if self.model_type == 'tfidf':
            return self._tfidf_distance(texts)

        elif self.model_type == 'sentence-transformers':
            return self._sentence_transformer_distance(texts)

        elif self.model_type == 'bert':
            return self._bert_distance(texts)

    def _tfidf_distance(self, texts: List[str]) -> np.ndarray:
        """TF-IDF based distance"""
        from sklearn.metrics.pairwise import cosine_similarity

        # Векторизация
        tfidf_matrix = self.model.fit_transform(texts)

        # Косинусное сходство
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Преобразование в дистанцию
        distance_matrix = 1 - similarity_matrix

        return distance_matrix

    def _sentence_transformer_distance(self, texts: List[str]) -> np.ndarray:
        """Sentence Transformer embeddings distance"""
        from sklearn.metrics.pairwise import cosine_similarity

        # Получаем embeddings
        embeddings = self.model.encode(texts)

        # Косинусное сходство
        similarity_matrix = cosine_similarity(embeddings)

        # Преобразование в дистанцию
        distance_matrix = 1 - similarity_matrix

        return distance_matrix

    def _bert_distance(self, texts: List[str]) -> np.ndarray:
        """BERT embeddings distance"""
        import torch
        from sklearn.metrics.pairwise import cosine_similarity

        embeddings = []

        for text in texts:
            # Токенизация
            inputs = self.tokenizer(text, return_tensors='pt',
                                   truncation=True, max_length=512, padding=True)

            # Получаем embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Используем [CLS] токен или mean pooling
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
            embeddings.append(embedding[0])

        embeddings = np.array(embeddings)

        # Косинусное сходство
        similarity_matrix = cosine_similarity(embeddings)

        # Преобразование в дистанцию
        distance_matrix = 1 - similarity_matrix

        return distance_matrix


# ============================================================================
# GENETIC ALGORITHM WITH ADVANCED OPERATORS
# ============================================================================

class AdvancedGeneticAlgorithm:
    """Продвинутый генетический алгоритм для оптимизации структуры"""

    def __init__(self,
                 chapters: List,
                 distance_matrix: np.ndarray,
                 dependencies: Dict[str, List[str]],
                 start_id: str,
                 end_id: str,
                 population_size: int = 100,
                 elite_size: int = 10,
                 mutation_rate: float = 0.2,
                 crossover_rate: float = 0.8):
        """
        Parameters:
        -----------
        chapters: список глав
        distance_matrix: матрица дистанций
        dependencies: зависимости между главами
        start_id, end_id: ID начала и конца
        population_size: размер популяции
        elite_size: количество элитных особей
        mutation_rate: вероятность мутации
        crossover_rate: вероятность кроссовера
        """
        self.chapters = {ch.id: ch for ch in chapters}
        self.distance_matrix = distance_matrix
        self.dependencies = dependencies
        self.start_id = start_id
        self.end_id = end_id
        self.pop_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

        # Маппинги
        self.id_to_index = {ch.id: i for i, ch in enumerate(chapters)}
        self.index_to_id = {i: ch.id for ch_id, i in self.id_to_index.items()}

    def create_individual(self) -> List[str]:
        """Создание одной особи (валидной последовательности)"""
        start, end = self.start_id, self.end_id
        middle = list(set(self.chapters.keys()) - {start, end})

        # Топологическая сортировка с рандомизацией
        individual = self._topological_sort_randomized(middle)
        return [start] + individual + [end]

    def _topological_sort_randomized(self, vertices: List[str]) -> List[str]:
        """Рандомизированная топологическая сортировка"""
        result = []
        remaining = set(vertices)
        visited_set = {self.start_id}  # введение уже "посещено"

        while remaining:
            # Находим вершины, доступные для добавления
            available = [
                v for v in remaining
                if all(prereq in visited_set for prereq in self.dependencies.get(v, []))
            ]

            if not available:
                # Цикл или ошибка - добавляем любую
                available = list(remaining)

            # Случайный выбор среди доступных
            chosen = random.choice(available)
            result.append(chosen)
            visited_set.add(chosen)
            remaining.remove(chosen)

        return result

    def fitness(self, individual: List[str]) -> float:
        """Функция приспособленности"""
        cost = 0

        # Стоимость пути
        for i in range(len(individual) - 1):
            from_idx = self.id_to_index[individual[i]]
            to_idx = self.id_to_index[individual[i+1]]
            cost += self.distance_matrix[from_idx][to_idx]

        # Штраф за нарушение зависимостей
        penalty = 0
        for idx, ch_id in enumerate(individual):
            for prereq in self.dependencies.get(ch_id, []):
                if prereq not in individual[:idx]:
                    penalty += 1000

        return cost + penalty

    def tournament_selection(self, population: List, tournament_size: int = 5):
        """Турнирная селекция"""
        tournament = random.sample(population, tournament_size)
        return min(tournament, key=self.fitness)

    def order_crossover(self, parent1: List[str], parent2: List[str]) -> List[str]:
        """
        Упорядоченный кроссовер (Order Crossover, OX)

        Сохраняет относительный порядок элементов
        """
        size = len(parent1)

        # Выбираем сегмент
        start, end = sorted(random.sample(range(1, size-1), 2))

        # Копируем сегмент от parent1
        child = [None] * size
        child[0], child[-1] = parent1[0], parent1[-1]
        child[start:end] = parent1[start:end]

        # Заполняем остальное из parent2, сохраняя порядок
        parent2_genes = [g for g in parent2 if g not in child]

        idx = 1
        for gene in parent2_genes:
            while idx < size - 1 and child[idx] is not None:
                idx += 1
            if idx < size - 1:
                child[idx] = gene
                idx += 1

        return child

    def pmx_crossover(self, parent1: List[str], parent2: List[str]) -> List[str]:
        """
        Partially Mapped Crossover (PMX)

        Более сложный кроссовер, сохраняющий больше информации от родителей
        """
        size = len(parent1)
        start, end = sorted(random.sample(range(1, size-1), 2))

        child = [None] * size
        child[0], child[-1] = parent1[0], parent1[-1]

        # Копируем сегмент
        child[start:end] = parent1[start:end]

        # Маппинг
        mapping = {}
        for i in range(start, end):
            mapping[parent2[i]] = parent1[i]

        # Заполняем остальное
        for i in range(1, size - 1):
            if child[i] is None:
                gene = parent2[i]

                # Следуем цепочке маппинга
                while gene in child[start:end]:
                    gene = mapping.get(gene, gene)

                child[i] = gene

        return child

    def swap_mutation(self, individual: List[str]) -> List[str]:
        """Мутация: обмен двух элементов"""
        mutated = individual.copy()
        i, j = random.sample(range(1, len(mutated)-1), 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
        return mutated

    def inversion_mutation(self, individual: List[str]) -> List[str]:
        """Мутация: обращение сегмента"""
        mutated = individual.copy()
        i, j = sorted(random.sample(range(1, len(mutated)-1), 2))
        mutated[i:j+1] = reversed(mutated[i:j+1])
        return mutated

    def scramble_mutation(self, individual: List[str]) -> List[str]:
        """Мутация: перемешивание сегмента"""
        mutated = individual.copy()
        i, j = sorted(random.sample(range(1, len(mutated)-1), 2))

        segment = mutated[i:j+1]
        random.shuffle(segment)
        mutated[i:j+1] = segment

        return mutated

    def is_valid(self, individual: List[str]) -> bool:
        """Проверка валидности особи"""
        for idx, ch_id in enumerate(individual):
            for prereq in self.dependencies.get(ch_id, []):
                if prereq not in individual[:idx]:
                    return False
        return True

    def repair(self, individual: List[str]) -> List[str]:
        """Починка невалидной особи"""
        # Если валидна, возвращаем как есть
        if self.is_valid(individual):
            return individual

        # Иначе создаем новую валидную особь
        return self.create_individual()

    def evolve(self, generations: int = 500, verbose: bool = True) -> Tuple[List[str], float]:
        """
        Основной цикл эволюции

        Returns:
        --------
        best_individual: лучшая особь
        best_fitness: её приспособленность
        """
        # Инициализация популяции
        population = [self.create_individual() for _ in range(self.pop_size)]

        best_individual = min(population, key=self.fitness)
        best_fitness = self.fitness(best_individual)

        fitness_history = []

        for gen in range(generations):
            new_population = []

            # Элитизм
            elite = sorted(population, key=self.fitness)[:self.elite_size]
            new_population.extend(elite)

            # Создание новых особей
            while len(new_population) < self.pop_size:
                # Селекция
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)

                # Кроссовер
                if random.random() < self.crossover_rate:
                    # Выбираем тип кроссовера
                    if random.random() < 0.5:
                        child = self.order_crossover(parent1, parent2)
                    else:
                        child = self.pmx_crossover(parent1, parent2)
                else:
                    child = parent1.copy()

                # Мутация
                if random.random() < self.mutation_rate:
                    mutation_type = random.choice(['swap', 'inversion', 'scramble'])

                    if mutation_type == 'swap':
                        child = self.swap_mutation(child)
                    elif mutation_type == 'inversion':
                        child = self.inversion_mutation(child)
                    else:
                        child = self.scramble_mutation(child)

                # Починка, если невалидна
                child = self.repair(child)

                new_population.append(child)

            population = new_population

            # Обновление лучшего
            current_best = min(population, key=self.fitness)
            current_fitness = self.fitness(current_best)

            if current_fitness < best_fitness:
                best_individual = current_best
                best_fitness = current_fitness

                if verbose:
                    print(f"Generation {gen}: New best fitness = {best_fitness:.2f}")

            fitness_history.append(best_fitness)

        if verbose:
            print(f"\n✅ Evolution completed!")
            print(f"Best fitness: {best_fitness:.2f}")

        return best_individual, best_fitness


# ============================================================================
# MULTI-OBJECTIVE OPTIMIZATION
# ============================================================================

class MultiObjectiveOptimizer:
    """Многокритериальная оптимизация структуры диссертации"""

    def __init__(self, optimizer):
        """
        Parameters:
        -----------
        optimizer: экземпляр DissertationOptimizer
        """
        self.optimizer = optimizer

    def compute_objectives(self, path: List[str]) -> Dict[str, float]:
        """
        Вычисляет несколько целевых функций

        Returns:
        --------
        objectives: словарь {название: значение}
        """
        objectives = {}

        # 1. Когнитивная стоимость (минимизируем)
        objectives['cognitive_cost'] = self.optimizer.path_cost(path)

        # 2. Время написания (минимизируем)
        total_time = sum(
            self.optimizer._estimate_writing_time(self.optimizer.chapters[ch_id])
            for ch_id in path
        )
        objectives['writing_time'] = total_time

        # 3. Нарушения зависимостей (минимизируем)
        violations = 0
        for idx, ch_id in enumerate(path):
            chapter = self.optimizer.chapters[ch_id]
            for prereq in chapter.prerequisites:
                if prereq not in path[:idx]:
                    violations += 1
        objectives['dependency_violations'] = violations

        # 4. Связность (максимизируем -> минимизируем отрицание)
        coherence = self.optimizer.evaluate_structure(path)['coherence']
        objectives['coherence'] = -coherence  # инвертируем для минимизации

        return objectives

    def pareto_dominates(self, obj1: Dict, obj2: Dict) -> bool:
        """
        Проверяет, доминирует ли obj1 над obj2 по Парето

        obj1 доминирует obj2, если:
        - obj1 не хуже obj2 по всем критериям
        - obj1 лучше obj2 хотя бы по одному критерию
        """
        better_in_some = False
        for key in obj1.keys():
            if obj1[key] > obj2[key]:
                return False  # obj1 хуже по этому критерию
            if obj1[key] < obj2[key]:
                better_in_some = True

        return better_in_some

    def find_pareto_front(self, solutions: List[List[str]]) -> List[List[str]]:
        """
        Находит Парето-фронт среди решений

        Returns:
        --------
        pareto_front: список недоминируемых решений
        """
        objectives = [self.compute_objectives(sol) for sol in solutions]

        pareto_front = []

        for i, sol in enumerate(solutions):
            dominated = False

            for j, other_sol in enumerate(solutions):
                if i != j and self.pareto_dominates(objectives[j], objectives[i]):
                    dominated = True
                    break

            if not dominated:
                pareto_front.append(sol)

        return pareto_front

    def nsga2_optimize(self,
                      population_size: int = 100,
                      generations: int = 300) -> List[List[str]]:
        """
        NSGA-II (Non-dominated Sorting Genetic Algorithm II)

        Возвращает Парето-фронт решений

        Returns:
        --------
        pareto_front: список оптимальных по Парето решений
        """
        print("Running NSGA-II multi-objective optimization...")

        # Инициализация популяции
        population = []
        for _ in range(population_size):
            path, _ = self.optimizer.greedy_solution()
            # Добавляем вариации
            path_variant = self.optimizer._generate_neighbor(path) or path
            population.append(path_variant)

        for gen in range(generations):
            # Вычисляем objectives для всех
            all_objectives = [self.compute_objectives(sol) for sol in population]

            # Non-dominated sorting
            fronts = self._fast_non_dominated_sort(population, all_objectives)

            # Создаем новую популяцию
            new_population = []

            for front in fronts:
                if len(new_population) + len(front) <= population_size:
                    new_population.extend(front)
                else:
                    # Добавляем только часть фронта (по crowding distance)
                    remaining = population_size - len(new_population)
                    sorted_front = self._crowding_distance_sort(front, all_objectives)
                    new_population.extend(sorted_front[:remaining])
                    break

            # Эволюция
            offspring = []
            while len(offspring) < population_size:
                parent1, parent2 = random.sample(new_population, 2)

                # Кроссовер (простой: обмен сегментами)
                child = self._simple_crossover(parent1, parent2)

                # Мутация
                if random.random() < 0.2:
                    child = self.optimizer._generate_neighbor(child) or child

                offspring.append(child)

            population = new_population + offspring

            if gen % 50 == 0:
                print(f"Generation {gen}: Population size = {len(population)}")

        # Финальный Парето-фронт
        pareto_front = self.find_pareto_front(population)

        print(f"✅ NSGA-II completed. Pareto front size: {len(pareto_front)}")

        return pareto_front

    def _fast_non_dominated_sort(self, population, objectives):
        """Быстрая недоминируемая сортировка"""
        fronts = [[]]
        domination_count = [0] * len(population)
        dominated_solutions = [[] for _ in range(len(population))]

        for i in range(len(population)):
            for j in range(len(population)):
                if i != j:
                    if self.pareto_dominates(objectives[i], objectives[j]):
                        dominated_solutions[i].append(j)
                    elif self.pareto_dominates(objectives[j], objectives[i]):
                        domination_count[i] += 1

            if domination_count[i] == 0:
                fronts[0].append(population[i])

        # Построение остальных фронтов
        i = 0
        while fronts[i]:
            next_front = []

            for sol_idx in range(len(population)):
                if population[sol_idx] in fronts[i]:
                    for dominated_idx in dominated_solutions[sol_idx]:
                        domination_count[dominated_idx] -= 1
                        if domination_count[dominated_idx] == 0:
                            next_front.append(population[dominated_idx])

            i += 1
            if next_front:
                fronts.append(next_front)

        return fronts

    def _crowding_distance_sort(self, front, all_objectives):
        """Сортировка по crowding distance"""
        # Упрощенная версия
        return front

    def _simple_crossover(self, parent1, parent2):
        """Простой кроссовер для многокритериальной оптимизации"""
        size = len(parent1)
        cut = random.randint(1, size - 2)

        child = parent1[:cut] + [g for g in parent2 if g not in parent1[:cut]]

        # Валидация
        if self.optimizer.is_valid_path(child):
            return child
        else:
            return parent1


# ============================================================================
# ADAPTIVE LEARNING
# ============================================================================

class AdaptiveLearningOptimizer:
    """
    Адаптивная система, обучающаяся в процессе написания

    Идея: по мере написания диссертации система корректирует оценки дистанций
    """

    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.writing_history = []  # история написания
        self.actual_difficulties = {}  # реальные сложности переходов
        self.learning_rate = 0.1

    def record_writing_session(self,
                               from_chapter: str,
                               to_chapter: str,
                               actual_difficulty: float):
        """
        Записывает реальную сложность перехода

        Parameters:
        -----------
        from_chapter: ID главы, с которой переходим
        to_chapter: ID главы, на которую переходим
        actual_difficulty: реальная сложность (0-1)
        """
        self.writing_history.append({
            'from': from_chapter,
            'to': to_chapter,
            'difficulty': actual_difficulty
        })

        # Обновляем оценки
        self._update_distance_estimate(from_chapter, to_chapter, actual_difficulty)

    def _update_distance_estimate(self, from_ch, to_ch, actual_diff):
        """Обновляет оценку дистанции на основе реального опыта"""
        from_idx = self.optimizer.id_to_index[from_ch]
        to_idx = self.optimizer.id_to_index[to_ch]

        # Текущая оценка
        current_estimate = self.optimizer.distance_matrix[from_idx][to_idx]

        # Обновление по правилу скользящего среднего
        new_estimate = (1 - self.learning_rate) * current_estimate + \
                       self.learning_rate * actual_diff

        self.optimizer.distance_matrix[from_idx][to_idx] = new_estimate

    def reoptimize(self, remaining_chapters: List[str]):
        """
        Переоптимизирует структуру для оставшихся глав

        Parameters:
        -----------
        remaining_chapters: главы, которые еще не написаны
        """
        print(f"Переоптимизация для {len(remaining_chapters)} оставшихся глав...")

        # Создаем подзадачу
        # (в реальности нужно создать новый оптимизатор с подмножеством глав)

        # Запускаем оптимизацию
        path, cost = self.optimizer.optimize(method='simulated_annealing')

        print(f"Новая оптимальная структура найдена, стоимость: {cost:.2f}")

        return path


if __name__ == "__main__":
    print("Advanced Methods - Demo")
    print("=" * 60)

    # Для демонстрации нужен базовый оптимизатор
    print("\n⚠ Запустите этот модуль вместе с dissertation_optimizer.py")
    print("Пример использования в практических руководствах.")
