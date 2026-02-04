# Математическая формализация диссертации как задачи коммивояжера

## 1. Теоретические основы

### 1.1. Формальная модель диссертации как графа

**Определение 1.1:** Диссертация представляется как ориентированный взвешенный граф D = (V, E, W, C), где:

- **V = {v₁, v₂, ..., vₙ}** — множество тематических блоков (разделов, глав, параграфов)
- **E ⊆ V × V** — множество возможных переходов между блоками
- **W: E → ℝ⁺** — функция весов рёбер (когнитивная дистанция перехода)
- **C: V → ℝ⁺** — функция стоимости создания блока (время написания)

**Определение 1.2:** Когнитивная дистанция d(vᵢ, vⱼ) между блоками vᵢ и vⱼ определяется как:

```
d(vᵢ, vⱼ) = α·d_semantic(vᵢ, vⱼ) + β·d_temporal(vᵢ, vⱼ) + γ·d_logical(vᵢ, vⱼ) + δ·d_reader(vᵢ, vⱼ)
```

где:
- **d_semantic** — семантическое расстояние (несхожесть тем)
- **d_temporal** — временное расстояние (разрыв в хронологии)
- **d_logical** — логическая дистанция (нарушение причинно-следственных связей)
- **d_reader** — читательская нагрузка (сложность переключения контекста)
- **α, β, γ, δ** — весовые коэффициенты (∑ = 1)

### 1.2. Задача оптимизации структуры диссертации

**Постановка задачи:**

Найти перестановку π разделов диссертации V, минимизирующую суммарную когнитивную нагрузку:

```
minimize: J(π) = Σᵢ₌₁ⁿ⁻¹ d(π(i), π(i+1)) + λ·Σᵢ₌₁ⁿ p(π(i))

при ограничениях:
1. π — перестановка множества V
2. s_start ∈ {π(1)} (введение первым)
3. s_end ∈ {π(n)} (заключение последним)
4. ∀i: prerequisite(π(i)) ⊆ {π(1), ..., π(i-1)} (соблюдение зависимостей)
```

где:
- **p(vᵢ)** — штраф за позицию блока vᵢ в последовательности
- **λ** — параметр регуляризации
- **prerequisite(v)** — множество обязательных предшествующих блоков

### 1.3. Метрики семантического расстояния

#### 1.3.1. На основе тематического моделирования

**Определение:** Каждый блок представляется как распределение по темам θᵢ ∈ Δᵏ (k-мерный симплекс):

```
d_semantic(vᵢ, vⱼ) = D_JS(θᵢ || θⱼ)
```

где D_JS — дивергенция Йенсена-Шеннона:

```
D_JS(P || Q) = 0.5·D_KL(P || M) + 0.5·D_KL(Q || M)
M = 0.5·(P + Q)
D_KL(P || Q) = Σᵢ P(i)·log(P(i)/Q(i))
```

#### 1.3.2. На основе векторных представлений

Используя современные language models (BERT, GPT):

```
d_semantic(vᵢ, vⱼ) = 1 - cosine_similarity(emb(vᵢ), emb(vⱼ))
                   = 1 - (emb(vᵢ)·emb(vⱼ))/(||emb(vᵢ)||·||emb(vⱼ)||)
```

### 1.4. Метрики логической связности

**Определение:** Логическая связность между блоками определяется через граф зависимостей:

```
d_logical(vᵢ, vⱼ) = shortest_path_length(vᵢ, vⱼ) / diameter(G_logic)
```

где G_logic = (V, E_logic) — граф логических зависимостей.

**Типы зависимостей:**
1. **Определение → Использование** (определил термин → использую его)
2. **Проблема → Решение** (поставил задачу → решаю её)
3. **Метод → Применение** (описал метод → применяю к данным)
4. **Результат → Обсуждение** (получил результат → обсуждаю его)

**Матрица зависимостей:**

```
L[i,j] = {
  1,   если vⱼ использует результаты vᵢ
  0,   иначе
}

d_logical(vᵢ, vⱼ) = {
  0,       если L[i,j] = 1 (прямая зависимость)
  ∞,       если L[j,i] = 1 (обратная зависимость — недопустима!)
  BFS_dist, иначе
}
```

### 1.5. Читательская когнитивная нагрузка

**Модель когнитивной нагрузки Свеллера:**

```
CL_reader = CL_intrinsic + CL_extraneous + CL_germane
```

**Для перехода между разделами:**

```
d_reader(vᵢ, vⱼ) = w₁·context_switch_cost(vᵢ, vⱼ) +
                   w₂·working_memory_load(vᵢ, vⱼ) +
                   w₃·prerequisite_retrieval_cost(vᵢ, vⱼ)
```

где:
- **context_switch_cost** — стоимость переключения контекста (↑ при несхожести тем)
- **working_memory_load** — нагрузка на рабочую память (↑ при большом разрыве)
- **prerequisite_retrieval_cost** — стоимость извлечения предпосылок (↑ если они далеко)

---

## 2. Варианты задачи TSP для диссертации

### 2.1. Классическая TSP (базовая модель)

**Применение:** Оптимизация порядка глав верхнего уровня.

**Модель:**
- Вершины = главы диссертации
- Расстояния = когнитивная дистанция между главами
- Цель = минимизировать общую когнитивную нагрузку на читателя

**Алгоритм:**
1. Построить матрицу расстояний D[i,j] = d(vᵢ, vⱼ)
2. Применить алгоритм решения TSP (например, 2-opt, simulated annealing)
3. Зафиксировать начало (введение) и конец (заключение)

### 2.2. TSP с временными окнами (Time Window TSP)

**Применение:** Учет дедлайнов на написание разделов.

**Модель:**
- Каждая глава vᵢ имеет временное окно [earliest_i, latest_i]
- Глава должна быть "посещена" (написана) в этом окне
- Учитывается время написания C(vᵢ)

**Задача:**
```
minimize: J(π) = Σᵢ d(π(i), π(i+1))

при ограничениях:
- earliest_i ≤ start_time(π(i)) ≤ latest_i
- start_time(π(i+1)) = start_time(π(i)) + C(π(i))
```

**Практический пример:**
- Глава "Обзор литературы" должна быть написана в первый год
- Глава "Эксперименты" — после получения данных (месяц 12-18)
- Глава "Обсуждение" — в последние 6 месяцев

### 2.3. Иерархический TSP (Hierarchical TSP)

**Применение:** Оптимизация структуры на нескольких уровнях (главы → разделы → параграфы).

**Модель:**
```
Уровень 1 (макро): Главы
    ↓
Уровень 2 (мезо): Разделы внутри глав
    ↓
Уровень 3 (микро): Параграфы внутри разделов
```

**Алгоритм:**
1. Оптимизировать порядок глав (TSP уровня 1)
2. Для каждой главы оптимизировать порядок разделов (TSP уровня 2)
3. Для каждого раздела оптимизировать порядок параграфов (TSP уровня 3)

**Целевая функция:**
```
J_hierarchical = J_macro + α·J_meso + β·J_micro
```

### 2.4. Multi-depot TSP (несколько авторов/направлений)

**Применение:** Диссертация с несколькими независимыми направлениями исследования.

**Модель:**
- Несколько "складов" (depot) = несколько тематических линий
- Каждая линия имеет свой оптимальный маршрут
- Линии должны сходиться в заключении

**Пример:**
```
Диссертация по биоинформатике:

Depot 1 (Биология):
  → Гл. 1: Биологические основы
  → Гл. 3: Экспериментальные данные
  → Гл. 5: Биологическая валидация

Depot 2 (Информатика):
  → Гл. 2: Вычислительные методы
  → Гл. 4: Алгоритмы анализа
  → Гл. 6: Программная реализация

Финал:
  → Гл. 7: Интеграция результатов (объединение линий)
  → Заключение
```

### 2.5. TSP с обязательными переходами (Precedence Constrained TSP)

**Применение:** Учет строгих логических зависимостей (нельзя использовать метод до его описания).

**Модель:**
- Частично упорядоченное множество (poset) глав
- Некоторые переходы строго предписаны
- Оптимизация оставшихся переходов

**Граф ограничений:**
```
Введение
    ↓ (обязательно)
Постановка задачи
    ↓ (обязательно)
Обзор литературы
    ↓ (обязательно)
[Методы | Эксперименты]  ← оптимизируем порядок этих двух
    ↓ (обязательно)
Результаты
    ↓ (обязательно)
Обсуждение
    ↓ (обязательно)
Заключение
```

### 2.6. Динамическая TSP (Dynamic TSP)

**Применение:** Адаптация структуры по мере написания (появление новых разделов, изменение связей).

**Модель:**
- Множество вершин V(t) изменяется со временем
- Расстояния d(i,j,t) могут меняться (новые открытия, связи)
- Перепланирование маршрута в процессе

**Практический пример:**
```
t=0: Планируем 5 глав
t=6 мес: Добавляется новая глава (неожиданный результат)
t=12 мес: Меняется порядок (новые связи между главами)
t=18 мес: Финальная оптимизация
```

### 2.7. Stochastic TSP (вероятностные оценки)

**Применение:** Учет неопределенности в оценках времени и сложности.

**Модель:**
```
C(vᵢ) ~ Normal(μᵢ, σᵢ²)  — время написания главы (случайная величина)
d(vᵢ, vⱼ) ~ LogNormal(μᵢⱼ, σᵢⱼ²)  — когнитивная дистанция (неопределенная)
```

**Целевая функция:**
```
minimize: E[J(π)] + ρ·Var[J(π)]

где ρ — параметр risk-aversion (избегание риска)
```

---

## 3. Алгоритмы решения

### 3.1. Точные алгоритмы (для малых диссертаций, N < 15 глав)

#### 3.1.1. Динамическое программирование (Held-Karp)

**Алгоритм:**
```python
def dissertation_dp(V, d, start, end):
    """
    V: множество разделов
    d: матрица когнитивных дистанций
    start: введение (обязательно первое)
    end: заключение (обязательно последнее)
    """
    n = len(V)
    # dp[mask][i] = минимальная стоимость маршрута через вершины в mask, заканчивающегося в i
    dp = [[float('inf')] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    # База: начинаем с введения
    dp[1 << start][start] = 0

    # Заполнение таблицы
    for mask in range(1 << n):
        for last in range(n):
            if not (mask & (1 << last)):
                continue
            if dp[mask][last] == float('inf'):
                continue

            for next_v in range(n):
                if mask & (1 << next_v):  # уже посещено
                    continue
                if next_v == end and mask != ((1 << n) - 1) - (1 << end):  # заключение только в конце
                    continue

                new_mask = mask | (1 << next_v)
                new_cost = dp[mask][last] + d[last][next_v]

                if new_cost < dp[new_mask][next_v]:
                    dp[new_mask][next_v] = new_cost
                    parent[new_mask][next_v] = last

    # Восстановление маршрута
    full_mask = (1 << n) - 1
    return reconstruct_path(parent, full_mask, end)

# Сложность: O(n² · 2ⁿ)
# Применимо для: диссертация с 10-15 главами
```

#### 3.1.2. Branch and Bound с отсечением по зависимостям

```python
def branch_and_bound_with_dependencies(V, d, dependencies):
    """
    dependencies: dict {v: [prereq1, prereq2, ...]}
    """
    best_solution = None
    best_cost = float('inf')

    def bound(partial_path, remaining):
        """Нижняя граница для оставшегося пути (оптимистичная оценка)"""
        if not remaining:
            return 0
        # MST на оставшихся вершинах
        mst_cost = minimum_spanning_tree(remaining, d)
        return mst_cost

    def is_valid(partial_path, next_v):
        """Проверка выполнения зависимостей"""
        for prereq in dependencies.get(next_v, []):
            if prereq not in partial_path:
                return False
        return True

    def branch(partial_path, current_cost, remaining):
        nonlocal best_solution, best_cost

        if not remaining:
            if current_cost < best_cost:
                best_cost = current_cost
                best_solution = partial_path.copy()
            return

        # Отсечение: если нижняя граница уже больше лучшего решения
        if current_cost + bound(partial_path, remaining) >= best_cost:
            return

        # Ветвление: перебор возможных следующих вершин
        for next_v in remaining:
            if not is_valid(partial_path, next_v):
                continue

            new_cost = current_cost + d[partial_path[-1]][next_v]
            branch(
                partial_path + [next_v],
                new_cost,
                remaining - {next_v}
            )

    start = 0  # введение
    branch([start], 0, set(V) - {start})
    return best_solution, best_cost
```

### 3.2. Приближенные алгоритмы (для средних диссертаций, N = 15-30)

#### 3.2.1. Жадный алгоритм с ограничениями

```python
def greedy_with_constraints(V, d, dependencies, start, end):
    """
    Жадный выбор ближайшей допустимой вершины
    """
    path = [start]
    remaining = set(V) - {start, end}
    current = start

    while remaining:
        # Выбираем ближайшую вершину, удовлетворяющую зависимостям
        best_next = None
        best_dist = float('inf')

        for v in remaining:
            # Проверка зависимостей
            prereqs_satisfied = all(
                prereq in path for prereq in dependencies.get(v, [])
            )

            if prereqs_satisfied and d[current][v] < best_dist:
                best_next = v
                best_dist = d[current][v]

        if best_next is None:
            # Тупик: нужно backtracking
            # Выбираем любую вершину, добавляя штраф
            best_next = min(remaining, key=lambda v: d[current][v])

        path.append(best_next)
        remaining.remove(best_next)
        current = best_next

    path.append(end)
    return path
```

#### 3.2.2. 2-opt локальная оптимизация

```python
def two_opt_optimize(path, d, dependencies):
    """
    Улучшение маршрута методом 2-opt

    Идея: пробуем переставить пары рёбер, если улучшается
    """
    improved = True

    while improved:
        improved = False

        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path) - 1):
                # Проверяем, не нарушаем ли зависимости при обращении
                if not check_dependencies_after_reversal(path, i, j, dependencies):
                    continue

                # Текущие рёбра: (i-1, i) и (j, j+1)
                # Новые рёбра: (i-1, j) и (i, j+1)
                # Сегмент [i, j] обращается

                old_cost = d[path[i-1]][path[i]] + d[path[j]][path[j+1]]
                new_cost = d[path[i-1]][path[j]] + d[path[i]][path[j+1]]

                if new_cost < old_cost:
                    # Обращаем сегмент [i, j]
                    path[i:j+1] = reversed(path[i:j+1])
                    improved = True
                    break

            if improved:
                break

    return path

def check_dependencies_after_reversal(path, i, j, dependencies):
    """
    Проверка, что после обращения сегмента [i, j] все зависимости сохраняются
    """
    reversed_segment = path[i:j+1][::-1]
    new_path = path[:i] + reversed_segment + path[j+1:]

    for idx, v in enumerate(new_path):
        for prereq in dependencies.get(v, []):
            if prereq not in new_path[:idx]:
                return False
    return True
```

#### 3.2.3. Simulated Annealing (имитация отжига)

```python
import random
import math

def simulated_annealing_dissertation(V, d, dependencies, T_init=1000, alpha=0.95, max_iter=10000):
    """
    Имитация отжига для оптимизации структуры диссертации

    Параметры:
    - T_init: начальная температура
    - alpha: коэффициент охлаждения
    - max_iter: максимум итераций
    """
    # Начальное решение (жадный алгоритм)
    current = greedy_with_constraints(V, d, dependencies, V[0], V[-1])
    current_cost = path_cost(current, d)

    best = current.copy()
    best_cost = current_cost

    T = T_init

    for iteration in range(max_iter):
        # Генерируем соседа
        neighbor = generate_neighbor(current, dependencies)
        neighbor_cost = path_cost(neighbor, d)

        # Принятие решения
        delta = neighbor_cost - current_cost

        if delta < 0:
            # Улучшение — всегда принимаем
            current = neighbor
            current_cost = neighbor_cost

            if current_cost < best_cost:
                best = current.copy()
                best_cost = current_cost
        else:
            # Ухудшение — принимаем с вероятностью exp(-delta/T)
            acceptance_prob = math.exp(-delta / T)
            if random.random() < acceptance_prob:
                current = neighbor
                current_cost = neighbor_cost

        # Охлаждение
        T *= alpha

        if T < 0.01:
            break

    return best, best_cost

def generate_neighbor(path, dependencies):
    """
    Генерация соседнего решения (небольшое изменение пути)
    """
    neighbor = path.copy()

    # Стратегия: swap двух элементов или reversal сегмента
    strategy = random.choice(['swap', 'reversal', 'insert'])

    if strategy == 'swap':
        # Меняем местами две главы
        i, j = random.sample(range(1, len(path)-1), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

    elif strategy == 'reversal':
        # Обращаем сегмент
        i, j = sorted(random.sample(range(1, len(path)-1), 2))
        neighbor[i:j+1] = reversed(neighbor[i:j+1])

    elif strategy == 'insert':
        # Извлекаем элемент и вставляем в другое место
        i = random.randint(1, len(path)-2)
        j = random.randint(1, len(path)-2)
        element = neighbor.pop(i)
        neighbor.insert(j, element)

    # Проверка валидности (зависимости)
    if is_valid_path(neighbor, dependencies):
        return neighbor
    else:
        return path  # возвращаем исходный, если новый невалиден

def is_valid_path(path, dependencies):
    """Проверка выполнения всех зависимостей"""
    for idx, v in enumerate(path):
        for prereq in dependencies.get(v, []):
            if prereq not in path[:idx]:
                return False
    return True

def path_cost(path, d):
    """Стоимость пути"""
    return sum(d[path[i]][path[i+1]] for i in range(len(path)-1))
```

### 3.3. Метаэвристики (для больших диссертаций, N > 30)

#### 3.3.1. Генетический алгоритм

```python
import random

class DissertationGA:
    def __init__(self, V, d, dependencies, pop_size=100, generations=500):
        self.V = V
        self.d = d
        self.dependencies = dependencies
        self.pop_size = pop_size
        self.generations = generations

    def create_individual(self):
        """Создание одной особи (валидной последовательности глав)"""
        start, end = self.V[0], self.V[-1]
        middle = list(set(self.V) - {start, end})

        # Топологическая сортировка с учетом зависимостей
        individual = self.topological_sort_randomized(middle)
        return [start] + individual + [end]

    def topological_sort_randomized(self, vertices):
        """Рандомизированная топологическая сортировка"""
        result = []
        remaining = set(vertices)

        while remaining:
            # Выбираем случайную вершину среди доступных
            available = [
                v for v in remaining
                if all(prereq in result or prereq not in vertices
                       for prereq in self.dependencies.get(v, []))
            ]

            if not available:
                # Cycle detected or error — add any vertex
                available = list(remaining)

            chosen = random.choice(available)
            result.append(chosen)
            remaining.remove(chosen)

        return result

    def fitness(self, individual):
        """Функция приспособленности (минимизируем)"""
        cost = sum(self.d[individual[i]][individual[i+1]]
                   for i in range(len(individual)-1))

        # Штраф за нарушение зависимостей
        penalty = 0
        for idx, v in enumerate(individual):
            for prereq in self.dependencies.get(v, []):
                if prereq not in individual[:idx]:
                    penalty += 1000  # большой штраф

        return cost + penalty

    def selection(self, population):
        """Турнирная селекция"""
        tournament_size = 5
        tournament = random.sample(population, tournament_size)
        return min(tournament, key=self.fitness)

    def crossover(self, parent1, parent2):
        """Упорядоченный кроссовер (Order Crossover, OX)"""
        size = len(parent1)
        start, end = sorted(random.sample(range(1, size-1), 2))

        # Копируем сегмент от parent1
        child = [None] * size
        child[0], child[-1] = parent1[0], parent1[-1]  # фиксируем начало и конец
        child[start:end] = parent1[start:end]

        # Заполняем остальное из parent2
        parent2_filtered = [v for v in parent2 if v not in child]

        idx = 1
        for v in parent2_filtered:
            while child[idx] is not None:
                idx += 1
            if idx >= size - 1:
                break
            child[idx] = v

        return child

    def mutate(self, individual, mutation_rate=0.2):
        """Мутация: swap или reversal"""
        if random.random() < mutation_rate:
            mutated = individual.copy()
            i, j = sorted(random.sample(range(1, len(mutated)-1), 2))

            if random.random() < 0.5:
                # Swap
                mutated[i], mutated[j] = mutated[j], mutated[i]
            else:
                # Reversal
                mutated[i:j+1] = reversed(mutated[i:j+1])

            # Проверка валидности
            if is_valid_path(mutated, self.dependencies):
                return mutated

        return individual

    def evolve(self):
        """Основной цикл генетического алгоритма"""
        # Инициализация популяции
        population = [self.create_individual() for _ in range(self.pop_size)]

        best_individual = min(population, key=self.fitness)
        best_fitness = self.fitness(best_individual)

        for generation in range(self.generations):
            new_population = []

            # Элитизм: сохраняем лучших
            elite_size = self.pop_size // 10
            elite = sorted(population, key=self.fitness)[:elite_size]
            new_population.extend(elite)

            # Создание новых особей
            while len(new_population) < self.pop_size:
                parent1 = self.selection(population)
                parent2 = self.selection(population)

                child = self.crossover(parent1, parent2)
                child = self.mutate(child)

                new_population.append(child)

            population = new_population

            # Обновление лучшего решения
            current_best = min(population, key=self.fitness)
            current_fitness = self.fitness(current_best)

            if current_fitness < best_fitness:
                best_individual = current_best
                best_fitness = current_fitness
                print(f"Generation {generation}: New best fitness = {best_fitness}")

        return best_individual, best_fitness
```

---

## 4. Специальные метрики для диссертаций

### 4.1. Метрика связности (Coherence Score)

**Определение:** Мера того, насколько логично связаны соседние главы.

```
Coherence(π) = (1/n) · Σᵢ₌₁ⁿ⁻¹ similarity(π(i), π(i+1))

где similarity ∈ [0, 1]
```

**Реализация через LDA (Latent Dirichlet Allocation):**

```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

def compute_coherence_score(chapters, n_topics=10):
    """
    Вычисляет связность последовательности глав

    chapters: list of str (тексты глав)
    n_topics: количество тем для LDA
    """
    # Векторизация
    vectorizer = CountVectorizer(max_features=1000, stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(chapters)

    # LDA
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    topic_distributions = lda.fit_transform(doc_term_matrix)

    # Вычисление связности
    coherence_scores = []
    for i in range(len(topic_distributions) - 1):
        theta_i = topic_distributions[i]
        theta_j = topic_distributions[i+1]

        # Jensen-Shannon divergence
        m = 0.5 * (theta_i + theta_j)
        js_div = 0.5 * kl_divergence(theta_i, m) + 0.5 * kl_divergence(theta_j, m)

        # Similarity = 1 - distance
        similarity = 1 - np.sqrt(js_div)
        coherence_scores.append(similarity)

    return np.mean(coherence_scores)

def kl_divergence(p, q):
    """KL дивергенция"""
    epsilon = 1e-10
    return np.sum(p * np.log((p + epsilon) / (q + epsilon)))
```

### 4.2. Метрика зависимостей (Dependency Violation Score)

**Определение:** Количество нарушений логических зависимостей.

```
DV(π) = Σᵢ₌₁ⁿ |{prereq ∈ prerequisites(π(i)) : prereq appears after π(i)}|
```

Чем меньше DV, тем лучше структура.

```python
def dependency_violation_score(path, dependencies):
    """
    Подсчитывает количество нарушений зависимостей

    path: последовательность глав
    dependencies: dict {chapter: [prerequisites]}
    """
    violations = 0

    for idx, chapter in enumerate(path):
        prereqs = dependencies.get(chapter, [])

        for prereq in prereqs:
            if prereq not in path[:idx]:
                violations += 1

    return violations
```

### 4.3. Читательская сложность (Reader Complexity Score)

**Определение:** Оценка когнитивной нагрузки на читателя.

```
RC(π) = Σᵢ₌₁ⁿ⁻¹ [context_switch(π(i), π(i+1)) + memory_load(π, i)]
```

где:
- **context_switch** — стоимость переключения контекста (тематика, методология, стиль)
- **memory_load** — нагрузка на память (сколько нужно помнить из предыдущих глав)

```python
def reader_complexity_score(path, chapters_texts, dependencies):
    """
    Оценка когнитивной сложности для читателя
    """
    total_complexity = 0

    for i in range(len(path) - 1):
        current_chapter = path[i]
        next_chapter = path[i+1]

        # 1. Context switch cost
        context_cost = compute_context_switch_cost(
            chapters_texts[current_chapter],
            chapters_texts[next_chapter]
        )

        # 2. Memory load (сколько глав нужно помнить)
        memory_cost = compute_memory_load(path, i, dependencies)

        total_complexity += context_cost + memory_cost

    return total_complexity

def compute_context_switch_cost(text1, text2):
    """
    Стоимость переключения контекста между двумя текстами

    Использует метрики:
    - Lexical diversity (разнообразие лексики)
    - Sentence structure similarity
    - Topic shift
    """
    # Простая метрика: косинусное расстояние TF-IDF векторов
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    cosine_sim = (tfidf_matrix[0] * tfidf_matrix[1].T).toarray()[0, 0]
    context_cost = 1 - cosine_sim  # чем меньше похожесть, тем больше cost

    return context_cost

def compute_memory_load(path, current_idx, dependencies):
    """
    Нагрузка на рабочую память читателя

    Идея: сколько предыдущих глав нужно держать в голове,
    чтобы понять текущую главу
    """
    current_chapter = path[current_idx]
    prereqs = dependencies.get(current_chapter, [])

    # Считаем, как далеко назад нужно "помнить"
    max_distance = 0
    for prereq in prereqs:
        if prereq in path[:current_idx]:
            distance = current_idx - path.index(prereq)
            max_distance = max(max_distance, distance)

    # Нормализуем: чем дальше назад, тем сложнее помнить
    memory_load = max_distance / len(path) if path else 0

    return memory_load
```

---

## 5. Вычислительная сложность и практические ограничения

### 5.1. Анализ сложности

| Алгоритм | Временная сложность | Пространственная сложность | Оптимальность |
|----------|---------------------|----------------------------|---------------|
| Полный перебор | O(n!) | O(n) | Гарантирована |
| Динамическое программирование | O(n² · 2ⁿ) | O(n · 2ⁿ) | Гарантирована |
| Branch & Bound | O(n!) worst, O(2ⁿ) average | O(n²) | Гарантирована |
| Жадный алгоритм | O(n²) | O(n) | Нет гарантий |
| 2-opt | O(n² · iterations) | O(n) | Локальный оптимум |
| Simulated Annealing | O(n · iterations) | O(n) | Вероятностная |
| Генетический алгоритм | O(pop_size · gen · n) | O(pop_size · n) | Вероятностная |

### 5.2. Рекомендации по выбору алгоритма

```
Количество глав N:

N ≤ 10:  Динамическое программирование (точное решение за секунды)
         → Используйте Held-Karp алгоритм

10 < N ≤ 20: Branch & Bound с хорошими эвристиками
             → Отсечение по зависимостям ускорит в 10-100 раз

20 < N ≤ 50: Комбинация жадного + 2-opt + Simulated Annealing
             → Жадный для начального решения
             → 2-opt для локальной оптимизации
             → SA для глобального улучшения

N > 50: Генетический алгоритм или Ant Colony Optimization
        → Параллелизация на нескольких ядрах
        → Итеративное улучшение
```

---

## 6. Практические формулы для оценки параметров

### 6.1. Оценка времени написания главы

**Эмпирическая формула:**

```
T(chapter) = α · word_count + β · novelty_score + γ · complexity + δ

где:
- word_count: количество слов (обычно 5000-15000 на главу)
- novelty_score ∈ [0, 1]: степень новизны материала (0 = обзор, 1 = новые эксперименты)
- complexity ∈ [0, 1]: сложность изложения
- α ≈ 0.01 час/слово (10 слов в час при написании с нуля)
- β ≈ 50 часов (новый материал требует больше времени)
- γ ≈ 30 часов (сложный материал требует больше итераций)
- δ ≈ 20 часов (базовая стоимость любой главы)
```

**Калибровка:**

```python
def estimate_chapter_time(word_count, novelty, complexity):
    """
    Оценка времени написания главы в часах

    Parameters:
    - word_count: количество слов (int)
    - novelty: [0, 1], 0 = литобзор, 1 = новые эксперименты
    - complexity: [0, 1], 0 = простое изложение, 1 = сложная математика

    Returns:
    - hours: оценка времени в часах
    """
    alpha = 0.01  # час на слово (при написании первого драфта)
    beta = 50     # бонус за новизну
    gamma = 30    # бонус за сложность
    delta = 20    # базовая стоимость

    hours = alpha * word_count + beta * novelty + gamma * complexity + delta

    # Учет вариации (±30%)
    import random
    variation = random.uniform(0.7, 1.3)

    return hours * variation
```

### 6.2. Формула когнитивной дистанции (комбинированная)

**Итоговая формула для d(vᵢ, vⱼ):**

```
d(vᵢ, vⱼ) = w₁·d_semantic(vᵢ, vⱼ) +
            w₂·d_temporal(vᵢ, vⱼ) +
            w₃·d_logical(vᵢ, vⱼ) +
            w₄·d_stylistic(vᵢ, vⱼ)

где веса: w₁ = 0.4, w₂ = 0.2, w₃ = 0.3, w₄ = 0.1 (сумма = 1)
```

**Компоненты:**

1. **d_semantic**: семантическая дистанция
   ```
   d_semantic = 1 - cosine_similarity(emb(vᵢ), emb(vⱼ))
   ```

2. **d_temporal**: временная дистанция
   ```
   d_temporal = |epoch(vᵢ) - epoch(vⱼ)| / max_epoch_diff

   epoch: исторический период (древность=0, средневековье=1, современность=2)
   ```

3. **d_logical**: логическая дистанция
   ```
   d_logical = shortest_dependency_path(vᵢ, vⱼ) / graph_diameter
   ```

4. **d_stylistic**: стилистическая дистанция
   ```
   d_stylistic = |readability(vᵢ) - readability(vⱼ)| / max_diff

   readability: индекс Flesch-Kincaid или аналог
   ```

---

## 7. Теоретические результаты

### Теорема 1: Нижняя граница сложности

**Утверждение:** Задача оптимизации структуры диссертации с ограничениями зависимостей является NP-полной.

**Доказательство:** Сведение к классической TSP с precedence constraints, которая доказана NP-полной.

### Теорема 2: Аппроксимация для метрической диссертационной TSP

**Утверждение:** Если когнитивные дистанции удовлетворяют неравенству треугольника, существует полиномиальный алгоритм с гарантией 1.5-аппроксимации.

**Следствие:** Использование алгоритма Кристофидеса для начального решения.

### Теорема 3: Оптимальность жадного алгоритма при древовидных зависимостях

**Утверждение:** Если граф зависимостей является деревом, жадный алгоритм находит оптимальное решение за O(n log n).

---

## 8. Расширенные модели

### 8.1. Мультикритериальная оптимизация

Вместо одной целевой функции оптимизируем вектор:

```
minimize: J(π) = [J₁(π), J₂(π), J₃(π)]

где:
- J₁ = когнитивная нагрузка на читателя
- J₂ = время написания
- J₃ = количество нарушений зависимостей
```

**Метод:** Парето-оптимизация (NSGA-II, MOEA/D).

### 8.2. Динамическая модель с обучением

Система адаптируется по мере написания:

```
d(vᵢ, vⱼ, t) = d₀(vᵢ, vⱼ) · exp(-λ · similarity_growth(vᵢ, vⱼ, t))

По мере написания связи между главами проясняются → дистанции уменьшаются
```

### 8.3. Учет стиля научного руководителя

Каждый научрук имеет предпочтения по структуре:

```
J_supervisor(π) = Σᵢ preference_weight(vᵢ, position(vᵢ))

Оптимизация: баланс между читабельностью и предпочтениями научрука
```

---

## Заключение теоретической части

Разработанная математическая модель позволяет:

1. **Формализовать** процесс оптимизации структуры диссертации
2. **Применить** богатый арсенал алгоритмов TSP
3. **Измерить** качество структуры количественно
4. **Автоматизировать** поиск оптимального порядка глав
5. **Адаптировать** структуру в процессе написания

**Следующий шаг:** Программная реализация и практические инструменты.
