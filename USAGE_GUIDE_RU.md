# Руководство по использованию системы трансформации знаний

## 📋 Оглавление

1. [Быстрый старт](#быстрый-старт)
2. [Компоненты системы](#компоненты-системы)
3. [Практические сценарии](#практические-сценарии)
4. [API Reference](#api-reference)
5. [Примеры кода](#примеры-кода)
6. [Лучшие практики](#лучшие-практики)
7. [Решение проблем](#решение-проблем)

---

## 🚀 Быстрый старт

### Установка

Система не требует установки зависимостей для базовой функциональности:

```bash
# Клонировать репозиторий
cd /path/to/data7

# Запустить демонстрацию
python3 demo_auto.py
```

### Опциональные зависимости

Для расширенных возможностей (ML-based извлечение):

```bash
pip install numpy scikit-learn transformers
```

### Первый пример

```python
from knowledge_transformer import DissertationDecomposer, WikiAggregator

# 1. Декомпозировать диссертацию
decomposer = DissertationDecomposer()
segments = decomposer.decompose(
    dissertation_text,
    metadata={'author': 'John Doe', 'year': 2024}
)

# 2. Агрегировать в энциклопедическую статью
aggregator = WikiAggregator(target_length=2000)
article = aggregator.aggregate(segments, topic="Machine Learning")

print(article)
```

---

## 🧩 Компоненты системы

### 1. DissertationDecomposer

**Назначение**: Разбиение диссертации на тематические сегменты с извлечением концептов.

**Ключевые методы**:
- `decompose(text, metadata)` - основной метод декомпозиции

**Параметры**:
- `use_ml: bool` - использовать ML для кластеризации (требует sklearn)

**Пример**:
```python
decomposer = DissertationDecomposer(use_ml=False)
segments = decomposer.decompose(
    dissertation_text,
    metadata={
        'source_id': 'PhD_2024_001',
        'author': 'Dr. Smith',
        'university': 'MIT',
        'year': 2024
    }
)

print(f"Извлечено {len(segments)} сегментов")
for seg in segments:
    print(f"  Сегмент: {len(seg.concepts)} концептов, {len(seg)} слов")
```

---

### 2. WikiAggregator

**Назначение**: Объединение сегментов из нескольких диссертаций в единую энциклопедическую статью.

**Ключевые методы**:
- `aggregate(segments, topic)` - создание энциклопедической статьи

**Параметры**:
- `target_length: int` - целевая длина статьи в словах

**Пример**:
```python
# Агрегировать сегменты из 3 диссертаций
aggregator = WikiAggregator(target_length=5000)
article = aggregator.aggregate(all_segments, topic="Neural Networks")

# Сохранить статью
with open('wiki_article.md', 'w', encoding='utf-8') as f:
    f.write(article)
```

---

### 3. WikiDecomposer

**Назначение**: Извлечение структурированных фактов (SPO триплетов) из энциклопедических статей.

**Ключевые методы**:
- `decompose(wiki_text, metadata)` - извлечение фактов

**Параметры**:
- `use_ml: bool` - использовать NLP для извлечения триплетов

**Пример**:
```python
wiki_decomposer = WikiDecomposer()
facts = wiki_decomposer.decompose(
    wiki_article,
    metadata={'source': 'Wikipedia: Machine Learning'}
)

for fact in facts:
    print(f"({fact.subject}) --{fact.predicate}--> ({fact.object})")
```

---

### 4. DissertationSynthesizer

**Назначение**: Генерация новых идей диссертаций на основе фактов из энциклопедий.

**Ключевые методы**:
- `synthesize(facts, domain)` - генерация предложений диссертаций

**Параметры**:
- `min_novelty: float` - минимальный порог новизны (0-1)

**Пример**:
```python
synthesizer = DissertationSynthesizer(min_novelty=0.6)
proposals = synthesizer.synthesize(facts, domain="Computer Science")

# Топ-3 предложения
for i, prop in enumerate(proposals[:3], 1):
    print(f"\n{i}. {prop['title']}")
    print(f"   Новизна: {prop['novelty']:.2f}")
    print(f"   Влияние: {prop['impact']:.2f}")
    print(f"   Реализуемость: {prop['feasibility']:.2f}")
    print(f"   Описание: {prop['description']}")
```

---

### 5. KnowledgeRationalizer

**Назначение**: Оптимизация графов знаний через удаление избыточности.

**Ключевые методы**:
- `rationalize(graph, optimization_goal)` - рационализация графа

**Параметры**:
- `compression_target: float` - целевой коэффициент сжатия (0-1)

**Режимы оптимизации**:
- `"compression"` - максимальное сжатие
- `"coverage"` - максимальное покрытие
- `"balanced"` - баланс между сжатием и покрытием

**Пример**:
```python
rationalizer = KnowledgeRationalizer(compression_target=0.5)
result = rationalizer.rationalize(
    knowledge_graph,
    optimization_goal='balanced'
)

print(f"Сжатие: {result['compression_ratio']:.2f}")
print(f"Покрытие сохранено: {result['coverage_preserved']:.2f}")
print(f"Удалено избыточностей: {result['redundancies_removed']}")
```

---

## 💼 Практические сценарии

### Сценарий 1: Создание обзорной статьи

**Задача**: Объединить 5 диссертаций по теме "Квантовые вычисления" в обзорную статью.

```python
from knowledge_transformer import DissertationDecomposer, WikiAggregator

# Список диссертаций
dissertations = [
    {'text': text1, 'metadata': {'author': 'Smith', 'year': 2020}},
    {'text': text2, 'metadata': {'author': 'Jones', 'year': 2021}},
    # ... еще 3
]

# Декомпозиция
decomposer = DissertationDecomposer()
all_segments = []
for diss in dissertations:
    segments = decomposer.decompose(diss['text'], diss['metadata'])
    all_segments.extend(segments)

# Агрегация
aggregator = WikiAggregator(target_length=3000)
review_article = aggregator.aggregate(
    all_segments,
    topic="Quantum Computing: Recent Advances"
)

# Сохранить
with open('quantum_review.md', 'w') as f:
    f.write(review_article)
```

---

### Сценарий 2: Поиск новых исследовательских направлений

**Задача**: Найти пробелы в знаниях на стыке нейронных сетей и квантовых вычислений.

```python
from knowledge_transformer import WikiDecomposer, DissertationSynthesizer

# Загрузить статьи Википедии
wiki_articles = [
    "Neural Networks article text...",
    "Quantum Computing article text...",
    "Graph Theory article text..."
]

# Извлечь факты
wiki_decomposer = WikiDecomposer()
all_facts = []
for article in wiki_articles:
    facts = wiki_decomposer.decompose(article, {})
    all_facts.extend(facts)

# Синтезировать идеи
synthesizer = DissertationSynthesizer(min_novelty=0.7)
proposals = synthesizer.synthesize(
    all_facts,
    domain="Quantum Machine Learning"
)

# Вывести топ-5
for i, prop in enumerate(proposals[:5], 1):
    print(f"\n{'='*60}")
    print(f"Идея {i}: {prop['title']}")
    print(f"{'='*60}")
    print(f"Оценка: {prop['overall_score']:.2f}")
    print(f"\nОписание:\n{prop['description']}\n")
    print("Исследовательские вопросы:")
    for q in prop['research_questions']:
        print(f"  • {q}")
```

---

### Сценарий 3: Оптимизация большой базы знаний

**Задача**: Уменьшить избыточность в корпоративной базе знаний на 40%.

```python
from knowledge_transformer import KnowledgeGraph, KnowledgeRationalizer, Concept, Relation

# Построить граф из существующей базы
graph = KnowledgeGraph()

# Добавить концепты и связи
for concept_data in corporate_knowledge_base:
    concept = Concept(
        id=concept_data['id'],
        name=concept_data['name'],
        definition=concept_data['definition'],
        domain=concept_data['domain']
    )
    graph.add_concept(concept)

for relation_data in corporate_relations:
    relation = Relation(
        source=relation_data['from'],
        target=relation_data['to'],
        relation_type=relation_data['type'],
        strength=relation_data['strength']
    )
    graph.add_relation(relation)

# Рационализировать
rationalizer = KnowledgeRationalizer(compression_target=0.6)
result = rationalizer.rationalize(graph, optimization_goal='compression')

print(f"Исходный размер: {result['initial_metrics']['size']}")
print(f"Оптимизированный: {result['final_metrics']['size']}")
print(f"Экономия: {(1 - result['compression_ratio']) * 100:.1f}%")

# Сохранить оптимизированный граф
optimized_graph = result['optimized_graph']
# ... экспорт в вашу систему
```

---

## 📚 API Reference

### Структуры данных

#### Concept
```python
@dataclass
class Concept:
    id: str                    # Уникальный идентификатор
    name: str                  # Название концепта
    definition: str            # Определение
    domain: str                # Область знания
    novelty: float = 0.5       # Новизна (0-1)
    certainty: float = 0.9     # Достоверность (0-1)
    sources: List[str] = []    # Источники
    attributes: Dict = {}      # Дополнительные атрибуты
```

#### Relation
```python
@dataclass
class Relation:
    source: str                # ID концепта-источника
    target: str                # ID концепта-цели
    relation_type: str         # Тип связи (is_a, part_of, causes, etc.)
    strength: float = 1.0      # Сила связи (0-1)
    bidirectional: bool = False # Двунаправленная связь
```

#### Segment
```python
@dataclass
class Segment:
    id: str                    # Уникальный ID
    text: str                  # Текст сегмента
    concepts: List[Concept]    # Концепты в сегменте
    relations: List[Relation]  # Связи между концептами
    context: str               # Контекст/тема
    metadata: Dict = {}        # Метаданные
```

#### Fact
```python
@dataclass
class Fact:
    subject: str               # Субъект (S)
    predicate: str             # Предикат (P)
    object: str                # Объект (O)
    certainty: float = 1.0     # Достоверность
    sources: List[str] = []    # Источники
    context: str = ""          # Контекст
```

---

## 🎯 Лучшие практики

### 1. Декомпозиция диссертаций

✅ **Рекомендуется**:
- Предварительно очистить текст от форматирования
- Включить метаданные (автор, год, университет)
- Использовать `use_ml=True` для больших текстов (>10000 слов)

❌ **Не рекомендуется**:
- Декомпозировать несколько диссертаций одним вызовом
- Игнорировать метаданные (теряется отслеживаемость)

### 2. Агрегация в энциклопедии

✅ **Рекомендуется**:
- Группировать сегменты по теме перед агрегацией
- Устанавливать `target_length` в зависимости от аудитории
  - 1000-2000 слов: краткий обзор
  - 3000-5000 слов: полный обзор
  - 5000+ слов: детальная статья
- Проверять качество источников

❌ **Не рекомендуется**:
- Агрегировать более 50 сегментов за раз (теряется фокус)
- Смешивать сильно различающиеся темы

### 3. Синтез диссертаций

✅ **Рекомендуется**:
- Использовать `min_novelty >= 0.6` для PhD уровня
- Комбинировать факты из 3-5 различных источников
- Вручную проверять топ предложения

❌ **Не рекомендуется**:
- Слишком низкий `min_novelty` (<0.4) - много шума
- Слишком высокий `min_novelty` (>0.9) - мало результатов

### 4. Рационализация

✅ **Рекомендуется**:
- Начинать с режима `"balanced"`
- Делать бэкап перед агрессивным сжатием
- Проверять `coverage_preserved > 0.8`

❌ **Не рекомендуется**:
- Использовать `"compression"` для критичных данных
- Рационализировать графы с <50 узлами (незначительный эффект)

---

## 🔧 Решение проблем

### Проблема 1: Слишком много сегментов

**Симптомы**: `decompose()` возвращает >50 сегментов

**Решение**:
```python
# Увеличить размер сегментов через параметры кластеризации
decomposer = DissertationDecomposer(use_ml=True)
# ML-кластеризация создает более крупные, семантически связные сегменты
```

### Проблема 2: Нет предложений диссертаций

**Симптомы**: `synthesize()` возвращает пустой список

**Решение**:
```python
# Уменьшить порог новизны
synthesizer = DissertationSynthesizer(min_novelty=0.4)  # вместо 0.7

# Или добавить больше источников фактов
```

### Проблема 3: Низкое качество агрегации

**Симптомы**: Статья содержит повторы или несвязные фрагменты

**Решение**:
```python
# Предварительная фильтрация сегментов
filtered_segments = [
    seg for seg in segments
    if len(seg.concepts) >= 3  # Только содержательные сегменты
]

aggregator = WikiAggregator(target_length=3000)
article = aggregator.aggregate(filtered_segments, topic)
```

### Проблема 4: Слишком агрессивное сжатие

**Симптомы**: `coverage_preserved < 0.5`

**Решение**:
```python
# Использовать более мягкий режим
result = rationalizer.rationalize(graph, optimization_goal='balanced')
# Или даже 'coverage' для сохранения всех данных
```

---

## 📊 Метрики качества

### Для агрегации

- **Coverage** (покрытие): какая доля исходных концептов включена
- **Coherence** (связность): средняя сила связей между концептами
- **Diversity** (разнообразие): количество уникальных источников
- **Redundancy** (избыточность): доля дублирующихся концептов

```python
# Вычислить метрики вручную
def evaluate_aggregation(article, original_segments):
    original_concepts = set()
    for seg in original_segments:
        original_concepts.update(c.name for c in seg.concepts)

    # Извлечь концепты из статьи (упрощенно)
    article_concepts = set(re.findall(r'\*\*([^*]+)\*\*', article))

    coverage = len(article_concepts & original_concepts) / len(original_concepts)
    return {'coverage': coverage}
```

### Для синтеза

- **Novelty** (новизна): насколько идея отличается от существующих
- **Impact** (влияние): потенциальная значимость
- **Feasibility** (реализуемость): практическая выполнимость
- **Overall Score**: комбинированная оценка

Эти метрики возвращаются автоматически в каждом предложении.

---

## 🔗 Дополнительные ресурсы

- **Теория**: `knowledge_transformation_theory.md`
- **Практические примеры**: `practical_examples.py`
- **Автоматическая демонстрация**: `demo_auto.py`
- **Основной модуль**: `knowledge_transformer.py`
- **Мастер README**: `README_MASTER.md`

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте раздел "Решение проблем" выше
2. Запустите `demo_auto.py` для проверки базовой функциональности
3. Изучите примеры в `practical_examples.py`
4. Обратитесь к теоретическому обоснованию в `knowledge_transformation_theory.md`

---

**Версия**: 1.0
**Дата**: 2026-02-04
**Автор**: AI Research Assistant
