"""
Dissertation Structure Optimizer using TSP algorithms
Оптимизатор структуры диссертации с использованием алгоритмов TSP

Author: AI Research Assistant
Date: 2026-02-04
"""

import numpy as np
import random
import math
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class Chapter:
    """Представление главы/раздела диссертации"""
    id: str
    title: str
    content: str = ""
    word_count: int = 0
    novelty: float = 0.5  # [0, 1]: 0=обзор, 1=новые эксперименты
    complexity: float = 0.5  # [0, 1]: 0=простое, 1=сложное
    keywords: List[str] = None
    prerequisites: List[str] = None  # IDs глав-предпосылок
    epoch: int = 2  # Временной период: 0=древность, 1=средние века, 2=современность

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.prerequisites is None:
            self.prerequisites = []

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class DissertationOptimizer:
    """
    Основной класс для оптимизации структуры диссертации
    """

    def __init__(self,
                 chapters: List[Chapter],
                 start_chapter_id: str,
                 end_chapter_id: str,
                 weights: Dict[str, float] = None):
        """
        Parameters:
        -----------
        chapters: список глав
        start_chapter_id: ID введения (обязательно первым)
        end_chapter_id: ID заключения (обязательно последним)
        weights: веса для компонент когнитивной дистанции
        """
        self.chapters = {ch.id: ch for ch in chapters}
        self.start_id = start_chapter_id
        self.end_id = end_chapter_id

        # Веса по умолчанию
        self.weights = weights or {
            'semantic': 0.4,
            'temporal': 0.2,
            'logical': 0.3,
            'stylistic': 0.1
        }

        # Матрица дистанций
        self.distance_matrix = None
        self._compute_distance_matrix()

        # Граф зависимостей
        self.dependency_graph = self._build_dependency_graph()

    def _compute_distance_matrix(self):
        """Вычисляет матрицу когнитивных дистанций между всеми главами"""
        n = len(self.chapters)
        chapter_ids = list(self.chapters.keys())

        self.distance_matrix = np.zeros((n, n))
        self.id_to_index = {ch_id: i for i, ch_id in enumerate(chapter_ids)}
        self.index_to_id = {i: ch_id for ch_id, i in self.id_to_index.items()}

        for i, ch_id1 in enumerate(chapter_ids):
            for j, ch_id2 in enumerate(chapter_ids):
                if i == j:
                    self.distance_matrix[i][j] = 0
                else:
                    ch1 = self.chapters[ch_id1]
                    ch2 = self.chapters[ch_id2]

                    d_sem = self._semantic_distance(ch1, ch2)
                    d_temp = self._temporal_distance(ch1, ch2)
                    d_log = self._logical_distance(ch1, ch2)
                    d_style = self._stylistic_distance(ch1, ch2)

                    total_dist = (
                        self.weights['semantic'] * d_sem +
                        self.weights['temporal'] * d_temp +
                        self.weights['logical'] * d_log +
                        self.weights['stylistic'] * d_style
                    )

                    self.distance_matrix[i][j] = total_dist

    def _semantic_distance(self, ch1: Chapter, ch2: Chapter) -> float:
        """
        Семантическое расстояние на основе ключевых слов (упрощенная версия)

        В полной реализации используйте:
        - TF-IDF векторы
        - Word embeddings (Word2Vec, GloVe)
        - BERT embeddings
        """
        kw1 = set(ch1.keywords)
        kw2 = set(ch2.keywords)

        if not kw1 or not kw2:
            return 0.5  # нейтральное расстояние

        # Jaccard distance
        intersection = len(kw1 & kw2)
        union = len(kw1 | kw2)

        jaccard_sim = intersection / union if union > 0 else 0
        jaccard_dist = 1 - jaccard_sim

        return jaccard_dist

    def _temporal_distance(self, ch1: Chapter, ch2: Chapter) -> float:
        """Временное расстояние (разница в исторических периодах)"""
        max_epoch_diff = 2  # максимальная разница
        epoch_diff = abs(ch1.epoch - ch2.epoch)

        return epoch_diff / max_epoch_diff if max_epoch_diff > 0 else 0

    def _logical_distance(self, ch1: Chapter, ch2: Chapter) -> float:
        """
        Логическое расстояние на основе графа зависимостей

        Использует BFS для нахождения кратчайшего пути
        """
        # Проверка прямой зависимости
        if ch2.id in ch1.prerequisites:
            return 0.0  # ch2 -> ch1 прямая зависимость

        if ch1.id in ch2.prerequisites:
            return 1.0  # ch1 -> ch2 обратная зависимость (плохо, если ch2 идет после ch1)

        # BFS для поиска кратчайшего пути
        path_length = self._bfs_distance(ch1.id, ch2.id)

        # Нормализация
        max_diameter = len(self.chapters)
        normalized_dist = path_length / max_diameter if max_diameter > 0 else 0.5

        return min(normalized_dist, 1.0)

    def _stylistic_distance(self, ch1: Chapter, ch2: Chapter) -> float:
        """
        Стилистическое расстояние (разница в сложности)

        В полной реализации используйте метрики читаемости:
        - Flesch-Kincaid Grade Level
        - SMOG Index
        - Automated Readability Index
        """
        complexity_diff = abs(ch1.complexity - ch2.complexity)
        return complexity_diff

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Строит граф зависимостей (adjacency list)"""
        graph = defaultdict(set)

        for ch_id, chapter in self.chapters.items():
            for prereq_id in chapter.prerequisites:
                # prereq_id -> ch_id (prereq должен быть раньше)
                graph[prereq_id].add(ch_id)

        return graph

    def _bfs_distance(self, from_id: str, to_id: str) -> int:
        """BFS для нахождения кратчайшего пути в графе зависимостей"""
        if from_id == to_id:
            return 0

        from collections import deque

        queue = deque([(from_id, 0)])
        visited = {from_id}

        while queue:
            current, dist = queue.popleft()

            for neighbor in self.dependency_graph.get(current, []):
                if neighbor == to_id:
                    return dist + 1

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

        # Нет пути
        return len(self.chapters)  # максимальная дистанция

    def is_valid_path(self, path: List[str]) -> bool:
        """Проверяет, что путь удовлетворяет всем зависимостям"""
        for idx, ch_id in enumerate(path):
            chapter = self.chapters[ch_id]

            for prereq_id in chapter.prerequisites:
                if prereq_id not in path[:idx]:
                    return False

        return True

    def path_cost(self, path: List[str]) -> float:
        """Вычисляет стоимость пути"""
        total_cost = 0

        for i in range(len(path) - 1):
            from_idx = self.id_to_index[path[i]]
            to_idx = self.id_to_index[path[i+1]]
            total_cost += self.distance_matrix[from_idx][to_idx]

        return total_cost

    def greedy_solution(self) -> Tuple[List[str], float]:
        """
        Жадный алгоритм: выбираем ближайшую допустимую главу

        Returns:
        --------
        path: оптимизированный порядок глав (IDs)
        cost: стоимость пути
        """
        path = [self.start_id]
        remaining = set(self.chapters.keys()) - {self.start_id, self.end_id}
        current = self.start_id

        while remaining:
            best_next = None
            best_dist = float('inf')

            for ch_id in remaining:
                # Проверка зависимостей
                chapter = self.chapters[ch_id]
                prereqs_satisfied = all(
                    prereq in path for prereq in chapter.prerequisites
                )

                if not prereqs_satisfied:
                    continue

                from_idx = self.id_to_index[current]
                to_idx = self.id_to_index[ch_id]
                dist = self.distance_matrix[from_idx][to_idx]

                if dist < best_dist:
                    best_next = ch_id
                    best_dist = dist

            if best_next is None:
                # Тупик: выбираем любую вершину (с штрафом)
                best_next = random.choice(list(remaining))

            path.append(best_next)
            remaining.remove(best_next)
            current = best_next

        path.append(self.end_id)
        cost = self.path_cost(path)

        return path, cost

    def two_opt_optimize(self, path: List[str], max_iterations: int = 1000) -> Tuple[List[str], float]:
        """
        2-opt локальная оптимизация

        Parameters:
        -----------
        path: начальный путь
        max_iterations: максимум итераций

        Returns:
        --------
        optimized_path: улучшенный путь
        cost: стоимость пути
        """
        current_path = path.copy()
        current_cost = self.path_cost(current_path)

        improved = True
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1

            for i in range(1, len(current_path) - 2):
                for j in range(i + 1, len(current_path) - 1):
                    # Проверка зависимостей после обращения
                    new_path = current_path.copy()
                    new_path[i:j+1] = reversed(new_path[i:j+1])

                    if not self.is_valid_path(new_path):
                        continue

                    new_cost = self.path_cost(new_path)

                    if new_cost < current_cost:
                        current_path = new_path
                        current_cost = new_cost
                        improved = True
                        break

                if improved:
                    break

        return current_path, current_cost

    def simulated_annealing(self,
                           initial_temp: float = 1000,
                           cooling_rate: float = 0.95,
                           max_iterations: int = 10000) -> Tuple[List[str], float]:
        """
        Имитация отжига

        Parameters:
        -----------
        initial_temp: начальная температура
        cooling_rate: скорость охлаждения (0 < alpha < 1)
        max_iterations: максимум итераций

        Returns:
        --------
        best_path: оптимизированный путь
        best_cost: стоимость пути
        """
        # Начальное решение (жадный алгоритм)
        current_path, current_cost = self.greedy_solution()

        best_path = current_path.copy()
        best_cost = current_cost

        temp = initial_temp

        for iteration in range(max_iterations):
            # Генерация соседа
            neighbor = self._generate_neighbor(current_path)

            if neighbor is None:
                continue

            neighbor_cost = self.path_cost(neighbor)

            # Принятие решения
            delta = neighbor_cost - current_cost

            if delta < 0:
                # Улучшение - всегда принимаем
                current_path = neighbor
                current_cost = neighbor_cost

                if current_cost < best_cost:
                    best_path = current_path.copy()
                    best_cost = current_cost
            else:
                # Ухудшение - принимаем с вероятностью
                acceptance_prob = math.exp(-delta / temp) if temp > 0 else 0

                if random.random() < acceptance_prob:
                    current_path = neighbor
                    current_cost = neighbor_cost

            # Охлаждение
            temp *= cooling_rate

            if temp < 0.01:
                break

        return best_path, best_cost

    def _generate_neighbor(self, path: List[str]) -> Optional[List[str]]:
        """Генерирует соседнее решение"""
        neighbor = path.copy()

        # Стратегии: swap, reversal, insert
        strategy = random.choice(['swap', 'reversal', 'insert'])

        # Исключаем первый и последний элементы (введение и заключение)
        movable_indices = list(range(1, len(path) - 1))

        if len(movable_indices) < 2:
            return None

        for attempt in range(10):  # попыток найти валидного соседа
            try:
                if strategy == 'swap':
                    i, j = random.sample(movable_indices, 2)
                    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

                elif strategy == 'reversal':
                    i, j = sorted(random.sample(movable_indices, 2))
                    neighbor[i:j+1] = reversed(neighbor[i:j+1])

                elif strategy == 'insert':
                    i = random.choice(movable_indices)
                    j = random.choice(movable_indices)
                    element = neighbor.pop(i)
                    neighbor.insert(j, element)

                # Проверка валидности
                if self.is_valid_path(neighbor):
                    return neighbor
                else:
                    neighbor = path.copy()  # сброс для новой попытки

            except:
                continue

        return None

    def optimize(self, method: str = 'simulated_annealing', **kwargs) -> Tuple[List[str], float]:
        """
        Главный метод оптимизации

        Parameters:
        -----------
        method: 'greedy', 'two_opt', 'simulated_annealing'
        **kwargs: параметры для конкретного метода

        Returns:
        --------
        optimal_path: оптимизированный порядок глав
        optimal_cost: стоимость пути
        """
        if method == 'greedy':
            return self.greedy_solution()

        elif method == 'two_opt':
            # Сначала жадное, потом 2-opt
            initial_path, _ = self.greedy_solution()
            return self.two_opt_optimize(initial_path, **kwargs)

        elif method == 'simulated_annealing':
            return self.simulated_annealing(**kwargs)

        else:
            raise ValueError(f"Unknown method: {method}")

    def evaluate_structure(self, path: List[str]) -> Dict[str, float]:
        """
        Оценка качества структуры по различным метрикам

        Returns:
        --------
        metrics: словарь метрик
        """
        metrics = {}

        # 1. Когнитивная стоимость
        metrics['cognitive_cost'] = self.path_cost(path)

        # 2. Количество нарушений зависимостей
        violations = 0
        for idx, ch_id in enumerate(path):
            chapter = self.chapters[ch_id]
            for prereq_id in chapter.prerequisites:
                if prereq_id not in path[:idx]:
                    violations += 1
        metrics['dependency_violations'] = violations

        # 3. Coherence score (средняя схожесть соседних глав)
        coherence_scores = []
        for i in range(len(path) - 1):
            from_idx = self.id_to_index[path[i]]
            to_idx = self.id_to_index[path[i+1]]

            # Similarity = 1 - distance
            similarity = 1 - self.distance_matrix[from_idx][to_idx]
            coherence_scores.append(similarity)

        metrics['coherence'] = np.mean(coherence_scores) if coherence_scores else 0

        # 4. Reader complexity (нагрузка на память)
        memory_loads = []
        for idx, ch_id in enumerate(path):
            chapter = self.chapters[ch_id]

            max_distance = 0
            for prereq_id in chapter.prerequisites:
                if prereq_id in path[:idx]:
                    distance = idx - path.index(prereq_id)
                    max_distance = max(max_distance, distance)

            memory_load = max_distance / len(path) if path else 0
            memory_loads.append(memory_load)

        metrics['reader_complexity'] = np.mean(memory_loads) if memory_loads else 0

        # 5. Estimated writing time
        total_time = 0
        for ch_id in path:
            chapter = self.chapters[ch_id]
            time = self._estimate_writing_time(chapter)
            total_time += time

        metrics['estimated_hours'] = total_time

        return metrics

    def _estimate_writing_time(self, chapter: Chapter) -> float:
        """Оценка времени написания главы в часах"""
        alpha = 0.01  # час/слово
        beta = 50     # бонус за новизну
        gamma = 30    # бонус за сложность
        delta = 20    # базовая стоимость

        word_count = chapter.word_count if chapter.word_count > 0 else 5000  # по умолчанию

        hours = (
            alpha * word_count +
            beta * chapter.novelty +
            gamma * chapter.complexity +
            delta
        )

        return hours

    def export_results(self, path: List[str], filename: str):
        """Экспорт результатов в JSON"""
        results = {
            'optimal_path': path,
            'chapter_details': [
                {
                    'id': ch_id,
                    'title': self.chapters[ch_id].title,
                    'position': idx + 1
                }
                for idx, ch_id in enumerate(path)
            ],
            'metrics': self.evaluate_structure(path),
            'distance_matrix': self.distance_matrix.tolist(),
            'dependencies': {
                ch_id: ch.prerequisites
                for ch_id, ch in self.chapters.items()
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results exported to {filename}")

    def print_solution(self, path: List[str]):
        """Красивый вывод решения"""
        print("\n" + "="*80)
        print("ОПТИМИЗИРОВАННАЯ СТРУКТУРА ДИССЕРТАЦИИ")
        print("="*80)

        metrics = self.evaluate_structure(path)

        print("\n📊 Метрики качества структуры:")
        print(f"  • Когнитивная стоимость: {metrics['cognitive_cost']:.2f}")
        print(f"  • Связность (coherence): {metrics['coherence']:.2%}")
        print(f"  • Сложность для читателя: {metrics['reader_complexity']:.2%}")
        print(f"  • Нарушения зависимостей: {metrics['dependency_violations']}")
        print(f"  • Оценка времени написания: {metrics['estimated_hours']:.0f} часов")

        print("\n📚 Оптимальный порядок глав:")
        for idx, ch_id in enumerate(path, 1):
            chapter = self.chapters[ch_id]
            prereqs = ", ".join(chapter.prerequisites) if chapter.prerequisites else "нет"
            print(f"  {idx}. {chapter.title}")
            print(f"     ID: {ch_id} | Предпосылки: {prereqs}")

        print("\n" + "="*80)


# Вспомогательные функции

def create_sample_dissertation() -> Tuple[List[Chapter], str, str]:
    """Создает пример диссертации для тестирования"""
    chapters = [
        Chapter(
            id="intro",
            title="Введение",
            word_count=3000,
            novelty=0.3,
            complexity=0.2,
            keywords=["мотивация", "цели", "задачи", "актуальность"],
            prerequisites=[],
            epoch=2
        ),
        Chapter(
            id="literature",
            title="Обзор литературы",
            word_count=15000,
            novelty=0.1,
            complexity=0.4,
            keywords=["предыдущие исследования", "методы", "теория", "анализ"],
            prerequisites=["intro"],
            epoch=2
        ),
        Chapter(
            id="theory",
            title="Теоретические основы",
            word_count=12000,
            novelty=0.5,
            complexity=0.7,
            keywords=["теория", "модель", "математика", "формализация"],
            prerequisites=["literature"],
            epoch=2
        ),
        Chapter(
            id="methodology",
            title="Методология исследования",
            word_count=10000,
            novelty=0.7,
            complexity=0.6,
            keywords=["методы", "эксперимент", "дизайн", "процедура"],
            prerequisites=["theory"],
            epoch=2
        ),
        Chapter(
            id="experiments",
            title="Экспериментальная часть",
            word_count=18000,
            novelty=0.9,
            complexity=0.8,
            keywords=["эксперименты", "данные", "результаты", "анализ"],
            prerequisites=["methodology"],
            epoch=2
        ),
        Chapter(
            id="results",
            title="Результаты и обсуждение",
            word_count=14000,
            novelty=0.8,
            complexity=0.7,
            keywords=["результаты", "обсуждение", "интерпретация", "выводы"],
            prerequisites=["experiments"],
            epoch=2
        ),
        Chapter(
            id="applications",
            title="Практические применения",
            word_count=8000,
            novelty=0.6,
            complexity=0.5,
            keywords=["применение", "практика", "внедрение", "эффект"],
            prerequisites=["results"],
            epoch=2
        ),
        Chapter(
            id="conclusion",
            title="Заключение",
            word_count=4000,
            novelty=0.2,
            complexity=0.3,
            keywords=["выводы", "результаты", "перспективы", "значимость"],
            prerequisites=["results", "applications"],
            epoch=2
        )
    ]

    return chapters, "intro", "conclusion"


if __name__ == "__main__":
    print("Dissertation Structure Optimizer - Demo\n")

    # Создание примера диссертации
    chapters, start, end = create_sample_dissertation()

    # Инициализация оптимизатора
    optimizer = DissertationOptimizer(chapters, start, end)

    print("1. Жадный алгоритм...")
    greedy_path, greedy_cost = optimizer.optimize(method='greedy')
    print(f"   Стоимость: {greedy_cost:.2f}")

    print("\n2. 2-opt оптимизация...")
    two_opt_path, two_opt_cost = optimizer.optimize(method='two_opt')
    print(f"   Стоимость: {two_opt_cost:.2f}")
    print(f"   Улучшение: {((greedy_cost - two_opt_cost) / greedy_cost * 100):.1f}%")

    print("\n3. Simulated Annealing...")
    sa_path, sa_cost = optimizer.optimize(
        method='simulated_annealing',
        initial_temp=1000,
        cooling_rate=0.95,
        max_iterations=5000
    )
    print(f"   Стоимость: {sa_cost:.2f}")
    print(f"   Улучшение от жадного: {((greedy_cost - sa_cost) / greedy_cost * 100):.1f}%")

    # Вывод лучшего решения
    best_path = min([
        (greedy_path, greedy_cost),
        (two_opt_path, two_opt_cost),
        (sa_path, sa_cost)
    ], key=lambda x: x[1])

    optimizer.print_solution(best_path[0])

    # Экспорт
    optimizer.export_results(best_path[0], 'dissertation_structure_optimal.json')
