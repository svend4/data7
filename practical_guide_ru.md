# Практическое руководство: Оптимизация структуры диссертации методами TSP

## Содержание

1. [Введение](#введение)
2. [Быстрый старт](#быстрый-старт)
3. [Подготовка данных о вашей диссертации](#подготовка-данных)
4. [Запуск оптимизации](#запуск-оптимизации)
5. [Интерпретация результатов](#интерпретация-результатов)
6. [Продвинутые сценарии](#продвинутые-сценарии)
7. [Практические советы](#практические-советы)
8. [Решение проблем](#решение-проблем)

---

## Введение

Этот инструмент помогает оптимизировать структуру вашей диссертации, находя оптимальный порядок глав, который:
- Минимизирует когнитивную нагрузку на читателя
- Соблюдает логические зависимости между главами
- Обеспечивает плавный переход между темами
- Оценивает время написания

**Когда использовать:**
- ✅ На этапе планирования структуры (до начала написания)
- ✅ При реструктуризации уже написанного материала
- ✅ Для анализа и улучшения существующей структуры
- ✅ При добавлении новых глав в процессе работы

---

## Быстрый старт

### Шаг 1: Установка зависимостей

```bash
# Основные библиотеки
pip install numpy matplotlib seaborn networkx

# Опционально: для ML-методов
pip install scikit-learn sentence-transformers transformers torch
```

### Шаг 2: Создание описания вашей диссертации

Создайте файл `my_dissertation.py`:

```python
from dissertation_optimizer import Chapter, DissertationOptimizer

# Описываем главы вашей диссертации
chapters = [
    Chapter(
        id="intro",
        title="Введение",
        word_count=3000,
        novelty=0.3,      # 0-1: насколько новый материал
        complexity=0.2,   # 0-1: сложность изложения
        keywords=["цели", "задачи", "актуальность"],
        prerequisites=[],  # нет предпосылок
        epoch=2           # современность
    ),

    Chapter(
        id="literature",
        title="Обзор литературы",
        word_count=15000,
        novelty=0.1,
        complexity=0.4,
        keywords=["анализ", "методы", "теория"],
        prerequisites=["intro"],  # требует введения
        epoch=2
    ),

    # ... добавьте остальные главы

    Chapter(
        id="conclusion",
        title="Заключение",
        word_count=4000,
        novelty=0.2,
        complexity=0.3,
        keywords=["выводы", "результаты"],
        prerequisites=["results"],  # требует результатов
        epoch=2
    )
]

# Создаем оптимизатор
optimizer = DissertationOptimizer(
    chapters=chapters,
    start_chapter_id="intro",      # введение всегда первое
    end_chapter_id="conclusion"    # заключение всегда последнее
)

# Оптимизируем структуру
optimal_path, cost = optimizer.optimize(method='simulated_annealing')

# Выводим результаты
optimizer.print_solution(optimal_path)

# Сохраняем в файл
optimizer.export_results(optimal_path, 'my_dissertation_structure.json')
```

### Шаг 3: Запуск

```bash
python my_dissertation.py
```

**Результат:** Вы получите оптимальный порядок глав и метрики качества структуры.

---

## Подготовка данных о вашей диссертации

### Параметры главы

Каждая глава описывается следующими параметрами:

#### 1. `id` (обязательно)
Уникальный идентификатор главы.

```python
id="chapter_1_theory"
```

**Советы:**
- Используйте осмысленные ID (не просто "ch1", "ch2")
- Можно использовать: `intro`, `lit_review`, `methodology`, `experiments_1`, `results`, `discussion`, `conclusion`

#### 2. `title` (обязательно)
Название главы.

```python
title="Теоретические основы машинного обучения"
```

#### 3. `word_count`
Примерное количество слов в главе.

```python
word_count=12000
```

**Как оценить:**
- Обзор литературы: 10,000-20,000 слов
- Теоретическая глава: 8,000-15,000 слов
- Экспериментальная: 10,000-20,000 слов
- Обсуждение: 8,000-12,000 слов
- Введение/заключение: 3,000-5,000 слов каждое

#### 4. `novelty` (0.0 - 1.0)
Степень новизны материала.

```python
novelty=0.9  # очень новый материал (ваши эксперименты)
novelty=0.1  # обзорный материал (литература)
```

**Шкала:**
- `0.0-0.2`: Обзор существующих работ, устоявшаяся теория
- `0.3-0.5`: Адаптация существующих методов, небольшие модификации
- `0.6-0.8`: Существенные изменения, новые применения
- `0.9-1.0`: Полностью оригинальные результаты, новые методы

#### 5. `complexity` (0.0 - 1.0)
Сложность изложения для читателя.

```python
complexity=0.8  # сложная математика
complexity=0.3  # простое описание
```

**Шкала:**
- `0.0-0.2`: Описательный текст, минимум формул
- `0.3-0.5`: Стандартная научная сложность, некоторые формулы
- `0.6-0.8`: Много математики, доказательства, сложные концепции
- `0.9-1.0`: Очень техническое изложение, требует глубоких знаний

#### 6. `keywords`
Ключевые слова, описывающие тематику главы.

```python
keywords=["нейронные сети", "обучение", "классификация", "PyTorch"]
```

**Зачем:** Используется для вычисления семантического расстояния между главами.

**Советы:**
- 3-10 ключевых слов на главу
- Используйте термины из вашей области
- Избегайте общих слов ("исследование", "анализ")

#### 7. `prerequisites`
Список ID глав, которые должны идти раньше этой.

```python
prerequisites=["intro", "literature", "theory"]
```

**Важно:** Это жесткие ограничения! Алгоритм гарантирует их соблюдение.

**Примеры зависимостей:**
- Эксперименты зависят от методологии
- Обсуждение зависит от результатов
- Применение зависит от методов

#### 8. `epoch`
Исторический период (для исторических диссертаций).

```python
epoch=0  # древность
epoch=1  # средние века
epoch=2  # современность (по умолчанию)
```

**Для большинства диссертаций:** Оставьте `epoch=2` везде.

### Пример: Диссертация по машинному обучению

```python
chapters = [
    Chapter(
        id="intro",
        title="Введение",
        word_count=3500,
        novelty=0.3,
        complexity=0.2,
        keywords=["машинное обучение", "классификация", "мотивация", "цели"],
        prerequisites=[],
        epoch=2
    ),

    Chapter(
        id="ml_basics",
        title="Основы машинного обучения",
        word_count=10000,
        novelty=0.2,
        complexity=0.5,
        keywords=["supervised learning", "нейронные сети", "градиентный спуск"],
        prerequisites=["intro"],
        epoch=2
    ),

    Chapter(
        id="literature",
        title="Обзор существующих подходов",
        word_count=12000,
        novelty=0.1,
        complexity=0.4,
        keywords=["CNNs", "ResNet", "transfer learning", "анализ"],
        prerequisites=["intro", "ml_basics"],
        epoch=2
    ),

    Chapter(
        id="proposed_method",
        title="Предлагаемый метод",
        word_count=15000,
        novelty=0.9,
        complexity=0.8,
        keywords=["novel architecture", "attention mechanism", "формализация"],
        prerequisites=["ml_basics", "literature"],
        epoch=2
    ),

    Chapter(
        id="implementation",
        title="Реализация и детали",
        word_count=8000,
        novelty=0.6,
        complexity=0.6,
        keywords=["PyTorch", "training", "гиперпараметры"],
        prerequisites=["proposed_method"],
        epoch=2
    ),

    Chapter(
        id="experiments",
        title="Экспериментальное исследование",
        word_count=18000,
        novelty=0.8,
        complexity=0.7,
        keywords=["датасеты", "эксперименты", "метрики", "результаты"],
        prerequisites=["implementation"],
        epoch=2
    ),

    Chapter(
        id="analysis",
        title="Анализ результатов",
        word_count=12000,
        novelty=0.7,
        complexity=0.6,
        keywords=["интерпретация", "сравнение", "статистика"],
        prerequisites=["experiments"],
        epoch=2
    ),

    Chapter(
        id="applications",
        title="Практические применения",
        word_count=7000,
        novelty=0.5,
        complexity=0.4,
        keywords=["применение", "кейсы", "внедрение"],
        prerequisites=["analysis"],
        epoch=2
    ),

    Chapter(
        id="conclusion",
        title="Заключение",
        word_count=4000,
        novelty=0.2,
        complexity=0.3,
        keywords=["выводы", "вклад", "перспективы"],
        prerequisites=["analysis", "applications"],
        epoch=2
    )
]
```

---

## Запуск оптимизации

### Метод 1: Жадный алгоритм (быстро, но не оптимально)

```python
path, cost = optimizer.optimize(method='greedy')
```

**Когда использовать:**
- Быстрая оценка (секунды)
- Более 30 глав
- Нужна отправная точка для других методов

### Метод 2: 2-opt оптимизация (быстро, хорошо)

```python
path, cost = optimizer.optimize(
    method='two_opt',
    max_iterations=1000
)
```

**Когда использовать:**
- 10-30 глав
- Нужен баланс скорость/качество
- После жадного для улучшения

### Метод 3: Simulated Annealing (медленно, отлично)

```python
path, cost = optimizer.optimize(
    method='simulated_annealing',
    initial_temp=1000,      # начальная температура
    cooling_rate=0.95,      # скорость охлаждения
    max_iterations=10000    # макс итераций
)
```

**Когда использовать:**
- Менее 20 глав
- Нужно лучшее решение
- Есть время (минуты)

**Настройка параметров:**
- `initial_temp`: 500-2000 (выше = больше исследования)
- `cooling_rate`: 0.9-0.99 (выше = медленнее, но тщательнее)
- `max_iterations`: 5000-50000

### Сравнение методов

```python
# Запускаем все три
greedy_path, greedy_cost = optimizer.optimize(method='greedy')
two_opt_path, two_opt_cost = optimizer.optimize(method='two_opt')
sa_path, sa_cost = optimizer.optimize(method='simulated_annealing')

print(f"Greedy:     {greedy_cost:.2f}")
print(f"2-opt:      {two_opt_cost:.2f} ({((greedy_cost-two_opt_cost)/greedy_cost*100):.1f}% улучшение)")
print(f"Sim.Anneal: {sa_cost:.2f} ({((greedy_cost-sa_cost)/greedy_cost*100):.1f}% улучшение)")

# Выбираем лучший
best_path = min([
    (greedy_path, greedy_cost),
    (two_opt_path, two_opt_cost),
    (sa_path, sa_cost)
], key=lambda x: x[1])

print(f"\n✅ Лучший метод дал улучшение {((greedy_cost-best_path[1])/greedy_cost*100):.1f}%")
```

---

## Интерпретация результатов

### Метрики качества структуры

После оптимизации вы получаете несколько метрик:

#### 1. Когнитивная стоимость (Cognitive Cost)

```
Когнитивная стоимость: 4.25
```

**Что это:** Суммарная "сложность" всех переходов между главами.

**Интерпретация:**
- Чем ниже, тем лучше
- Абсолютное значение зависит от количества глав
- Сравнивайте разные структуры ВАШЕЙ диссертации

**Хорошо ли это значение?**
- Для 8 глав: < 5.0 — отлично, 5-7 — хорошо, > 7 — плохо
- Для 15 глав: < 10 — отлично, 10-15 — хорошо, > 15 — плохо

#### 2. Связность (Coherence)

```
Связность (coherence): 78%
```

**Что это:** Насколько хорошо соседние главы связаны тематически.

**Интерпретация:**
- 80-100%: Отлично! Плавные переходы
- 60-80%: Хорошо, приемлемая структура
- 40-60%: Среднее, есть "прыжки" между темами
- < 40%: Плохо, структура хаотична

**Что делать при низкой связности:**
- Проверьте ключевые слова (keywords) — возможно, недостаточно общих тем
- Рассмотрите добавление переходных разделов
- Возможно, некоторые главы логически не связаны (это нормально для мультидисциплинарных диссертаций)

#### 3. Сложность для читателя (Reader Complexity)

```
Сложность для читателя: 35%
```

**Что это:** Насколько сложно читателю следовать за структурой (нагрузка на память).

**Интерпретация:**
- < 30%: Легко читается, информация свежа в памяти
- 30-50%: Средняя нагрузка, иногда нужно вспоминать
- 50-70%: Высокая нагрузка, часто нужно возвращаться назад
- > 70%: Очень сложно, читатель теряется

**Что делать при высокой сложности:**
- Главы с зависимостями размещайте ближе друг к другу
- Добавьте напоминания (references) к предыдущим главам
- Рассмотрите объединение сильно связанных глав

#### 4. Нарушения зависимостей

```
Нарушения зависимостей: 0
```

**Что это:** Количество случаев, когда глава идет раньше своих предпосылок.

**Важно:** Должно быть 0! Алгоритм гарантирует это.

Если > 0 — это ошибка в алгоритме или данных.

#### 5. Оценка времени написания

```
Оценка времени написания: 720 часов ≈ 18 недель
```

**Что это:** Примерное время на написание всех глав.

**Как используется:**
- Основа для планирования
- Оценка реалистичности сроков
- Распределение усилий

**Формула:**
```
Время(глава) = 0.01 * word_count + 50 * novelty + 30 * complexity + 20
```

---

## Продвинутые сценарии

### Сценарий 1: Визуализация структуры

```python
from dissertation_visualizer import DissertationVisualizer

# Создаем визуализатор
visualizer = DissertationVisualizer(optimizer)

# Генерируем полный отчет с графиками
visualizer.generate_report(
    path=optimal_path,
    output_dir='./my_dissertation_report'
)
```

**Результат:** Папка с графиками:
- `distance_matrix.png` — тепловая карта дистанций
- `dependency_graph.png` — граф зависимостей
- `narrative_flow.png` — поток повествования
- `writing_timeline.png` — временная шкала
- `complexity_flow.png` — динамика сложности

### Сценарий 2: Сравнение вариантов

```python
# У вас есть несколько идей по структуре
manual_structure_1 = ["intro", "literature", "theory", "method", "experiments", "results", "conclusion"]
manual_structure_2 = ["intro", "theory", "literature", "method", "experiments", "results", "conclusion"]

# Оптимальная структура
optimal_structure, _ = optimizer.optimize(method='simulated_annealing')

# Сравниваем
paths = {
    'Ваш вариант 1': manual_structure_1,
    'Ваш вариант 2': manual_structure_2,
    'Оптимизированная': optimal_structure
}

visualizer.plot_path_comparison(paths, save_path='comparison.png')
visualizer.plot_metrics_radar(paths, save_path='metrics_radar.png')
```

### Сценарий 3: ML-based оптимизация (с реальными текстами)

```python
from advanced_methods import SemanticDistanceCalculator

# У вас есть черновики глав
chapter_texts = {
    "intro": "В данной работе исследуется...",
    "literature": "Анализ существующих подходов показывает...",
    # ... остальные тексты
}

# Вычисляем семантические дистанции с помощью BERT
calc = SemanticDistanceCalculator(model_type='sentence-transformers')

texts = [chapter_texts[ch.id] for ch in chapters]
ml_distance_matrix = calc.compute_distance_matrix(texts)

# Заменяем дистанции в оптимизаторе
optimizer.distance_matrix = ml_distance_matrix

# Оптимизируем с реальными семантическими дистанциями
optimal_path, cost = optimizer.optimize(method='simulated_annealing')
```

### Сценарий 4: Многокритериальная оптимизация

```python
from advanced_methods import MultiObjectiveOptimizer

# Хотим оптимизировать сразу несколько целей:
# 1. Когнитивная стоимость
# 2. Время написания
# 3. Связность

mo_optimizer = MultiObjectiveOptimizer(optimizer)

# Находим Парето-фронт решений
pareto_front = mo_optimizer.nsga2_optimize(
    population_size=100,
    generations=300
)

# Исследуем компромиссные решения
for i, solution in enumerate(pareto_front[:5]):
    objectives = mo_optimizer.compute_objectives(solution)
    print(f"\nРешение {i+1}:")
    print(f"  Когнитивная стоимость: {objectives['cognitive_cost']:.2f}")
    print(f"  Время написания: {objectives['writing_time']:.0f} часов")
    print(f"  Связность: {-objectives['coherence']:.2%}")
```

### Сценарий 5: Адаптивная оптимизация в процессе написания

```python
from advanced_methods import AdaptiveLearningOptimizer

# Вы начали писать и обнаружили, что некоторые переходы сложнее, чем ожидалось
adaptive = AdaptiveLearningOptimizer(optimizer)

# Записываем реальный опыт
adaptive.record_writing_session(
    from_chapter="intro",
    to_chapter="literature",
    actual_difficulty=0.2  # оказалось легко
)

adaptive.record_writing_session(
    from_chapter="literature",
    to_chapter="theory",
    actual_difficulty=0.8  # оказалось сложно!
)

# Система обучается и корректирует оценки

# Переоптимизируем для оставшихся глав
remaining = ["method", "experiments", "results", "conclusion"]
new_path = adaptive.reoptimize(remaining)
```

---

## Практические советы

### 1. Когда оптимизировать структуру?

**Оптимальное время:**
- ✅ **На этапе планирования** (до написания)
  - Максимальная польза
  - Легко менять порядок
  - Экономит месяцы работы

- ✅ **После написания 30-50%** (промежуточная оптимизация)
  - У вас есть реальные тексты для ML-анализа
  - Можно скорректировать план оставшихся глав

- ⚠️ **После написания 100%** (реструктуризация)
  - Трудоемко менять порядок
  - Но все еще полезно для улучшения читаемости

### 2. Как выбрать метод оптимизации?

```
Количество глав:

< 10 глав:
  → Simulated Annealing (5-10 минут)
  → Высокое качество, приемлемое время

10-20 глав:
  → 2-opt после жадного (1-5 минут)
  → Хороший баланс

20-50 глав:
  → Жадный алгоритм (секунды)
  → Genetic Algorithm для улучшения (10-30 минут)

> 50 глав:
  → Иерархическая оптимизация
  → Сначала главы, потом разделы внутри глав
```

### 3. Настройка весов дистанций

По умолчанию:
```python
weights = {
    'semantic': 0.4,   # семантическая близость
    'temporal': 0.2,   # временная близость
    'logical': 0.3,    # логические зависимости
    'stylistic': 0.1   # стилистическая близость
}
```

**Когда менять:**

**Диссертация с сильной логической структурой (математика, CS):**
```python
weights = {
    'semantic': 0.3,
    'temporal': 0.1,
    'logical': 0.5,   # ← увеличили
    'stylistic': 0.1
}
```

**Исторические/обзорные диссертации:**
```python
weights = {
    'semantic': 0.4,
    'temporal': 0.4,   # ← увеличили
    'logical': 0.1,
    'stylistic': 0.1
}
```

**Междисциплинарные диссертации:**
```python
weights = {
    'semantic': 0.6,   # ← увеличили (важна тематическая близость)
    'temporal': 0.1,
    'logical': 0.2,
    'stylistic': 0.1
}
```

### 4. Работа с зависимостями

**Типичные зависимости:**

```python
# Обзор литературы → зависит от введения
Chapter(id="literature", prerequisites=["intro"])

# Методология → зависит от обзора и теории
Chapter(id="methodology", prerequisites=["literature", "theory"])

# Эксперименты → зависят от методологии
Chapter(id="experiments", prerequisites=["methodology"])

# Результаты → зависят от экспериментов
Chapter(id="results", prerequisites=["experiments"])

# Обсуждение → зависит от результатов
Chapter(id="discussion", prerequisites=["results"])

# Заключение → зависит от всех результатов
Chapter(id="conclusion", prerequisites=["results", "discussion"])
```

**Ошибки при задании зависимостей:**

❌ **Циклические зависимости:**
```python
Chapter(id="A", prerequisites=["B"])
Chapter(id="B", prerequisites=["A"])
# Невозможно удовлетворить!
```

❌ **Чрезмерные зависимости:**
```python
Chapter(id="conclusion", prerequisites=["intro", "lit", "theory", "method", "exp", "results", "discussion"])
# Слишком строго! Достаточно ["results", "discussion"]
```

✅ **Правильный подход:**
- Указывайте только **прямые** зависимости
- Транзитивные зависимости вычисляются автоматически
- Если A → B и B → C, не нужно указывать A → C

### 5. Оценка параметров глав

**novelty:**
```
Быстрая оценка:
- Переписываете из учебника? → 0.1
- Обзор чужих статей? → 0.2
- Применяете известный метод? → 0.5
- Модифицируете метод? → 0.7
- Создаете новый метод? → 0.9
```

**complexity:**
```
Быстрая оценка:
- Описание без формул? → 0.2
- Стандартные формулы? → 0.4
- Выводы доказательств? → 0.7
- Продвинутая математика? → 0.9
```

### 6. Интерпретация "плохих" результатов

**Высокая когнитивная стоимость:**
- Возможно, ваши главы действительно очень разные тематически
- Это нормально для междисциплинарных работ
- Решение: добавьте переходные разделы

**Низкая связность:**
- Проверьте keywords — возможно, недостаточно общих тем
- Рассмотрите объединение близких глав
- Или разделение очень больших глав на подглавы

**Высокая читательская сложность:**
- Главы с зависимостями далеко друг от друга
- Решение: relaxуйте некоторые зависимости
- Или добавьте краткие напоминания в текст

---

## Решение проблем

### Проблема 1: Алгоритм работает слишком долго

**Причина:** Слишком много глав или итераций.

**Решение:**
```python
# Уменьшите параметры
path, cost = optimizer.optimize(
    method='simulated_annealing',
    initial_temp=500,        # было 1000
    cooling_rate=0.90,       # было 0.95 (быстрее охлаждение)
    max_iterations=2000      # было 10000
)
```

Или используйте более быстрый метод:
```python
path, cost = optimizer.optimize(method='two_opt')
```

### Проблема 2: Невозможно удовлетворить зависимости

**Ошибка:** `ValueError: Cannot satisfy dependencies`

**Причина:** Циклические зависимости или невозможная конфигурация.

**Решение:**
1. Проверьте граф зависимостей:
```python
visualizer.plot_dependency_graph()
```

2. Найдите циклы:
```python
import networkx as nx

G = nx.DiGraph()
for ch in chapters:
    for prereq in ch.prerequisites:
        G.add_edge(prereq, ch.id)

try:
    cycles = list(nx.find_cycle(G))
    print(f"Найдены циклы: {cycles}")
except nx.NetworkXNoCycle:
    print("Циклов нет")
```

3. Разорвите цикл, убрав одну из зависимостей.

### Проблема 3: Результат не отличается от исходного порядка

**Причина:** Зависимости слишком жесткие, практически нет свободы.

**Решение:**
1. Проверьте, действительно ли все зависимости необходимы
2. Relaxуйте некоторые зависимости (например, "желательно" вместо "обязательно")
3. Если структура уже оптимальна — это хорошо!

### Проблема 4: Метрики кажутся странными

**Связность > 90%:**
- Возможно, у вас очень узкая тема
- Или все keywords одинаковые
- Решение: это не проблема, если диссертация действительно очень сфокусирована

**Когнитивная стоимость близка к 0:**
- Главы очень похожи
- Возможно, стоит объединить некоторые

**Время написания кажется нереалистичным:**
- Проверьте `word_count`, `novelty`, `complexity`
- Скорректируйте коэффициенты в формуле:
```python
# В файле dissertation_optimizer.py, метод _estimate_writing_time
alpha = 0.01  # ваша скорость написания (час/слово)
```

---

## Примеры использования

### Пример 1: Минимальная диссертация (5 глав)

```python
chapters = [
    Chapter(id="intro", title="Введение",
            word_count=3000, novelty=0.3, complexity=0.2,
            keywords=["цели", "задачи"], prerequisites=[]),

    Chapter(id="literature", title="Обзор литературы",
            word_count=12000, novelty=0.1, complexity=0.4,
            keywords=["анализ", "методы"], prerequisites=["intro"]),

    Chapter(id="methodology", title="Методология",
            word_count=10000, novelty=0.7, complexity=0.7,
            keywords=["метод", "подход"], prerequisites=["literature"]),

    Chapter(id="results", title="Результаты",
            word_count=15000, novelty=0.9, complexity=0.6,
            keywords=["эксперименты", "данные"], prerequisites=["methodology"]),

    Chapter(id="conclusion", title="Заключение",
            word_count=4000, novelty=0.2, complexity=0.3,
            keywords=["выводы"], prerequisites=["results"])
]

optimizer = DissertationOptimizer(chapters, "intro", "conclusion")
path, cost = optimizer.optimize(method='simulated_annealing')
optimizer.print_solution(path)
```

### Пример 2: Сложная диссертация с ветвлениями

```python
# У вас есть две независимые линии исследования,
# которые сходятся в конце

chapters = [
    Chapter(id="intro", title="Введение", ...),
    Chapter(id="lit", title="Обзор", prerequisites=["intro"]),

    # Линия 1: Теоретическая
    Chapter(id="theory_1", title="Теория, часть 1", prerequisites=["lit"]),
    Chapter(id="theory_2", title="Теория, часть 2", prerequisites=["theory_1"]),

    # Линия 2: Экспериментальная
    Chapter(id="exp_1", title="Эксперимент 1", prerequisites=["lit"]),
    Chapter(id="exp_2", title="Эксперимент 2", prerequisites=["exp_1"]),

    # Объединение
    Chapter(id="integration", title="Интеграция результатов",
            prerequisites=["theory_2", "exp_2"]),

    Chapter(id="conclusion", title="Заключение",
            prerequisites=["integration"])
]

# Оптимизатор найдет оптимальное чередование линий
```

---

## Заключение

Этот инструмент — помощник, а не замена вашему суждению. Используйте результаты как:
- **Отправную точку** для размышлений о структуре
- **Валидацию** вашей интуиции
- **Альтернативу** вашим идеям для сравнения

**Помните:**
- Лучшая структура зависит от вашей области, научного руководителя и традиций
- Алгоритм не знает специфики вашей работы
- Ваш опыт и знание предмета важнее любой оптимизации

**Успехов в написании диссертации!** 🎓
