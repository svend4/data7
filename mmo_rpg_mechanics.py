"""
MMO RPG Game Mechanics - Python Implementation
Программная реализация игровых механик на основе оптимизации

Реализует:
1. Smart Quest Log - TSP оптимизация квестов
2. AI Director - динамическая балансировка сложности
3. Burnout Detector - мониторинг выгорания
4. Economy Balancer - контроль инфляции
5. Skill Tree Optimizer - оптимизация билдов

Author: AI Research Assistant
Date: 2026-02-04
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import math
import random

# Импорт наших оптимизаторов
try:
    from dissertation_optimizer import DissertationOptimizer, Chapter
    HAS_OPTIMIZER = True
except ImportError:
    HAS_OPTIMIZER = False


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Location:
    """Локация в игровом мире"""
    id: str
    name: str
    position: Tuple[float, float]
    level_range: Tuple[int, int]
    zone_type: str = "neutral"  # neutral, pvp, dungeon


@dataclass
class Quest:
    """Квест"""
    id: str
    name: str
    location_id: str
    level: int
    estimated_time: int  # минуты
    rewards: Dict[str, int] = field(default_factory=dict)  # gold, xp, items
    prerequisites: List[str] = field(default_factory=list)
    quest_type: str = "normal"  # normal, daily, epic, dungeon


@dataclass
class Skill:
    """Навык в древе скиллов"""
    id: str
    name: str
    tier: int  # 1-5
    cost: int  # skill points
    power: float  # эффективность
    prerequisites: List[str] = field(default_factory=list)
    synergies: Dict[str, float] = field(default_factory=dict)  # skill_id: bonus
    description: str = ""


@dataclass
class PlayerState:
    """Состояние игрока"""
    id: str
    name: str
    level: int
    experience: int
    gold: int

    # Позиция
    current_location: str

    # Навыки
    skills: Dict[str, int] = field(default_factory=dict)  # skill_id: level
    skill_points: int = 0

    # Метрики игры
    session_time: float = 0.0  # часы
    total_play_time: float = 0.0

    # Метрики удовольствия
    fun_level: float = 0.75  # 0-1
    frustration: float = 0.2  # 0-1
    energy: float = 0.9  # 0-1

    # Активность
    recent_deaths: int = 0
    recent_successes: int = 0
    repetitive_actions: int = 0

    # История
    completed_quests: List[str] = field(default_factory=list)
    quest_history: List[Dict] = field(default_factory=list)


# ============================================================================
# 1. SMART QUEST LOG - TSP Optimization
# ============================================================================

class SmartQuestLog:
    """
    Умный квестовый журнал с автоматической оптимизацией маршрута
    Использует TSP алгоритмы для минимизации времени в пути
    """

    def __init__(self, locations: Dict[str, Location], quests: Dict[str, Quest]):
        self.locations = locations
        self.quests = quests

    def optimize_quest_order(self, player: PlayerState,
                            active_quests: List[str]) -> Tuple[List[str], float]:
        """
        Найти оптимальный порядок выполнения квестов

        Returns:
            (optimal_order, time_saved)
        """
        if not active_quests:
            return [], 0.0

        # Получаем данные о квестах
        quest_objects = [self.quests[qid] for qid in active_quests]

        # Текущая позиция игрока
        current_loc = self.locations[player.current_location]

        # Строим матрицу расстояний
        distance_matrix = self._build_distance_matrix(
            current_loc, quest_objects
        )

        # Находим оптимальный маршрут
        if HAS_OPTIMIZER and len(active_quests) > 3:
            # Используем TSP оптимизатор для больших наборов
            optimal_order = self._optimize_with_tsp(quest_objects, distance_matrix)
        else:
            # Greedy algorithm для малых наборов
            optimal_order = self._greedy_optimize(quest_objects, distance_matrix)

        # Вычисляем экономию времени
        random_time = self._calculate_total_time(
            quest_objects, distance_matrix, list(range(len(quest_objects)))
        )
        optimal_time = self._calculate_total_time(
            quest_objects, distance_matrix, optimal_order
        )
        time_saved = random_time - optimal_time

        # Возвращаем ID квестов в оптимальном порядке
        optimized_quest_ids = [quest_objects[i].id for i in optimal_order]

        return optimized_quest_ids, time_saved

    def _build_distance_matrix(self, start: Location,
                               quests: List[Quest]) -> List[List[float]]:
        """Построить матрицу расстояний между локациями квестов"""
        n = len(quests)
        matrix = [[0.0] * n for _ in range(n)]

        # Расстояния между квестами
        for i in range(n):
            loc_i = self.locations[quests[i].location_id]
            for j in range(i + 1, n):
                loc_j = self.locations[quests[j].location_id]
                dist = self._euclidean_distance(loc_i.position, loc_j.position)
                matrix[i][j] = dist
                matrix[j][i] = dist

        return matrix

    def _euclidean_distance(self, pos1: Tuple[float, float],
                           pos2: Tuple[float, float]) -> float:
        """Евклидово расстояние между позициями"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)

    def _greedy_optimize(self, quests: List[Quest],
                        distances: List[List[float]]) -> List[int]:
        """Greedy алгоритм для оптимизации порядка"""
        n = len(quests)
        if n == 0:
            return []

        visited = [False] * n
        path = [0]  # Начинаем с первого квеста
        visited[0] = True

        for _ in range(n - 1):
            current = path[-1]
            min_dist = float('inf')
            next_idx = -1

            # Находим ближайший непосещенный квест
            for j in range(n):
                if not visited[j] and distances[current][j] < min_dist:
                    min_dist = distances[current][j]
                    next_idx = j

            if next_idx != -1:
                path.append(next_idx)
                visited[next_idx] = True

        return path

    def _optimize_with_tsp(self, quests: List[Quest],
                          distances: List[List[float]]) -> List[int]:
        """Использовать TSP оптимизатор диссертаций"""
        # Преобразуем квесты в "главы"
        chapters = []
        for i, quest in enumerate(quests):
            chapter = Chapter(
                id=quest.id,
                title=quest.name,
                content=f"Quest: {quest.name}",
                dependencies=quest.prerequisites,
                keywords=[quest.quest_type],
                domain=quest.location_id,
                word_count=quest.estimated_time * 100
            )
            chapters.append(chapter)

        # Запускаем оптимизатор
        optimizer = DissertationOptimizer(chapters)
        optimal_order, _ = optimizer.optimize(method='greedy')

        return list(range(len(optimal_order)))

    def _calculate_total_time(self, quests: List[Quest],
                             distances: List[List[float]],
                             order: List[int]) -> float:
        """Вычислить общее время для данного порядка"""
        total_time = 0.0

        # Время на выполнение квестов
        for idx in order:
            total_time += quests[idx].estimated_time

        # Время на перемещение между квестами
        for i in range(len(order) - 1):
            current_idx = order[i]
            next_idx = order[i + 1]
            # Предполагаем скорость 1 единица расстояния = 1 минута
            total_time += distances[current_idx][next_idx]

        return total_time

    def generate_quest_log_ui(self, player: PlayerState,
                             active_quests: List[str]) -> str:
        """Сгенерировать UI квестового журнала"""
        optimal_order, time_saved = self.optimize_quest_order(player, active_quests)

        ui = []
        ui.append("╔════════════════════════════════════════════╗")
        ui.append("║     SMART QUEST LOG (Optimized Route)      ║")
        ui.append("╠════════════════════════════════════════════╣")

        if not optimal_order:
            ui.append("║  No active quests                          ║")
        else:
            # Группируем по зонам
            zones = defaultdict(list)
            for qid in optimal_order:
                quest = self.quests[qid]
                zones[quest.location_id].append(quest)

            for zone_id, zone_quests in zones.items():
                zone = self.locations[zone_id]
                ui.append(f"║                                            ║")
                ui.append(f"║ 📍 Zone: {zone.name:<30} ║")

                for quest in zone_quests:
                    status = "☑" if quest.id in player.completed_quests else "☐"
                    ui.append(f"║   {status} {quest.name:<35} ║")
                    ui.append(f"║      └─ Time: {quest.estimated_time} min, Level: {quest.level}     ║")

            ui.append("╠════════════════════════════════════════════╣")
            ui.append(f"║ ⏱️  Time saved: {time_saved:.0f} minutes          ║")
            ui.append(f"║ 🎯 Optimized for minimal travel time       ║")

        ui.append("╚════════════════════════════════════════════╝")

        return "\n".join(ui)


# ============================================================================
# 2. AI DIRECTOR - Dynamic Difficulty
# ============================================================================

class AIDirector:
    """
    AI Director для динамической балансировки сложности игры
    Поддерживает игрока в состоянии Flow
    """

    def __init__(self):
        self.difficulty_level = 1.0  # 0.5 - 2.0
        self.adjustment_history = []

    def analyze_performance(self, player: PlayerState) -> Dict[str, float]:
        """Анализ performance игрока"""
        total_attempts = player.recent_deaths + player.recent_successes

        if total_attempts == 0:
            return {
                'success_rate': 0.5,
                'death_rate': 0.0,
                'skill_estimate': 0.5,
                'challenge_level': self.difficulty_level
            }

        success_rate = player.recent_successes / total_attempts
        death_rate = player.recent_deaths / total_attempts

        # Оценка навыка игрока (0-1)
        skill_estimate = success_rate * 0.7 + (1 - death_rate) * 0.3

        return {
            'success_rate': success_rate,
            'death_rate': death_rate,
            'skill_estimate': skill_estimate,
            'challenge_level': self.difficulty_level
        }

    def adjust_difficulty(self, player: PlayerState) -> Dict[str, any]:
        """Скорректировать сложность на основе performance"""
        perf = self.analyze_performance(player)

        adjustment = {
            'previous_difficulty': self.difficulty_level,
            'action': 'maintain',
            'reason': '',
            'new_difficulty': self.difficulty_level
        }

        # Слишком легко
        if perf['success_rate'] > 0.85 and perf['death_rate'] < 0.1:
            self.difficulty_level = min(2.0, self.difficulty_level * 1.1)
            adjustment['action'] = 'increase'
            adjustment['reason'] = 'Too easy - player success rate > 85%'
            adjustment['changes'] = [
                'Enemy HP +10%',
                'Enemy damage +10%',
                'Rewards +15% (compensation)'
            ]

        # Слишком сложно
        elif perf['death_rate'] > 0.4 or perf['success_rate'] < 0.4:
            self.difficulty_level = max(0.5, self.difficulty_level * 0.9)
            adjustment['action'] = 'decrease'
            adjustment['reason'] = 'Too hard - death rate > 40%'
            adjustment['changes'] = [
                'Enemy HP -10%',
                'Enemy damage -10%',
                'Drop rates +20%',
                'Helpful hints enabled'
            ]

        # Flow State - идеально
        elif 0.6 <= perf['success_rate'] <= 0.8:
            adjustment['action'] = 'maintain'
            adjustment['reason'] = 'Flow State - optimal challenge'

        adjustment['new_difficulty'] = self.difficulty_level
        self.adjustment_history.append(adjustment)

        return adjustment

    def calculate_encounter_difficulty(self, base_difficulty: float) -> float:
        """Вычислить финальную сложность encounter'а"""
        return base_difficulty * self.difficulty_level

    def generate_director_report(self, player: PlayerState) -> str:
        """Сгенерировать отчет AI Director"""
        perf = self.analyze_performance(player)
        adjustment = self.adjust_difficulty(player)

        report = []
        report.append("╔════════════════════════════════════════════╗")
        report.append("║           AI DIRECTOR REPORT               ║")
        report.append("╠════════════════════════════════════════════╣")
        report.append(f"║ Player: {player.name:<33} ║")
        report.append(f"║ Level: {player.level:<35} ║")
        report.append("║                                            ║")
        report.append("║ Performance Metrics:                       ║")
        report.append(f"║   Success Rate: {perf['success_rate']:.1%}                  ║")
        report.append(f"║   Death Rate: {perf['death_rate']:.1%}                    ║")
        report.append(f"║   Skill Estimate: {perf['skill_estimate']:.1%}               ║")
        report.append("║                                            ║")
        report.append(f"║ Difficulty: {self.difficulty_level:.2f}x                    ║")
        report.append(f"║ Action: {adjustment['action']:<33} ║")
        report.append(f"║ Reason: {adjustment['reason']:<33} ║")

        if adjustment['action'] != 'maintain':
            report.append("║                                            ║")
            report.append("║ Applied Changes:                           ║")
            for change in adjustment.get('changes', []):
                report.append(f"║   • {change:<38} ║")

        report.append("╚════════════════════════════════════════════╝")

        return "\n".join(report)


# ============================================================================
# 3. BURNOUT DETECTOR
# ============================================================================

class BurnoutDetector:
    """
    Система обнаружения и предотвращения выгорания игроков
    """

    def __init__(self, warning_threshold: float = 0.6,
                 critical_threshold: float = 0.8):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def calculate_burnout_risk(self, player: PlayerState) -> float:
        """
        Вычислить риск выгорания (0-1)

        Формула:
        Burnout = 0.25·Repetitiveness + 0.25·Frustration +
                  0.20·Progress_Stagnation + 0.15·Social_Isolation +
                  0.15·Time_Pressure
        """
        # 1. Repetitiveness (монотонность)
        repetitiveness = min(1.0, player.repetitive_actions / 100.0)

        # 2. Frustration
        frustration = player.frustration

        # 3. Progress Stagnation (отсутствие прогресса)
        # Проверяем последние 10 квестов
        recent_progress = len(player.quest_history[-10:]) / 10.0 if player.quest_history else 0.0
        progress_stagnation = 1.0 - recent_progress

        # 4. Social Isolation (играет ли в одиночку)
        # Упрощенная метрика
        social_isolation = 0.5  # Заглушка, в реальности анализируем group play %

        # 5. Time Pressure (играет ли слишком долго)
        if player.session_time > 4.0:  # >4 часа
            time_pressure = min(1.0, (player.session_time - 4.0) / 4.0)
        else:
            time_pressure = 0.0

        # Взвешенная сумма
        burnout_risk = (
            0.25 * repetitiveness +
            0.25 * frustration +
            0.20 * progress_stagnation +
            0.15 * social_isolation +
            0.15 * time_pressure
        )

        return burnout_risk

    def detect_and_intervene(self, player: PlayerState) -> Dict[str, any]:
        """Обнаружить риск и предложить интервенцию"""
        risk = self.calculate_burnout_risk(player)

        result = {
            'risk_level': risk,
            'status': 'healthy',
            'recommendations': []
        }

        if risk < self.warning_threshold:
            result['status'] = 'healthy'
            result['recommendations'].append('Keep having fun!')

        elif risk < self.critical_threshold:
            result['status'] = 'warning'
            result['recommendations'] = [
                f"⚠️  You've been playing for {player.session_time:.1f} hours",
                "💡 Consider taking a short break",
                "🎮 Try something different - PvP or exploration?",
                "👥 Your friends are online - join them!"
            ]

        else:  # risk >= critical_threshold
            result['status'] = 'critical'
            result['recommendations'] = [
                "🚨 HIGH BURNOUT RISK DETECTED",
                "🛑 Strongly recommend taking a break",
                "💤 Rested XP bonus will accumulate",
                "🎁 Special rewards waiting after break",
                "⏰ Consider logging out for at least 30 minutes"
            ]
            result['mechanical_changes'] = [
                'Boost drop rates by 25%',
                'Reduce grind requirements by 20%',
                'Enable fast travel shortcuts',
                'Double XP for next hour'
            ]

        return result

    def generate_burnout_report(self, player: PlayerState) -> str:
        """Сгенерировать отчет о риске выгорания"""
        result = self.detect_and_intervene(player)
        risk = result['risk_level']

        report = []
        report.append("╔════════════════════════════════════════════╗")
        report.append("║        BURNOUT PREVENTION SYSTEM           ║")
        report.append("╠════════════════════════════════════════════╣")

        # Визуализация риска
        bar_length = 40
        filled = int(risk * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)

        report.append(f"║ Burnout Risk: {risk:.1%}                     ║")
        report.append(f"║ [{bar}] ║")

        # Статус
        status_emoji = {'healthy': '✅', 'warning': '⚠️', 'critical': '🚨'}
        emoji = status_emoji.get(result['status'], '❓')
        report.append(f"║ Status: {emoji} {result['status'].upper():<29} ║")

        # Рекомендации
        if result['recommendations']:
            report.append("║                                            ║")
            report.append("║ Recommendations:                           ║")
            for rec in result['recommendations']:
                # Разбиваем длинные строки
                if len(rec) <= 40:
                    report.append(f"║ {rec:<42} ║")
                else:
                    words = rec.split()
                    line = ""
                    for word in words:
                        if len(line + word) <= 40:
                            line += word + " "
                        else:
                            report.append(f"║ {line:<42} ║")
                            line = word + " "
                    if line:
                        report.append(f"║ {line:<42} ║")

        # Механические изменения
        if 'mechanical_changes' in result:
            report.append("║                                            ║")
            report.append("║ Auto-applied changes:                      ║")
            for change in result['mechanical_changes']:
                report.append(f"║   • {change:<38} ║")

        report.append("╚════════════════════════════════════════════╝")

        return "\n".join(report)


# ============================================================================
# 4. ECONOMY BALANCER
# ============================================================================

class EconomyBalancer:
    """
    Система балансировки игровой экономики
    Контроль инфляции и дефляции
    """

    def __init__(self):
        self.total_gold = 1000000  # Всего золота в экономике
        self.gold_generation_rate = 50000  # В день
        self.gold_sink_rate = 45000  # В день
        self.price_history = defaultdict(list)

    def calculate_inflation_rate(self) -> float:
        """Вычислить уровень инфляции"""
        if self.gold_sink_rate == 0:
            return float('inf')

        inflation_rate = self.gold_generation_rate / self.gold_sink_rate
        return inflation_rate

    def balance_economy(self) -> Dict[str, any]:
        """Сбалансировать экономику"""
        inflation_rate = self.calculate_inflation_rate()

        result = {
            'inflation_rate': inflation_rate,
            'status': 'balanced',
            'actions': []
        }

        # Инфляция (слишком много золота генерируется)
        if inflation_rate > 1.2:
            result['status'] = 'inflation'
            result['actions'] = [
                'Increase repair costs by 15%',
                'Increase teleport costs by 20%',
                'Add luxury items (gold sinks)',
                'Increase auction house fees by 10%'
            ]
            # Применяем изменения
            self.gold_sink_rate = int(self.gold_sink_rate * 1.15)

        # Дефляция (слишком мало золота)
        elif inflation_rate < 0.8:
            result['status'] = 'deflation'
            result['actions'] = [
                'Increase quest rewards by 15%',
                'Boost vendor sell prices by 10%',
                'Add bonus gold events',
                'Reduce repair costs by 10%'
            ]
            # Применяем изменения
            self.gold_generation_rate = int(self.gold_generation_rate * 1.15)

        else:
            result['status'] = 'balanced'
            result['actions'] = ['Economy is healthy - no changes needed']

        return result

    def find_arbitrage_opportunities(self, prices: Dict[str, float]) -> List[Dict]:
        """Найти возможности арбитража"""
        opportunities = []

        # Простой пример: ищем разницу цен >30%
        for item, price in prices.items():
            # Симулируем цену в другом месте
            other_price = price * random.uniform(0.7, 1.4)

            if abs(price - other_price) / price > 0.3:
                profit = abs(price - other_price)
                opportunities.append({
                    'item': item,
                    'buy_price': min(price, other_price),
                    'sell_price': max(price, other_price),
                    'profit': profit,
                    'roi': profit / min(price, other_price)
                })

        # Сортируем по ROI
        opportunities.sort(key=lambda x: x['roi'], reverse=True)

        return opportunities

    def generate_economy_report(self) -> str:
        """Сгенерировать отчет об экономике"""
        balance_result = self.balance_economy()

        report = []
        report.append("╔════════════════════════════════════════════╗")
        report.append("║         ECONOMY BALANCER REPORT            ║")
        report.append("╠════════════════════════════════════════════╣")
        report.append(f"║ Total Gold in Economy: {self.total_gold:,}        ║")
        report.append(f"║ Generation Rate: {self.gold_generation_rate:,}/day         ║")
        report.append(f"║ Sink Rate: {self.gold_sink_rate:,}/day              ║")
        report.append("║                                            ║")

        inflation = balance_result['inflation_rate']
        report.append(f"║ Inflation Rate: {inflation:.2f}x                 ║")

        status_emoji = {
            'balanced': '✅',
            'inflation': '📈',
            'deflation': '📉'
        }
        emoji = status_emoji.get(balance_result['status'], '❓')
        report.append(f"║ Status: {emoji} {balance_result['status'].upper():<29} ║")

        report.append("║                                            ║")
        report.append("║ Actions Taken:                             ║")
        for action in balance_result['actions']:
            if len(action) <= 40:
                report.append(f"║   • {action:<38} ║")

        report.append("╚════════════════════════════════════════════╝")

        return "\n".join(report)


# ============================================================================
# 5. SKILL TREE OPTIMIZER
# ============================================================================

class SkillTreeOptimizer:
    """
    Оптимизатор древа навыков для нахождения лучших билдов
    """

    def __init__(self, skills: Dict[str, Skill]):
        self.skills = skills

    def evaluate_build(self, skill_ids: List[str]) -> float:
        """Оценить качество билда"""
        if not skill_ids:
            return 0.0

        total_power = 0.0

        # Базовая мощь навыков
        for sid in skill_ids:
            skill = self.skills[sid]
            total_power += skill.power

        # Бонус за синергии
        for i, sid1 in enumerate(skill_ids):
            skill1 = self.skills[sid1]
            for sid2 in skill_ids[i+1:]:
                if sid2 in skill1.synergies:
                    synergy_bonus = skill1.synergies[sid2]
                    total_power += synergy_bonus

        return total_power

    def optimize_build(self, available_points: int,
                      playstyle: str = "dps") -> List[str]:
        """
        Найти оптимальный билд для заданного количества skill points

        Parameters:
            available_points: доступные skill points
            playstyle: dps, tank, healer, support
        """
        # Greedy approach: выбираем навыки с лучшим ROI
        selected = []
        remaining_points = available_points

        while remaining_points > 0:
            best_skill = None
            best_roi = 0.0

            for sid, skill in self.skills.items():
                # Проверяем, можем ли взять
                if sid in selected:
                    continue
                if skill.cost > remaining_points:
                    continue

                # Проверяем prerequisites
                if not all(prereq in selected for prereq in skill.prerequisites):
                    continue

                # Вычисляем ROI (return on investment)
                roi = skill.power / skill.cost

                # Бонус за синергии с уже взятыми навыками
                synergy_bonus = sum(
                    skill.synergies.get(sid2, 0) for sid2 in selected
                )
                roi += synergy_bonus / skill.cost

                if roi > best_roi:
                    best_roi = roi
                    best_skill = skill

            if best_skill is None:
                break

            selected.append(best_skill.id)
            remaining_points -= best_skill.cost

        return selected

    def generate_build_report(self, skill_ids: List[str],
                             total_points: int) -> str:
        """Сгенерировать отчет о билде"""
        build_power = self.evaluate_build(skill_ids)
        used_points = sum(self.skills[sid].cost for sid in skill_ids)

        report = []
        report.append("╔════════════════════════════════════════════╗")
        report.append("║         SKILL TREE OPTIMIZER               ║")
        report.append("╠════════════════════════════════════════════╣")
        report.append(f"║ Build Power: {build_power:.1f}                    ║")
        report.append(f"║ Points Used: {used_points}/{total_points}                      ║")
        report.append(f"║ Efficiency: {build_power/used_points:.2f} power/point          ║")
        report.append("║                                            ║")
        report.append("║ Selected Skills:                           ║")

        for sid in skill_ids:
            skill = self.skills[sid]
            report.append(f"║   • {skill.name:<35} ║")
            report.append(f"║     Tier {skill.tier}, Cost: {skill.cost}, Power: {skill.power:.1f}     ║")

        # Синергии
        synergies_found = []
        for i, sid1 in enumerate(skill_ids):
            skill1 = self.skills[sid1]
            for sid2 in skill_ids[i+1:]:
                if sid2 in skill1.synergies:
                    synergies_found.append(
                        (skill1.name, self.skills[sid2].name, skill1.synergies[sid2])
                    )

        if synergies_found:
            report.append("║                                            ║")
            report.append("║ Synergies Activated:                       ║")
            for s1, s2, bonus in synergies_found:
                report.append(f"║   {s1[:15]} + {s2[:15]} = +{bonus:.1f} ║")

        report.append("╚════════════════════════════════════════════╝")

        return "\n".join(report)


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

def demo_smart_quest_log():
    """Демо Smart Quest Log"""
    print("=" * 80)
    print("DEMO: Smart Quest Log")
    print("=" * 80)

    # Создаем локации
    locations = {
        'darkwood': Location('darkwood', 'Darkwood Forest', (10, 20), (5, 10)),
        'caves': Location('caves', 'Crystal Caves', (30, 15), (8, 12)),
        'mountains': Location('mountains', 'Iron Mountains', (50, 40), (10, 15)),
        'plains': Location('plains', 'Golden Plains', (15, 50), (5, 8))
    }

    # Создаем квесты
    quests = {
        'q1': Quest('q1', 'Hunt Forest Wolves', 'darkwood', 6, 15, {'gold': 50, 'xp': 100}),
        'q2': Quest('q2', 'Gather Herbs', 'darkwood', 5, 10, {'gold': 30, 'xp': 80}),
        'q3': Quest('q3', 'Clear Cave', 'caves', 10, 25, {'gold': 150, 'xp': 250}),
        'q4': Quest('q4', 'Mine Iron Ore', 'mountains', 12, 20, {'gold': 100, 'xp': 200}),
        'q5': Quest('q5', 'Escort Caravan', 'plains', 7, 30, {'gold': 80, 'xp': 150})
    }

    # Создаем игрока
    player = PlayerState('p1', 'TestPlayer', 8, 5000, 500, 'darkwood')

    # Активные квесты
    active_quests = ['q1', 'q2', 'q3', 'q4', 'q5']

    # Оптимизируем
    quest_log = SmartQuestLog(locations, quests)
    ui = quest_log.generate_quest_log_ui(player, active_quests)

    print(ui)
    print()


def demo_ai_director():
    """Демо AI Director"""
    print("=" * 80)
    print("DEMO: AI Director")
    print("=" * 80)

    # Создаем игрока с разным performance
    player = PlayerState('p1', 'SkillfulPlayer', 15, 10000, 1000, 'dungeon')
    player.recent_successes = 17
    player.recent_deaths = 3

    director = AIDirector()
    report = director.generate_director_report(player)

    print(report)
    print()


def demo_burnout_detector():
    """Демо Burnout Detector"""
    print("=" * 80)
    print("DEMO: Burnout Prevention System")
    print("=" * 80)

    # Игрок с высоким риском выгорания
    player = PlayerState('p1', 'BurnedPlayer', 20, 50000, 5000, 'grind_zone')
    player.session_time = 5.5  # 5.5 часов подряд
    player.frustration = 0.7
    player.repetitive_actions = 150
    player.quest_history = []  # Нет прогресса

    detector = BurnoutDetector()
    report = detector.generate_burnout_report(player)

    print(report)
    print()


def demo_economy_balancer():
    """Демо Economy Balancer"""
    print("=" * 80)
    print("DEMO: Economy Balancer")
    print("=" * 80)

    balancer = EconomyBalancer()
    balancer.gold_generation_rate = 60000  # Инфляция!

    report = balancer.generate_economy_report()

    print(report)
    print()


def demo_skill_tree_optimizer():
    """Демо Skill Tree Optimizer"""
    print("=" * 80)
    print("DEMO: Skill Tree Optimizer")
    print("=" * 80)

    # Создаем простое дерево навыков
    skills = {
        # Tier 1
        'basic_attack': Skill('basic_attack', 'Basic Attack', 1, 1, 10.0),
        'defense': Skill('defense', 'Defense', 1, 1, 8.0),

        # Tier 2
        'power_strike': Skill('power_strike', 'Power Strike', 2, 2, 15.0, ['basic_attack']),
        'cleave': Skill('cleave', 'Cleave', 2, 2, 14.0, ['basic_attack'], {'power_strike': 5.0}),

        # Tier 3
        'whirlwind': Skill('whirlwind', 'Whirlwind', 3, 3, 25.0, ['cleave'], {'cleave': 8.0}),
        'execute': Skill('execute', 'Execute', 3, 3, 30.0, ['power_strike'], {'power_strike': 10.0}),
    }

    optimizer = SkillTreeOptimizer(skills)

    # Оптимизируем билд для 10 skill points
    optimal_build = optimizer.optimize_build(10, 'dps')

    report = optimizer.generate_build_report(optimal_build, 10)

    print(report)
    print()


def run_all_demos():
    """Запустить все демонстрации"""
    print("\n" + "=" * 80)
    print("MMO RPG GAME MECHANICS - Complete Demo Suite")
    print("=" * 80 + "\n")

    demo_smart_quest_log()
    demo_ai_director()
    demo_burnout_detector()
    demo_economy_balancer()
    demo_skill_tree_optimizer()

    print("=" * 80)
    print("✅ All demos completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_demos()
