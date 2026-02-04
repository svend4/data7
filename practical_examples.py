"""
Практические примеры использования системы трансформации знаний

Демонстрирует все возможности системы на реалистичных примерах:
1. Агрегация нескольких диссертаций в энциклопедическую статью
2. Синтез новых диссертационных идей из энциклопедий
3. Рационализация больших графов знаний
4. Комбинированные сценарии

Author: AI Research Assistant
Date: 2026-02-04
"""

from knowledge_transformer import (
    DissertationDecomposer,
    WikiAggregator,
    WikiDecomposer,
    DissertationSynthesizer,
    KnowledgeRationalizer,
    KnowledgeGraph,
    Concept,
    Relation
)


# =============================================================================
# ПРИМЕР 1: АГРЕГАЦИЯ НЕСКОЛЬКИХ ДИССЕРТАЦИЙ
# =============================================================================

def example_multiple_dissertations_to_encyclopedia():
    """
    Пример: Агрегация 3 диссертаций по машинному обучению
    в единую энциклопедическую статью
    """
    print("=" * 80)
    print("ПРИМЕР 1: Агрегация нескольких диссертаций → Энциклопедия")
    print("=" * 80)

    # Три диссертации по разным аспектам ML
    dissertations = [
        {
            'text': """
            Supervised Learning Methods in Computer Vision

            Supervised Learning requires labeled training data for model training.
            Convolutional Neural Networks (CNNs) are the dominant architecture for image classification.
            Data Augmentation techniques improve model generalization by artificially expanding the training set.
            Transfer Learning allows pre-trained models to be fine-tuned on specific tasks.
            ResNet introduced skip connections to enable training of very deep networks.
            Object Detection methods like YOLO and Faster R-CNN localize and classify objects in images.
            Semantic Segmentation assigns class labels to every pixel in an image.
            """,
            'metadata': {
                'source_id': 'PhD_2019_Smith',
                'author': 'Dr. John Smith',
                'year': 2019,
                'university': 'Stanford'
            }
        },
        {
            'text': """
            Unsupervised Representation Learning

            Unsupervised Learning discovers patterns in data without labeled examples.
            Autoencoders learn compressed representations through reconstruction objectives.
            Variational Autoencoders (VAEs) learn probabilistic latent representations.
            Generative Adversarial Networks (GANs) generate realistic synthetic data through adversarial training.
            Self-Supervised Learning creates supervision signals from the data itself.
            Contrastive Learning methods like SimCLR learn representations by comparing augmented views.
            Clustering algorithms like K-Means group similar data points together.
            """,
            'metadata': {
                'source_id': 'PhD_2020_Johnson',
                'author': 'Dr. Sarah Johnson',
                'year': 2020,
                'university': 'MIT'
            }
        },
        {
            'text': """
            Reinforcement Learning for Robotics

            Reinforcement Learning learns optimal policies through interaction with an environment.
            Q-Learning is a value-based method that learns action-value functions.
            Policy Gradient methods directly optimize the policy parameters.
            Actor-Critic methods combine value-based and policy-based approaches.
            Deep Reinforcement Learning uses neural networks as function approximators.
            Model-Based Reinforcement Learning learns environment dynamics for planning.
            Sim-to-Real transfer addresses the reality gap between simulation and real-world deployment.
            """,
            'metadata': {
                'source_id': 'PhD_2021_Chen',
                'author': 'Dr. Wei Chen',
                'year': 2021,
                'university': 'Berkeley'
            }
        }
    ]

    print("\nШаг 1: Декомпозиция диссертаций...")
    decomposer = DissertationDecomposer(use_ml=False)

    all_segments = []
    for diss in dissertations:
        segments = decomposer.decompose(diss['text'], diss['metadata'])
        all_segments.extend(segments)
        print(f"   {diss['metadata']['source_id']}: {len(segments)} сегментов, "
              f"{sum(len(s.concepts) for s in segments)} концептов")

    print(f"\nВсего сегментов: {len(all_segments)}")
    print(f"Всего концептов: {sum(len(s.concepts) for s in all_segments)}")

    print("\nШаг 2: Агрегация в энциклопедическую статью...")
    aggregator = WikiAggregator(target_length=2000)
    article = aggregator.aggregate(all_segments, topic="Machine Learning")

    print("\nШаг 3: Результат (первые 1000 символов):\n")
    print(article[:1000])
    print("\n[... продолжение статьи ...]")

    print("\nСтатистика статьи:")
    print(f"   Длина: {len(article)} символов")
    print(f"   Источники: {len(dissertations)} диссертации")
    print(f"   Авторы: {', '.join(d['metadata']['author'] for d in dissertations)}")

    print("\n" + "=" * 80 + "\n")
    return article


# =============================================================================
# ПРИМЕР 2: СИНТЕЗ ДИССЕРТАЦИЙ ИЗ ЭНЦИКЛОПЕДИЙ
# =============================================================================

def example_encyclopedia_to_dissertation_proposals():
    """
    Пример: Генерация новых диссертационных идей
    из нескольких статей Википедии
    """
    print("=" * 80)
    print("ПРИМЕР 2: Энциклопедии → Новые идеи диссертаций")
    print("=" * 80)

    # Несколько статей Википедии
    wiki_articles = [
        {
            'title': 'Neural Networks',
            'text': """
            Neural Networks are computing systems inspired by biological neural networks.
            Artificial Neural Networks consist of layers of interconnected nodes.
            Activation Functions introduce non-linearity into neural networks.
            Backpropagation is the primary algorithm for training neural networks.
            Deep Neural Networks have multiple hidden layers between input and output.
            Convolutional Neural Networks are specialized for processing grid-like data.
            Recurrent Neural Networks process sequential data through internal memory.
            """
        },
        {
            'title': 'Quantum Computing',
            'text': """
            Quantum Computing uses quantum mechanical phenomena for computation.
            Qubits are the basic units of quantum information.
            Superposition allows qubits to exist in multiple states simultaneously.
            Entanglement creates correlations between quantum particles.
            Quantum Gates manipulate qubits to perform computations.
            Quantum Algorithms like Shor's algorithm solve specific problems efficiently.
            Quantum Error Correction protects quantum information from decoherence.
            """
        },
        {
            'title': 'Graph Theory',
            'text': """
            Graph Theory studies mathematical structures modeling pairwise relations.
            Graphs consist of vertices connected by edges.
            Graph Algorithms solve computational problems on graph structures.
            Shortest Path algorithms find minimal paths between vertices.
            Graph Neural Networks extend deep learning to graph-structured data.
            Community Detection identifies clusters in network data.
            Graph Isomorphism determines structural equivalence between graphs.
            """
        }
    ]

    print("\nШаг 1: Декомпозиция статей в факты...")
    wiki_decomposer = WikiDecomposer(use_ml=False)

    all_facts = []
    for article in wiki_articles:
        facts = wiki_decomposer.decompose(
            article['text'],
            metadata={'source': f"Wikipedia: {article['title']}"}
        )
        all_facts.extend(facts)
        print(f"   {article['title']}: {len(facts)} фактов")

    print(f"\nВсего фактов: {len(all_facts)}")

    # Показать примеры фактов
    print("\nПримеры извлеченных фактов:")
    for i, fact in enumerate(all_facts[:8], 1):
        print(f"   {i}. ({fact.subject}) --[{fact.predicate}]--> ({fact.object})")

    print("\nШаг 2: Синтез диссертационных идей...")
    synthesizer = DissertationSynthesizer(min_novelty=0.5)
    proposals = synthesizer.synthesize(all_facts, domain="Computer Science")

    print(f"\nШаг 3: Сгенерировано {len(proposals)} предложений диссертаций:\n")

    # Показать топ-5 предложений
    for i, proposal in enumerate(proposals[:5], 1):
        print(f"\n{'─' * 70}")
        print(f"Предложение {i}: {proposal['title']}")
        print(f"{'─' * 70}")
        print(f"Тип пробела: {proposal['gap_type']}")
        print(f"Новизна: {proposal['novelty']:.2f} | "
              f"Потенциальное влияние: {proposal['impact']:.2f} | "
              f"Реализуемость: {proposal['feasibility']:.2f}")
        print(f"Общая оценка: {proposal['overall_score']:.2f}")
        print(f"\nОписание:")
        print(f"  {proposal['description']}")
        print(f"\nИсследовательские вопросы:")
        for j, question in enumerate(proposal['research_questions'], 1):
            print(f"  {j}. {question}")

    print("\n" + "=" * 80 + "\n")
    return proposals


# =============================================================================
# ПРИМЕР 3: РАЦИОНАЛИЗАЦИЯ БОЛЬШИХ ГРАФОВ ЗНАНИЙ
# =============================================================================

def example_knowledge_rationalization():
    """
    Пример: Рационализация большого графа знаний
    с демонстрацией всех режимов оптимизации
    """
    print("=" * 80)
    print("ПРИМЕР 3: Рационализация графа знаний")
    print("=" * 80)

    # Создаем большой граф знаний с избыточностью
    print("\nШаг 1: Создание графа знаний...")

    graph = KnowledgeGraph()

    # Определяем структуру AI/ML области
    concepts_hierarchy = {
        'AI': ['ML', 'KnowledgeRepresentation', 'Planning'],
        'ML': ['SupervisedLearning', 'UnsupervisedLearning', 'ReinforcementLearning'],
        'SupervisedLearning': ['Classification', 'Regression'],
        'UnsupervisedLearning': ['Clustering', 'DimensionalityReduction'],
        'Classification': ['SVM', 'DecisionTrees', 'NeuralNetworks'],
        'NeuralNetworks': ['CNN', 'RNN', 'Transformers'],
        'CNN': ['ImageClassification', 'ObjectDetection'],
        'RNN': ['LanguageModeling', 'TimeSeries'],
        'Transformers': ['BERT', 'GPT']
    }

    # Создаем концепты
    all_concept_names = set(['AI'])
    for parent, children in concepts_hierarchy.items():
        all_concept_names.add(parent)
        all_concept_names.update(children)

    concept_map = {}
    for name in all_concept_names:
        concept = Concept(
            id=f"c_{name.lower()}",
            name=name,
            definition=f"Concept representing {name}",
            domain="Artificial Intelligence",
            novelty=0.5
        )
        graph.add_concept(concept)
        concept_map[name] = concept

    # Создаем иерархические связи
    for parent, children in concepts_hierarchy.items():
        for child in children:
            relation = Relation(
                source=concept_map[parent].id,
                target=concept_map[child].id,
                relation_type="includes",
                strength=0.95
            )
            graph.add_relation(relation)

    # Добавляем транзитивные (избыточные) связи
    # Например: AI -> ML -> SupervisedLearning, но также AI -> SupervisedLearning
    redundant_links = [
        ('AI', 'SupervisedLearning'),
        ('AI', 'UnsupervisedLearning'),
        ('AI', 'Classification'),
        ('ML', 'Classification'),
        ('ML', 'Clustering'),
        ('SupervisedLearning', 'SVM'),
        ('SupervisedLearning', 'NeuralNetworks'),
    ]

    for src, tgt in redundant_links:
        if src in concept_map and tgt in concept_map:
            relation = Relation(
                source=concept_map[src].id,
                target=concept_map[tgt].id,
                relation_type="includes",
                strength=0.7  # Более низкая сила для транзитивных связей
            )
            graph.add_relation(relation)

    print(f"   Создано концептов: {len(graph.concepts)}")
    print(f"   Создано связей: {len(graph.relations)}")

    # Тестируем разные режимы оптимизации
    print("\nШаг 2: Рационализация в разных режимах...")

    rationalizer = KnowledgeRationalizer(compression_target=0.6)

    modes = ['compression', 'coverage', 'balanced']
    results = {}

    for mode in modes:
        result = rationalizer.rationalize(graph, optimization_goal=mode)
        results[mode] = result

        print(f"\n   Режим: {mode.upper()}")
        print(f"   ─────────────────────────────────────")
        print(f"   Избыточностей удалено: {result['redundancies_removed']}")
        print(f"   Коэффициент сжатия: {result['compression_ratio']:.2f}")
        print(f"   Сохранено покрытие: {result['coverage_preserved']:.2f}")
        print(f"   Концептов: {result['initial_metrics']['concepts']} → "
              f"{result['final_metrics']['concepts']}")
        print(f"   Связей: {result['initial_metrics']['relations']} → "
              f"{result['final_metrics']['relations']}")

    # Сравнительный анализ
    print("\n\nШаг 3: Сравнительный анализ режимов:")
    print("\n   Режим           | Сжатие | Покрытие | Связей удалено")
    print("   " + "─" * 60)

    for mode in modes:
        r = results[mode]
        relations_removed = (r['initial_metrics']['relations'] -
                           r['final_metrics']['relations'])

        print(f"   {mode:15s} | {r['compression_ratio']:6.2f} | "
              f"{r['coverage_preserved']:8.2f} | {relations_removed:14d}")

    print("\n   Рекомендации:")
    print("   • 'compression' - для минимизации избыточности")
    print("   • 'coverage' - для сохранения всей информации")
    print("   • 'balanced' - оптимальный баланс")

    print("\n" + "=" * 80 + "\n")
    return results


# =============================================================================
# ПРИМЕР 4: ПОЛНЫЙ ЦИКЛ РАБОТЫ
# =============================================================================

def example_full_pipeline():
    """
    Пример: Полный цикл трансформации знаний
    Диссертации → Энциклопедия → Новые идеи → Рационализация
    """
    print("=" * 80)
    print("ПРИМЕР 4: Полный цикл трансформации знаний")
    print("=" * 80)

    # Фаза 1: Диссертации → Энциклопедия
    print("\n📚 ФАЗА 1: Диссертации → Энциклопедия")
    print("─" * 70)

    dissertation_text = """
    Quantum Machine Learning: Bridging Two Paradigms

    Quantum Machine Learning combines quantum computing with machine learning.
    Quantum Algorithms can potentially accelerate certain machine learning tasks.
    Variational Quantum Eigensolver (VQE) is used for quantum chemistry simulations.
    Quantum Neural Networks use quantum circuits as computational models.
    Quantum Feature Maps embed classical data into quantum states.
    Hybrid Classical-Quantum models leverage both paradigms.
    Quantum Advantage requires problems where quantum speedup is demonstrable.
    """

    decomposer = DissertationDecomposer(use_ml=False)
    segments = decomposer.decompose(
        dissertation_text,
        metadata={'source_id': 'PhD_QML_2025', 'author': 'Dr. Alice Quantum'}
    )

    print(f"Извлечено сегментов: {len(segments)}")
    print(f"Извлечено концептов: {sum(len(s.concepts) for s in segments)}")

    # Фаза 2: Агрегация в статью
    print("\n📖 ФАЗА 2: Агрегация в энциклопедическую статью")
    print("─" * 70)

    aggregator = WikiAggregator(target_length=1000)
    article = aggregator.aggregate(segments, topic="Quantum Machine Learning")

    print(f"Длина статьи: {len(article)} символов")
    print(f"\nФрагмент статьи:")
    print(article[:400])
    print("...")

    # Фаза 3: Энциклопедия → Новые идеи
    print("\n💡 ФАЗА 3: Генерация новых исследовательских идей")
    print("─" * 70)

    wiki_decomposer = WikiDecomposer(use_ml=False)
    facts = wiki_decomposer.decompose(
        article,
        metadata={'source': 'Generated Encyclopedia Article'}
    )

    print(f"Извлечено фактов: {len(facts)}")

    synthesizer = DissertationSynthesizer(min_novelty=0.4)
    proposals = synthesizer.synthesize(facts, domain="Quantum Computing + ML")

    print(f"Сгенерировано предложений: {len(proposals)}")
    if proposals:
        top_proposal = proposals[0]
        print(f"\nЛучшее предложение: {top_proposal['title']}")
        print(f"Оценка: {top_proposal['overall_score']:.2f}")

    # Фаза 4: Рационализация
    print("\n⚙️  ФАЗА 4: Рационализация графа знаний")
    print("─" * 70)

    # Строим граф из всех сегментов
    knowledge_graph = KnowledgeGraph()
    for segment in segments:
        for concept in segment.concepts:
            knowledge_graph.add_concept(concept)
        for relation in segment.relations:
            knowledge_graph.add_relation(relation)

    print(f"Исходный граф: {len(knowledge_graph.concepts)} концептов, "
          f"{len(knowledge_graph.relations)} связей")

    rationalizer = KnowledgeRationalizer()
    result = rationalizer.rationalize(knowledge_graph, optimization_goal='balanced')

    print(f"Оптимизированный граф: {result['final_metrics']['concepts']} концептов, "
          f"{result['final_metrics']['relations']} связей")
    print(f"Коэффициент сжатия: {result['compression_ratio']:.2f}")

    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА")
    print("─" * 70)
    print(f"  Входные данные: 1 диссертация")
    print(f"  Сегментов обработано: {len(segments)}")
    print(f"  Концептов извлечено: {sum(len(s.concepts) for s in segments)}")
    print(f"  Фактов в энциклопедии: {len(facts)}")
    print(f"  Новых идей сгенерировано: {len(proposals)}")
    print(f"  Финальный граф: {result['final_metrics']['concepts']} концептов")

    print("\n✅ Полный цикл завершен успешно!")
    print("=" * 80 + "\n")


# =============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# =============================================================================

def main():
    """Запуск всех практических примеров"""
    print("\n" + "=" * 80)
    print("СИСТЕМА ТРАНСФОРМАЦИИ ЗНАНИЙ - ПРАКТИЧЕСКИЕ ПРИМЕРЫ")
    print("=" * 80 + "\n")

    # Запуск всех примеров
    try:
        example_multiple_dissertations_to_encyclopedia()
        input("Нажмите Enter для продолжения...")

        example_encyclopedia_to_dissertation_proposals()
        input("Нажмите Enter для продолжения...")

        example_knowledge_rationalization()
        input("Нажмите Enter для продолжения...")

        example_full_pipeline()

        print("\n" + "=" * 80)
        print("✅ ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Выполнение прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
