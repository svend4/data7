"""
MMO Economy Simulation - Multi-Agent Economic Simulation
Симуляция игровой экономики с множественными агентами

Demonstrates:
- Player behavior modeling
- Market dynamics (supply & demand)
- Inflation/deflation cycles
- Automatic balancing effectiveness
- Price discovery process

Author: AI Research Assistant
Date: 2026-02-04
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import random
import statistics

# Try to import plotting library
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# ============================================================================
# AGENT MODELS
# ============================================================================

@dataclass
class Player:
    """Игрок как экономический агент"""
    id: int
    name: str
    gold: int = 1000
    level: int = 1

    # Характеристики игрока
    play_style: str = "balanced"  # casual, hardcore, trader, grinder
    activity_level: float = 1.0  # 0.5-2.0

    # Экономическое поведение
    spending_rate: float = 0.7  # Сколько % дохода тратит
    saving_rate: float = 0.3

    # История
    gold_history: List[int] = field(default_factory=list)
    trades_made: int = 0

    def earn_gold(self, amount: int):
        """Заработать золото"""
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        """Потратить золото"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def daily_income(self, difficulty_mult: float = 1.0) -> int:
        """Дневной доход игрока"""
        base_income = 100 + self.level * 20

        # Модификаторы по стилю игры
        style_mult = {
            'casual': 0.7,
            'balanced': 1.0,
            'hardcore': 1.5,
            'trader': 0.8,  # Меньше от квестов, больше от торговли
            'grinder': 1.3
        }

        income = int(base_income * style_mult[self.play_style] *
                    self.activity_level * difficulty_mult)

        return income

    def daily_expenses(self, economy_prices: Dict[str, float]) -> int:
        """Дневные расходы игрока"""
        base_expenses = 50 + self.level * 10

        # Модификатор цен
        price_mult = economy_prices.get('repair_cost', 1.0)

        expenses = int(base_expenses * price_mult * self.activity_level)

        return expenses


# ============================================================================
# MARKET MODEL
# ============================================================================

@dataclass
class Item:
    """Предмет на рынке"""
    id: str
    name: str
    base_price: int
    current_price: int
    supply: int = 100
    demand: int = 100

    def update_price(self):
        """Обновить цену на основе спроса и предложения"""
        if self.supply == 0:
            self.current_price = int(self.base_price * 2.0)
            return

        # Простая модель: price = base_price * (demand / supply)
        ratio = self.demand / self.supply

        # Ограничиваем изменения
        ratio = max(0.5, min(2.0, ratio))

        self.current_price = int(self.base_price * ratio)


class Market:
    """Игровой рынок"""

    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.transaction_history: List[Dict] = []

        # Создаем базовые предметы
        self._init_items()

    def _init_items(self):
        """Инициализировать предметы"""
        items_data = [
            ('iron_ore', 'Iron Ore', 10),
            ('health_potion', 'Health Potion', 20),
            ('magic_scroll', 'Magic Scroll', 50),
            ('rare_gem', 'Rare Gem', 200),
            ('epic_sword', 'Epic Sword', 1000),
        ]

        for item_id, name, price in items_data:
            self.items[item_id] = Item(item_id, name, price, price)

    def simulate_trade(self, item_id: str, buyers: int, sellers: int):
        """Симулировать торговлю"""
        if item_id not in self.items:
            return

        item = self.items[item_id]

        # Обновляем спрос и предложение
        item.demand += buyers
        item.supply += sellers

        # Фактические сделки (минимум из покупателей и продавцов)
        trades = min(buyers, sellers)
        item.demand -= trades
        item.supply -= trades

        # Обновляем цену
        item.update_price()

        # Записываем транзакцию
        self.transaction_history.append({
            'item': item_id,
            'trades': trades,
            'price': item.current_price,
            'demand': item.demand,
            'supply': item.supply
        })

    def get_price(self, item_id: str) -> int:
        """Получить текущую цену"""
        return self.items[item_id].current_price if item_id in self.items else 0


# ============================================================================
# ECONOMY SIMULATION
# ============================================================================

class EconomySimulation:
    """Симуляция игровой экономики"""

    def __init__(self, num_players: int = 100):
        self.num_players = num_players
        self.players: List[Player] = []
        self.market = Market()

        # Экономические параметры
        self.total_gold = 0
        self.gold_generation_rate = 0
        self.gold_sink_rate = 0

        # Цены (модификаторы для балансировки)
        self.prices = {
            'repair_cost': 1.0,
            'teleport_cost': 1.0,
            'auction_fee': 0.05,
        }

        # История
        self.history = {
            'day': [],
            'total_gold': [],
            'avg_gold_per_player': [],
            'inflation_rate': [],
            'gini_coefficient': [],
        }

        self._init_players()

    def _init_players(self):
        """Инициализировать игроков"""
        play_styles = ['casual', 'balanced', 'hardcore', 'trader', 'grinder']

        for i in range(self.num_players):
            style = random.choice(play_styles)
            activity = random.uniform(0.5, 2.0)

            player = Player(
                id=i,
                name=f"Player_{i}",
                gold=random.randint(500, 1500),
                level=random.randint(1, 20),
                play_style=style,
                activity_level=activity
            )

            self.players.append(player)

        self._update_total_gold()

    def _update_total_gold(self):
        """Обновить общее количество золота"""
        self.total_gold = sum(p.gold for p in self.players)

    def simulate_day(self, day: int):
        """Симулировать один игровой день"""
        daily_generation = 0
        daily_sink = 0

        # Каждый игрок зарабатывает и тратит
        for player in self.players:
            # Доход
            income = player.daily_income()
            player.earn_gold(income)
            daily_generation += income

            # Расходы
            expenses = player.daily_expenses(self.prices)
            if player.spend_gold(expenses):
                daily_sink += expenses

            # Случайные покупки на рынке
            if random.random() < 0.3:  # 30% шанс
                item_id = random.choice(list(self.market.items.keys()))
                price = self.market.get_price(item_id)
                if player.spend_gold(price):
                    daily_sink += int(price * self.prices['auction_fee'])
                    player.trades_made += 1

        # Обновляем параметры экономики
        self.gold_generation_rate = daily_generation
        self.gold_sink_rate = daily_sink
        self._update_total_gold()

        # Рыночная активность
        self._simulate_market_activity()

        # Балансировка (каждые 7 дней)
        if day % 7 == 0:
            self._balance_economy()

        # Сохраняем статистику
        self._record_statistics(day)

    def _simulate_market_activity(self):
        """Симулировать рыночную активность"""
        for item_id in self.market.items.keys():
            # Случайное количество покупателей и продавцов
            buyers = random.randint(5, 20)
            sellers = random.randint(5, 20)

            self.market.simulate_trade(item_id, buyers, sellers)

    def _balance_economy(self):
        """Балансировать экономику"""
        inflation_rate = self.gold_generation_rate / self.gold_sink_rate if self.gold_sink_rate > 0 else 999

        # Инфляция (слишком много золота)
        if inflation_rate > 1.15:
            # Увеличиваем стоки
            self.prices['repair_cost'] *= 1.10
            self.prices['teleport_cost'] *= 1.15
            self.prices['auction_fee'] *= 1.10

        # Дефляция (слишком мало золота)
        elif inflation_rate < 0.85:
            # Уменьшаем стоки
            self.prices['repair_cost'] *= 0.95
            self.prices['teleport_cost'] *= 0.90
            self.prices['auction_fee'] *= 0.95

    def _calculate_gini_coefficient(self) -> float:
        """Вычислить коэффициент Джини (неравенство богатства)"""
        gold_amounts = sorted([p.gold for p in self.players])
        n = len(gold_amounts)

        if sum(gold_amounts) == 0:
            return 0.0

        # Формула Джини
        cumsum = 0
        for i, gold in enumerate(gold_amounts):
            cumsum += gold * (n - i)

        gini = (2 * cumsum) / (n * sum(gold_amounts)) - (n + 1) / n

        return gini

    def _record_statistics(self, day: int):
        """Записать статистику"""
        avg_gold = self.total_gold / self.num_players
        inflation_rate = self.gold_generation_rate / self.gold_sink_rate if self.gold_sink_rate > 0 else 0
        gini = self._calculate_gini_coefficient()

        self.history['day'].append(day)
        self.history['total_gold'].append(self.total_gold)
        self.history['avg_gold_per_player'].append(avg_gold)
        self.history['inflation_rate'].append(inflation_rate)
        self.history['gini_coefficient'].append(gini)

    def run_simulation(self, days: int = 100, verbose: bool = True):
        """Запустить симуляцию на N дней"""
        if verbose:
            print("=" * 80)
            print(f"ECONOMY SIMULATION: {self.num_players} players, {days} days")
            print("=" * 80)
            print()

        for day in range(1, days + 1):
            self.simulate_day(day)

            # Промежуточная статистика
            if verbose and (day % 10 == 0 or day == 1):
                self._print_day_summary(day)

        if verbose:
            print()
            print("=" * 80)
            print("SIMULATION COMPLETE")
            print("=" * 80)
            self._print_final_summary()

    def _print_day_summary(self, day: int):
        """Вывести сводку за день"""
        avg_gold = self.total_gold / self.num_players
        inflation = self.gold_generation_rate / self.gold_sink_rate if self.gold_sink_rate > 0 else 0

        print(f"Day {day:3d} | "
              f"Total Gold: {self.total_gold:,} | "
              f"Avg: {avg_gold:.0f} | "
              f"Inflation: {inflation:.2f}x | "
              f"Repair: {self.prices['repair_cost']:.2f}x")

    def _print_final_summary(self):
        """Вывести финальную сводку"""
        print()
        print("FINAL STATISTICS:")
        print("-" * 80)

        # Золото
        initial_gold = self.history['total_gold'][0]
        final_gold = self.history['total_gold'][-1]
        gold_growth = (final_gold - initial_gold) / initial_gold * 100

        print(f"Total Gold:    {initial_gold:,} → {final_gold:,} ({gold_growth:+.1f}%)")

        avg_initial = self.history['avg_gold_per_player'][0]
        avg_final = self.history['avg_gold_per_player'][-1]

        print(f"Avg per Player: {avg_initial:.0f} → {avg_final:.0f}")

        # Инфляция
        avg_inflation = statistics.mean(self.history['inflation_rate'])
        print(f"Avg Inflation: {avg_inflation:.2f}x")

        # Неравенство
        initial_gini = self.history['gini_coefficient'][0]
        final_gini = self.history['gini_coefficient'][-1]

        print(f"Gini Coefficient: {initial_gini:.3f} → {final_gini:.3f}")
        print(f"  (0 = perfect equality, 1 = maximum inequality)")

        # Цены
        print()
        print("Final Prices (multipliers):")
        for key, value in self.prices.items():
            print(f"  {key}: {value:.2f}x")

        # Рынок
        print()
        print("Market Prices:")
        for item_id, item in self.market.items.items():
            change = (item.current_price - item.base_price) / item.base_price * 100
            print(f"  {item.name}: {item.base_price} → {item.current_price} ({change:+.1f}%)")

    def generate_report(self) -> str:
        """Сгенерировать текстовый отчет"""
        lines = []

        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║         MMO ECONOMY SIMULATION REPORT                      ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")

        days = len(self.history['day'])
        lines.append(f"║ Duration: {days} days                                        ║")
        lines.append(f"║ Players: {self.num_players}                                          ║")
        lines.append("║                                                            ║")

        # Экономический рост
        initial_gold = self.history['total_gold'][0]
        final_gold = self.history['total_gold'][-1]
        growth = (final_gold - initial_gold) / initial_gold * 100

        lines.append("║ ECONOMIC GROWTH:                                           ║")
        lines.append(f"║   Total Gold: {initial_gold:,} → {final_gold:,}               ║")
        lines.append(f"║   Growth: {growth:+.1f}%                                        ║")

        # Балансировка
        avg_inflation = statistics.mean(self.history['inflation_rate'])
        lines.append("║                                                            ║")
        lines.append("║ BALANCING EFFECTIVENESS:                                   ║")
        lines.append(f"║   Avg Inflation: {avg_inflation:.2f}x                               ║")

        if 0.9 <= avg_inflation <= 1.1:
            lines.append("║   Status: ✅ EXCELLENT (within 10% target)                 ║")
        elif 0.8 <= avg_inflation <= 1.2:
            lines.append("║   Status: ✅ GOOD (within 20% target)                      ║")
        else:
            lines.append("║   Status: ⚠️ NEEDS TUNING                                  ║")

        # Неравенство
        final_gini = self.history['gini_coefficient'][-1]
        lines.append("║                                                            ║")
        lines.append("║ WEALTH DISTRIBUTION:                                       ║")
        lines.append(f"║   Gini Coefficient: {final_gini:.3f}                            ║")

        if final_gini < 0.3:
            lines.append("║   Status: ✅ Low inequality                                 ║")
        elif final_gini < 0.5:
            lines.append("║   Status: ⚠️ Moderate inequality                            ║")
        else:
            lines.append("║   Status: 🚨 High inequality                                ║")

        lines.append("╚════════════════════════════════════════════════════════════╝")

        return "\n".join(lines)

    def plot_results(self, filename: str = 'economy_simulation.png'):
        """Построить графики (если matplotlib доступен)"""
        if not HAS_MATPLOTLIB:
            print("⚠️  matplotlib not available - skipping plots")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('MMO Economy Simulation Results', fontsize=16, fontweight='bold')

        # 1. Total Gold over time
        ax1 = axes[0, 0]
        ax1.plot(self.history['day'], self.history['total_gold'], 'b-', linewidth=2)
        ax1.set_xlabel('Day')
        ax1.set_ylabel('Total Gold')
        ax1.set_title('Total Gold in Economy')
        ax1.grid(True, alpha=0.3)

        # 2. Inflation Rate
        ax2 = axes[0, 1]
        ax2.plot(self.history['day'], self.history['inflation_rate'], 'r-', linewidth=2)
        ax2.axhline(y=1.0, color='g', linestyle='--', label='Target (1.0x)')
        ax2.axhline(y=1.15, color='orange', linestyle='--', alpha=0.5, label='Upper bound')
        ax2.axhline(y=0.85, color='orange', linestyle='--', alpha=0.5, label='Lower bound')
        ax2.set_xlabel('Day')
        ax2.set_ylabel('Inflation Rate')
        ax2.set_title('Inflation Rate (Generation/Sink)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Average Gold per Player
        ax3 = axes[1, 0]
        ax3.plot(self.history['day'], self.history['avg_gold_per_player'], 'g-', linewidth=2)
        ax3.set_xlabel('Day')
        ax3.set_ylabel('Average Gold')
        ax3.set_title('Average Gold per Player')
        ax3.grid(True, alpha=0.3)

        # 4. Gini Coefficient (Inequality)
        ax4 = axes[1, 1]
        ax4.plot(self.history['day'], self.history['gini_coefficient'], 'm-', linewidth=2)
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Gini Coefficient')
        ax4.set_title('Wealth Inequality (Gini Coefficient)')
        ax4.set_ylim([0, 1])
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"✅ Plot saved to: {filename}")


# ============================================================================
# DEMO
# ============================================================================

def run_demo():
    """Запустить демонстрацию симуляции"""
    print("\n" + "=" * 80)
    print("MMO ECONOMY SIMULATION - Multi-Agent Demo")
    print("=" * 80 + "\n")

    # Создаем симуляцию
    sim = EconomySimulation(num_players=100)

    # Запускаем на 100 дней
    sim.run_simulation(days=100, verbose=True)

    # Генерируем отчет
    print()
    report = sim.generate_report()
    print(report)

    # Строим графики
    print()
    sim.plot_results('mmo_economy_simulation.png')

    print()
    print("=" * 80)
    print("✅ Simulation complete!")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
