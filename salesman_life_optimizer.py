"""
Salesman Life Optimizer - Система оптимизации жизни коммивояжера

Применение методов рационализации знаний и TSP оптимизации
к многомерной оптимизации жизни коммивояжера:
- Физическая: маршруты между городами
- Когнитивная: последовательность обучения
- Социальная: построение сети контактов
- Финансовая: оптимизация доходов
- Временная: распределение времени
- Карьерная: путь профессионального развития

Author: AI Research Assistant
Date: 2026-02-04
"""

from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import math

# Импорт наших систем
try:
    from dissertation_optimizer import DissertationOptimizer, Chapter
    from knowledge_transformer import KnowledgeGraph, Concept, Relation, KnowledgeRationalizer
    HAS_OPTIMIZERS = True
except ImportError:
    HAS_OPTIMIZERS = False

# Optional numpy
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    class np:
        @staticmethod
        def mean(lst):
            return sum(lst) / len(lst) if lst else 0


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class LifeState:
    """Состояние жизни коммивояжера в определенный момент"""
    id: str
    name: str

    # Физическое измерение
    location: str = ""  # город
    position: Tuple[float, float] = (0.0, 0.0)  # координаты

    # Когнитивное измерение
    skills: Dict[str, float] = field(default_factory=dict)  # навык: уровень (0-1)
    knowledge: Dict[str, float] = field(default_factory=dict)  # область: экспертиза

    # Социальное измерение
    contacts: List[str] = field(default_factory=list)  # список контактов
    network_quality: float = 0.5  # качество сети (0-1)

    # Финансовое измерение
    income: float = 0.0  # доход в год
    savings: float = 0.0  # накопления
    expenses: float = 0.0  # расходы

    # Временное измерение
    age: int = 25  # возраст
    experience_years: float = 0.0  # опыт работы

    # Качество жизни
    satisfaction: float = 0.5  # удовлетворенность (0-1)
    energy: float = 1.0  # энергия (0-1)
    stress: float = 0.3  # стресс (0-1)
    health: float = 0.9  # здоровье (0-1)

    # Метаданные
    timestamp: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class Transition:
    """Переход между состояниями жизни"""
    source: str  # ID исходного состояния
    target: str  # ID целевого состояния

    # Стоимости перехода
    time_cost: float = 0.0  # время (месяцы)
    money_cost: float = 0.0  # финансовые затраты
    energy_cost: float = 0.0  # затраты энергии
    stress_cost: float = 0.0  # уровень стресса

    # Выгоды перехода
    skill_gain: Dict[str, float] = field(default_factory=dict)
    income_gain: float = 0.0
    network_gain: int = 0
    satisfaction_gain: float = 0.0

    # Требования
    prerequisites: List[str] = field(default_factory=list)
    min_skills: Dict[str, float] = field(default_factory=dict)

    # Метаданные
    type: str = "career"  # career, learning, relocation, etc.
    description: str = ""


@dataclass
class CareerGoal:
    """Карьерная цель"""
    name: str
    target_income: float = 100000
    target_satisfaction: float = 0.8
    target_skills: Dict[str, float] = field(default_factory=dict)
    target_network_size: int = 500
    deadline: float = 10.0  # лет
    priority: float = 1.0  # приоритет (0-1)


# ============================================================================
# LIFE GRAPH
# ============================================================================

class LifeGraph:
    """Граф жизни коммивояжера"""

    def __init__(self):
        self.states: Dict[str, LifeState] = {}
        self.transitions: List[Transition] = []
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)

    def add_state(self, state: LifeState):
        """Добавить состояние"""
        self.states[state.id] = state

    def add_transition(self, transition: Transition):
        """Добавить переход"""
        self.transitions.append(transition)
        self.adjacency[transition.source].add(transition.target)

    def get_transition(self, source_id: str, target_id: str) -> Optional[Transition]:
        """Получить переход между состояниями"""
        for t in self.transitions:
            if t.source == source_id and t.target == target_id:
                return t
        return None

    def get_neighbors(self, state_id: str) -> Set[str]:
        """Получить соседние состояния"""
        return self.adjacency.get(state_id, set())

    def compute_distance(self, s1: LifeState, s2: LifeState,
                        weights: Dict[str, float] = None) -> float:
        """
        Вычислить многомерную дистанцию между состояниями

        Parameters:
        -----------
        weights: веса компонент дистанции
            - spatial: физическое расстояние
            - cognitive: когнитивная сложность
            - social: социальная дистанция
            - financial: финансовые затраты
            - temporal: время перехода
        """
        if weights is None:
            weights = {
                'spatial': 0.15,
                'cognitive': 0.25,
                'social': 0.20,
                'financial': 0.25,
                'temporal': 0.15
            }

        # 1. Пространственная дистанция
        dx = s2.position[0] - s1.position[0]
        dy = s2.position[1] - s1.position[1]
        d_spatial = math.sqrt(dx*dx + dy*dy)

        # 2. Когнитивная дистанция (насколько разные навыки)
        all_skills = set(s1.skills.keys()) | set(s2.skills.keys())
        skill_diffs = []
        for skill in all_skills:
            v1 = s1.skills.get(skill, 0)
            v2 = s2.skills.get(skill, 0)
            skill_diffs.append(abs(v2 - v1))
        d_cognitive = np.mean(skill_diffs) if skill_diffs else 0

        # 3. Социальная дистанция
        contacts1 = set(s1.contacts)
        contacts2 = set(s2.contacts)
        if contacts1 or contacts2:
            common = len(contacts1 & contacts2)
            total = len(contacts1 | contacts2)
            similarity = common / total if total > 0 else 0
            d_social = 1 - similarity
        else:
            d_social = 0.5

        # 4. Финансовая дистанция
        d_financial = abs(s2.income - s1.income) / max(s1.income, 1000)

        # 5. Временная дистанция
        d_temporal = abs(s2.age - s1.age) / 40.0  # нормализуем к 40 годам

        # Взвешенная сумма
        distance = (weights['spatial'] * d_spatial +
                   weights['cognitive'] * d_cognitive +
                   weights['social'] * d_social +
                   weights['financial'] * d_financial +
                   weights['temporal'] * d_temporal)

        return distance


# ============================================================================
# CAREER PATH OPTIMIZER
# ============================================================================

class CareerPathOptimizer:
    """Оптимизация карьерного пути"""

    def __init__(self, life_graph: LifeGraph):
        self.graph = life_graph

    def optimize(self, start_state_id: str, goal: CareerGoal,
                method: str = 'greedy') -> Tuple[List[str], float]:
        """
        Найти оптимальный карьерный путь

        Parameters:
        -----------
        start_state_id: начальное состояние
        goal: целевое состояние/цель
        method: метод оптимизации

        Returns:
        --------
        path: последовательность состояний
        cost: суммарная стоимость пути
        """
        if method == 'greedy':
            return self._greedy_path(start_state_id, goal)
        elif method == 'dijkstra':
            return self._dijkstra_path(start_state_id, goal)
        elif method == 'astar':
            return self._astar_path(start_state_id, goal)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _greedy_path(self, start_id: str, goal: CareerGoal) -> Tuple[List[str], float]:
        """Жадный алгоритм построения пути"""
        path = [start_id]
        current_id = start_id
        total_cost = 0.0
        visited = {start_id}

        max_steps = 20  # предотвращаем бесконечные циклы

        for _ in range(max_steps):
            current_state = self.graph.states[current_id]

            # Проверяем достижение цели
            if self._is_goal_reached(current_state, goal):
                break

            # Ищем лучший следующий шаг
            neighbors = self.graph.get_neighbors(current_id)
            unvisited = [n for n in neighbors if n not in visited]

            if not unvisited:
                break

            # Выбираем наиболее перспективного соседа
            best_neighbor = None
            best_score = -float('inf')

            for neighbor_id in unvisited:
                neighbor_state = self.graph.states[neighbor_id]
                score = self._evaluate_state(neighbor_state, goal)

                if score > best_score:
                    best_score = score
                    best_neighbor = neighbor_id

            if best_neighbor is None:
                break

            # Переход
            transition = self.graph.get_transition(current_id, best_neighbor)
            if transition:
                total_cost += self._compute_transition_cost(transition)

            path.append(best_neighbor)
            visited.add(best_neighbor)
            current_id = best_neighbor

        return path, total_cost

    def _dijkstra_path(self, start_id: str, goal: CareerGoal) -> Tuple[List[str], float]:
        """Алгоритм Дейкстры для поиска оптимального пути"""
        distances = {start_id: 0.0}
        previous = {}
        unvisited = set(self.graph.states.keys())

        while unvisited:
            # Найти узел с минимальной дистанцией
            current = min(unvisited, key=lambda x: distances.get(x, float('inf')))

            if distances.get(current, float('inf')) == float('inf'):
                break

            current_state = self.graph.states[current]
            if self._is_goal_reached(current_state, goal):
                # Восстановить путь
                path = []
                node = current
                while node in previous:
                    path.append(node)
                    node = previous[node]
                path.append(start_id)
                path.reverse()
                return path, distances[current]

            unvisited.remove(current)

            # Обновить дистанции до соседей
            for neighbor in self.graph.get_neighbors(current):
                if neighbor in unvisited:
                    transition = self.graph.get_transition(current, neighbor)
                    if transition:
                        cost = self._compute_transition_cost(transition)
                        new_distance = distances[current] + cost

                        if new_distance < distances.get(neighbor, float('inf')):
                            distances[neighbor] = new_distance
                            previous[neighbor] = current

        # Если цель не достигнута, возвращаем лучший найденный путь
        if start_id in distances:
            return [start_id], distances[start_id]
        return [start_id], 0.0

    def _astar_path(self, start_id: str, goal: CareerGoal) -> Tuple[List[str], float]:
        """A* алгоритм с эвристикой"""
        # Упрощенная версия - можно расширить
        return self._dijkstra_path(start_id, goal)

    def _is_goal_reached(self, state: LifeState, goal: CareerGoal) -> bool:
        """Проверить достижение цели"""
        # Проверяем все критерии
        income_ok = state.income >= goal.target_income * 0.9
        satisfaction_ok = state.satisfaction >= goal.target_satisfaction * 0.9

        # Проверяем навыки
        skills_ok = True
        for skill, target_level in goal.target_skills.items():
            if state.skills.get(skill, 0) < target_level * 0.8:
                skills_ok = False
                break

        # Проверяем размер сети
        network_ok = len(state.contacts) >= goal.target_network_size * 0.8

        return income_ok and satisfaction_ok and skills_ok and network_ok

    def _evaluate_state(self, state: LifeState, goal: CareerGoal) -> float:
        """Оценить состояние относительно цели"""
        score = 0.0

        # Доход
        income_ratio = state.income / goal.target_income if goal.target_income > 0 else 0
        score += 0.3 * min(income_ratio, 1.0)

        # Удовлетворенность
        score += 0.2 * state.satisfaction

        # Навыки
        skill_scores = []
        for skill, target in goal.target_skills.items():
            current = state.skills.get(skill, 0)
            skill_scores.append(current / target if target > 0 else 0)
        if skill_scores:
            score += 0.3 * np.mean(skill_scores)

        # Сеть
        network_ratio = len(state.contacts) / goal.target_network_size
        score += 0.2 * min(network_ratio, 1.0)

        return score

    def _compute_transition_cost(self, transition: Transition) -> float:
        """Вычислить стоимость перехода"""
        # Взвешенная комбинация различных стоимостей
        cost = (0.3 * transition.time_cost +
                0.3 * transition.money_cost / 10000 +  # нормализуем
                0.2 * transition.energy_cost +
                0.2 * transition.stress_cost)

        # Вычитаем выгоды
        benefits = (0.3 * transition.income_gain / 10000 +
                   0.3 * transition.satisfaction_gain +
                   0.2 * transition.network_gain / 100 +
                   0.2 * sum(transition.skill_gain.values()))

        return max(cost - benefits, 0.1)  # минимальная стоимость


# ============================================================================
# SKILL LEARNING OPTIMIZER
# ============================================================================

class SkillLearningOptimizer:
    """Оптимизация последовательности обучения навыкам"""

    def __init__(self):
        self.skill_graph = KnowledgeGraph() if HAS_OPTIMIZERS else None

    def optimize_learning_path(self, current_skills: Dict[str, float],
                              target_skills: Dict[str, float],
                              time_budget: float = 6.0) -> List[str]:
        """
        Найти оптимальную последовательность изучения навыков

        Parameters:
        -----------
        current_skills: текущий уровень навыков
        target_skills: целевой уровень навыков
        time_budget: доступное время (месяцы)

        Returns:
        --------
        learning_path: последовательность навыков для изучения
        """
        # Определяем навыки, которые нужно улучшить
        skills_to_learn = []
        for skill, target_level in target_skills.items():
            current_level = current_skills.get(skill, 0)
            if target_level > current_level:
                gap = target_level - current_level
                skills_to_learn.append((skill, gap))

        # Сортируем по важности и зависимостям
        # Используем TSP-подход: оптимизируем последовательность

        if HAS_OPTIMIZERS:
            # Используем оптимизатор диссертаций для навыков!
            chapters = []
            for i, (skill, gap) in enumerate(skills_to_learn):
                chapter = Chapter(
                    id=f"skill_{i}",
                    title=skill,
                    content=f"Learning {skill}",
                    dependencies=[],  # можно добавить зависимости
                    keywords=[skill],
                    domain=skill.split('_')[0] if '_' in skill else "general",
                    word_count=int(gap * 1000),  # пропорционально пробелу
                    difficulty=gap
                )
                chapters.append(chapter)

            optimizer = DissertationOptimizer(chapters)
            optimal_order, cost = optimizer.optimize(method='greedy')

            learning_path = [chapters[i].title for i in range(len(optimal_order))
                           if optimal_order[i] < len(chapters)]
        else:
            # Простая эвристика: сортируем по пробелу
            skills_to_learn.sort(key=lambda x: x[1], reverse=True)
            learning_path = [skill for skill, _ in skills_to_learn]

        return learning_path


# ============================================================================
# SALESMAN LIFE OPTIMIZER (главный класс)
# ============================================================================

class SalesmanLifeOptimizer:
    """
    Главный класс оптимизации жизни коммивояжера

    Интегрирует все компоненты:
    - Оптимизация маршрутов (физическая)
    - Оптимизация обучения (когнитивная)
    - Оптимизация сети (социальная)
    - Оптимизация карьеры (профессиональная)
    - Рационализация опыта (мета)
    """

    def __init__(self):
        self.life_graph = LifeGraph()
        self.career_optimizer = CareerPathOptimizer(self.life_graph)
        self.learning_optimizer = SkillLearningOptimizer()

        # База знаний
        self.knowledge_base = KnowledgeGraph() if HAS_OPTIMIZERS else None
        self.rationalizer = KnowledgeRationalizer() if HAS_OPTIMIZERS else None

    def optimize_life(self, current_state: LifeState, goal: CareerGoal,
                     horizon: float = 10.0) -> Dict:
        """
        Комплексная оптимизация жизни

        Parameters:
        -----------
        current_state: текущее состояние
        goal: карьерная цель
        horizon: горизонт планирования (лет)

        Returns:
        --------
        plan: план оптимизации
        """
        plan = {
            'current': current_state,
            'goal': goal,
            'horizon': horizon,
            'career_path': [],
            'learning_path': [],
            'milestones': [],
            'metrics': {},
            'recommendations': []
        }

        # 1. Оптимизация карьерного пути
        if current_state.id in self.life_graph.states:
            career_path, cost = self.career_optimizer.optimize(
                current_state.id,
                goal,
                method='greedy'
            )
            plan['career_path'] = career_path
            plan['metrics']['career_cost'] = cost

        # 2. Оптимизация обучения
        learning_path = self.learning_optimizer.optimize_learning_path(
            current_state.skills,
            goal.target_skills,
            time_budget=horizon * 12 * 0.2  # 20% времени на обучение
        )
        plan['learning_path'] = learning_path

        # 3. Рекомендации
        recommendations = self._generate_recommendations(current_state, goal)
        plan['recommendations'] = recommendations

        # 4. Milestones
        milestones = self._generate_milestones(current_state, goal, horizon)
        plan['milestones'] = milestones

        # 5. Метрики
        metrics = self._compute_metrics(current_state, goal)
        plan['metrics'].update(metrics)

        return plan

    def _generate_recommendations(self, state: LifeState, goal: CareerGoal) -> List[str]:
        """Сгенерировать рекомендации"""
        recommendations = []

        # Анализ дохода
        if state.income < goal.target_income * 0.5:
            recommendations.append(
                "💰 Приоритет: Увеличение дохода. "
                "Рассмотрите специализацию в высокодоходных сегментах."
            )

        # Анализ навыков
        skill_gaps = []
        for skill, target in goal.target_skills.items():
            current = state.skills.get(skill, 0)
            if current < target * 0.5:
                skill_gaps.append(skill)

        if skill_gaps:
            recommendations.append(
                f"📚 Критические навыки для развития: {', '.join(skill_gaps[:3])}"
            )

        # Анализ сети
        if len(state.contacts) < goal.target_network_size * 0.5:
            recommendations.append(
                "🤝 Приоритет: Расширение профессиональной сети. "
                "Цель: +10 качественных контактов/месяц."
            )

        # Анализ удовлетворенности
        if state.satisfaction < 0.5:
            recommendations.append(
                "⚠️ Низкая удовлетворенность работой. "
                "Рассмотрите смену направления или формата работы."
            )

        # Анализ энергии
        if state.energy < 0.6 or state.stress > 0.7:
            recommendations.append(
                "🔋 Риск выгорания! Запланируйте отдых и снижение нагрузки."
            )

        # Финансы
        if state.savings < state.expenses * 6:
            recommendations.append(
                "💵 Создайте финансовую подушку = 6 месяцев расходов."
            )

        return recommendations

    def _generate_milestones(self, state: LifeState, goal: CareerGoal,
                            horizon: float) -> List[Dict]:
        """Сгенерировать промежуточные цели"""
        milestones = []

        # Распределяем цели по времени
        time_points = [horizon * 0.25, horizon * 0.5, horizon * 0.75, horizon]

        for i, t in enumerate(time_points):
            progress = (i + 1) / len(time_points)

            milestone = {
                'time': t,
                'year': state.age + t,
                'targets': {
                    'income': state.income + (goal.target_income - state.income) * progress,
                    'satisfaction': state.satisfaction + (goal.target_satisfaction - state.satisfaction) * progress,
                    'network_size': len(state.contacts) + int((goal.target_network_size - len(state.contacts)) * progress)
                },
                'skills': {}
            }

            # Навыки
            for skill, target_level in goal.target_skills.items():
                current_level = state.skills.get(skill, 0)
                milestone['skills'][skill] = current_level + (target_level - current_level) * progress

            milestones.append(milestone)

        return milestones

    def _compute_metrics(self, state: LifeState, goal: CareerGoal) -> Dict:
        """Вычислить метрики"""
        metrics = {}

        # Прогресс к цели
        income_progress = state.income / goal.target_income if goal.target_income > 0 else 0
        satisfaction_progress = state.satisfaction / goal.target_satisfaction if goal.target_satisfaction > 0 else 0

        # Навыки
        skill_progresses = []
        for skill, target in goal.target_skills.items():
            current = state.skills.get(skill, 0)
            progress = current / target if target > 0 else 0
            skill_progresses.append(progress)

        avg_skill_progress = np.mean(skill_progresses) if skill_progresses else 0

        # Сеть
        network_progress = len(state.contacts) / goal.target_network_size if goal.target_network_size > 0 else 0

        # Общий прогресс
        overall_progress = (
            0.3 * income_progress +
            0.2 * satisfaction_progress +
            0.3 * avg_skill_progress +
            0.2 * network_progress
        )

        metrics = {
            'overall_progress': overall_progress,
            'income_progress': income_progress,
            'satisfaction_progress': satisfaction_progress,
            'skill_progress': avg_skill_progress,
            'network_progress': network_progress,
            'health_status': state.health,
            'energy_level': state.energy,
            'stress_level': state.stress
        }

        return metrics


# ============================================================================
# DEMO & EXAMPLES
# ============================================================================

def demo_salesman_life_optimization():
    """Демонстрация оптимизации жизни коммивояжера"""
    print("=" * 80)
    print("DEMO: Оптимизация жизни коммивояжера")
    print("=" * 80)

    # Создаем оптимизатор
    optimizer = SalesmanLifeOptimizer()

    # Текущее состояние: молодой коммивояжер
    current_state = LifeState(
        id="state_0",
        name="Junior Salesman",
        location="Moscow",
        position=(55.7558, 37.6173),
        skills={
            'communication': 0.6,
            'negotiation': 0.4,
            'presentation': 0.3,
            'crm': 0.5
        },
        knowledge={
            'products': 0.5,
            'market': 0.4
        },
        contacts=['Client_1', 'Client_2', 'Colleague_1'],
        network_quality=0.5,
        income=40000,
        savings=20000,
        expenses=30000,
        age=25,
        experience_years=2,
        satisfaction=0.6,
        energy=0.85,
        stress=0.4,
        health=0.9
    )

    # Цель: через 10 лет
    goal = CareerGoal(
        name="Senior Sales Manager",
        target_income=150000,
        target_satisfaction=0.85,
        target_skills={
            'communication': 0.9,
            'negotiation': 0.9,
            'presentation': 0.85,
            'crm': 0.8,
            'leadership': 0.75,
            'strategy': 0.7
        },
        target_network_size=500,
        deadline=10.0
    )

    print("\n📊 Текущее состояние:")
    print(f"   Должность: {current_state.name}")
    print(f"   Возраст: {current_state.age} лет")
    print(f"   Опыт: {current_state.experience_years} лет")
    print(f"   Доход: ${current_state.income:,.0f}/год")
    print(f"   Контактов: {len(current_state.contacts)}")
    print(f"   Удовлетворенность: {current_state.satisfaction:.1%}")
    print(f"   Навыки: {len(current_state.skills)}")

    print("\n🎯 Цель через 10 лет:")
    print(f"   Должность: {goal.name}")
    print(f"   Целевой доход: ${goal.target_income:,.0f}/год")
    print(f"   Целевая сеть: {goal.target_network_size} контактов")
    print(f"   Целевая удовлетворенность: {goal.target_satisfaction:.1%}")
    print(f"   Навыков к освоению: {len(goal.target_skills)}")

    # Оптимизация
    print("\n⚙️  Оптимизация плана жизни...")
    plan = optimizer.optimize_life(current_state, goal, horizon=10.0)

    # Результаты
    print("\n📈 Текущий прогресс к цели:")
    metrics = plan['metrics']
    print(f"   Общий прогресс: {metrics['overall_progress']:.1%}")
    print(f"   - Доход: {metrics['income_progress']:.1%}")
    print(f"   - Навыки: {metrics['skill_progress']:.1%}")
    print(f"   - Сеть: {metrics['network_progress']:.1%}")
    print(f"   - Удовлетворенность: {metrics['satisfaction_progress']:.1%}")

    # План обучения
    print("\n📚 Оптимальная последовательность обучения:")
    for i, skill in enumerate(plan['learning_path'][:5], 1):
        print(f"   {i}. {skill}")

    # Рекомендации
    print("\n💡 Рекомендации:")
    for i, rec in enumerate(plan['recommendations'], 1):
        print(f"   {i}. {rec}")

    # Milestones
    print("\n🎯 Промежуточные цели:")
    for i, milestone in enumerate(plan['milestones'], 1):
        print(f"\n   Milestone {i} (Год {milestone['year']:.0f}):")
        print(f"      Доход: ${milestone['targets']['income']:,.0f}/год")
        print(f"      Контактов: {milestone['targets']['network_size']}")
        print(f"      Удовлетворенность: {milestone['targets']['satisfaction']:.1%}")

    print("\n" + "=" * 80)
    print("✅ Оптимизация завершена!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("Salesman Life Optimizer - система оптимизации жизни коммивояжера\n")
    demo_salesman_life_optimization()
