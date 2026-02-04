"""
Knowledge Transformation System
Система двунаправленной трансформации научных знаний

Направления:
1. Диссертации → Энциклопедии (декомпозиция + агрегация)
2. Энциклопедии → Диссертации (декомпозиция + синтез)
3. Рационализация научного знания

Author: AI Research Assistant
Date: 2026-02-04
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json
import re


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Concept:
    """Концепт - атомарная единица знания"""
    id: str
    name: str
    definition: str
    domain: str  # область знания
    novelty: float = 0.5  # 0-1
    certainty: float = 0.9  # достоверность 0-1
    sources: List[str] = field(default_factory=list)
    attributes: Dict = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


@dataclass
class Relation:
    """Связь между концептами"""
    source: str  # concept_id
    target: str  # concept_id
    relation_type: str  # is_a, part_of, causes, etc.
    strength: float = 1.0
    bidirectional: bool = False


@dataclass
class Segment:
    """Сегмент текста (фрагмент диссертации)"""
    id: str
    text: str
    concepts: List[Concept]
    relations: List[Relation]
    context: str  # тематика
    metadata: Dict = field(default_factory=dict)

    def __len__(self):
        return len(self.text.split())


@dataclass
class Fact:
    """Факт из энциклопедии (SPO триплет)"""
    subject: str
    predicate: str
    object: str
    certainty: float = 1.0
    sources: List[str] = field(default_factory=list)
    context: str = ""


# ============================================================================
# KNOWLEDGE GRAPH
# ============================================================================

class KnowledgeGraph:
    """Граф научных знаний"""

    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.relations: List[Relation] = []
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)

    def add_concept(self, concept: Concept):
        """Добавить концепт"""
        self.concepts[concept.id] = concept

    def add_relation(self, relation: Relation):
        """Добавить связь"""
        self.relations.append(relation)
        self.adjacency[relation.source].add(relation.target)
        if relation.bidirectional:
            self.adjacency[relation.target].add(relation.source)

    def get_neighbors(self, concept_id: str) -> Set[str]:
        """Получить соседей концепта"""
        return self.adjacency.get(concept_id, set())

    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """BFS поиск пути между концептами"""
        if source_id not in self.concepts or target_id not in self.concepts:
            return None

        from collections import deque

        queue = deque([(source_id, [source_id])])
        visited = {source_id}

        while queue:
            current, path = queue.popleft()

            if len(path) > max_depth:
                continue

            if current == target_id:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_subgraph(self, concept_ids: Set[str]) -> 'KnowledgeGraph':
        """Извлечь подграф"""
        subgraph = KnowledgeGraph()

        for cid in concept_ids:
            if cid in self.concepts:
                subgraph.add_concept(self.concepts[cid])

        for relation in self.relations:
            if relation.source in concept_ids and relation.target in concept_ids:
                subgraph.add_relation(relation)

        return subgraph

    def merge(self, other: 'KnowledgeGraph'):
        """Объединить с другим графом"""
        # Добавить концепты
        for concept in other.concepts.values():
            if concept.id not in self.concepts:
                self.add_concept(concept)
            else:
                # Объединить источники
                self.concepts[concept.id].sources.extend(concept.sources)

        # Добавить связи
        for relation in other.relations:
            # Проверка на дубликаты
            if not any(r.source == relation.source and r.target == relation.target
                      and r.relation_type == relation.relation_type
                      for r in self.relations):
                self.add_relation(relation)

    def compute_centrality(self) -> Dict[str, float]:
        """Вычислить центральность концептов (простой PageRank)"""
        n = len(self.concepts)
        if n == 0:
            return {}

        # Инициализация
        pr = {cid: 1.0 / n for cid in self.concepts}
        damping = 0.85
        iterations = 20

        for _ in range(iterations):
            new_pr = {}

            for cid in self.concepts:
                # Сумма вкладов от соседей
                incoming_pr = 0.0

                for neighbor_id in self.concepts:
                    if cid in self.get_neighbors(neighbor_id):
                        out_degree = len(self.get_neighbors(neighbor_id))
                        if out_degree > 0:
                            incoming_pr += pr[neighbor_id] / out_degree

                new_pr[cid] = (1 - damping) / n + damping * incoming_pr

            pr = new_pr

        return pr


# ============================================================================
# DISSERTATION DECOMPOSER
# ============================================================================

class DissertationDecomposer:
    """Декомпозиция диссертации в сегменты"""

    def __init__(self, use_ml: bool = False):
        """
        Parameters:
        -----------
        use_ml: использовать ML для извлечения концептов
        """
        self.use_ml = use_ml

        if use_ml:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.decomposition import LatentDirichletAllocation
                self.vectorizer = TfidfVectorizer(max_features=1000)
                self.lda = LatentDirichletAllocation(n_components=10)
            except ImportError:
                print("⚠ ML libraries not available, using rule-based methods")
                self.use_ml = False

    def decompose(self, dissertation_text: str, metadata: Dict = None) -> List[Segment]:
        """
        Декомпозировать диссертацию в сегменты

        Parameters:
        -----------
        dissertation_text: текст диссертации
        metadata: метаданные (автор, год, область)

        Returns:
        --------
        segments: список сегментов
        """
        # Шаг 1: Разбиение на параграфы
        paragraphs = self._split_into_paragraphs(dissertation_text)

        # Шаг 2: Тематическая кластеризация
        if self.use_ml:
            clusters = self._cluster_paragraphs_ml(paragraphs)
        else:
            clusters = self._cluster_paragraphs_simple(paragraphs)

        # Шаг 3: Формирование сегментов
        segments = []
        for topic_id, paras in clusters.items():
            text = "\n\n".join(paras)

            # Извлечение концептов
            concepts = self._extract_concepts(text)

            # Извлечение связей
            relations = self._extract_relations(concepts, text)

            segment = Segment(
                id=f"seg_{len(segments)}",
                text=text,
                concepts=concepts,
                relations=relations,
                context=f"topic_{topic_id}",
                metadata=metadata or {}
            )

            segments.append(segment)

        return segments

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Разбить на параграфы"""
        # Простое разбиение по двойным переносам
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs

    def _cluster_paragraphs_simple(self, paragraphs: List[str]) -> Dict[int, List[str]]:
        """Простая кластеризация по ключевым словам"""
        # Очень упрощенная версия
        clusters = defaultdict(list)

        for para in paragraphs:
            # Присваиваем кластер по хэшу
            cluster_id = hash(para[:50]) % 5
            clusters[cluster_id].append(para)

        return clusters

    def _cluster_paragraphs_ml(self, paragraphs: List[str]) -> Dict[int, List[str]]:
        """ML-based кластеризация"""
        # TF-IDF + LDA
        tfidf = self.vectorizer.fit_transform(paragraphs)
        topic_distributions = self.lda.fit_transform(tfidf)

        clusters = defaultdict(list)

        for i, para in enumerate(paragraphs):
            # Доминирующая тема
            topic_id = np.argmax(topic_distributions[i])
            clusters[topic_id].append(para)

        return clusters

    def _extract_concepts(self, text: str) -> List[Concept]:
        """Извлечь концепты из текста"""
        # Упрощенная версия: извлекаем существительные фразы
        concepts = []

        # Простое извлечение: слова с заглавной буквы (потенциальные термины)
        words = text.split()
        terms = set()

        for i, word in enumerate(words):
            # Ищем капитализированные термины
            if word[0].isupper() and not (i == 0 or words[i-1][-1] in '.!?'):
                # Многословные термины
                term = [word]
                j = i + 1
                while j < len(words) and words[j][0].isupper():
                    term.append(words[j])
                    j += 1

                term_str = ' '.join(term)
                if len(term_str) > 3:  # фильтруем короткие
                    terms.add(term_str)

        # Создаем концепты
        for idx, term in enumerate(terms):
            concept = Concept(
                id=f"concept_{hash(term) % 10000}",
                name=term,
                definition=f"Concept extracted from text: {term}",
                domain="extracted",
                novelty=0.5,
                sources=[]
            )
            concepts.append(concept)

        return concepts

    def _extract_relations(self, concepts: List[Concept], text: str) -> List[Relation]:
        """Извлечь связи между концептами"""
        relations = []

        # Простая эвристика: если два концепта в одном предложении, они связаны
        sentences = re.split(r'[.!?]', text)

        for sentence in sentences:
            sentence_concepts = [c for c in concepts if c.name in sentence]

            # Создаем связи между всеми парами в предложении
            for i, c1 in enumerate(sentence_concepts):
                for c2 in sentence_concepts[i+1:]:
                    relation = Relation(
                        source=c1.id,
                        target=c2.id,
                        relation_type="related_to",
                        strength=0.7
                    )
                    relations.append(relation)

        return relations


# ============================================================================
# WIKI AGGREGATOR
# ============================================================================

class WikiAggregator:
    """Агрегация сегментов диссертаций в энциклопедическую статью"""

    def __init__(self, target_length: int = 5000):
        """
        Parameters:
        -----------
        target_length: целевая длина статьи в словах
        """
        self.target_length = target_length

    def aggregate(self, segments: List[Segment], topic: str) -> str:
        """
        Агрегировать сегменты в энциклопедическую статью

        Parameters:
        -----------
        segments: сегменты из разных диссертаций
        topic: целевая тема статьи

        Returns:
        --------
        article_text: текст энциклопедической статьи с цитированиями
        """
        # Шаг 1: Построить граф концептов
        knowledge_graph = self._build_knowledge_graph(segments)

        # Шаг 2: Кластеризовать концепты
        clusters = self._cluster_concepts(knowledge_graph)

        # Шаг 3: Выбрать центральные концепты
        central_concepts = self._select_central_concepts(clusters, knowledge_graph)

        # Шаг 4: Построить структуру статьи
        structure = self._build_article_structure(central_concepts, knowledge_graph)

        # Шаг 5: Генерировать текст
        article_text = self._generate_article_text(structure, segments, knowledge_graph)

        return article_text

    def _build_knowledge_graph(self, segments: List[Segment]) -> KnowledgeGraph:
        """Построить граф знаний из сегментов"""
        graph = KnowledgeGraph()

        for segment in segments:
            for concept in segment.concepts:
                graph.add_concept(concept)

            for relation in segment.relations:
                graph.add_relation(relation)

        return graph

    def _cluster_concepts(self, graph: KnowledgeGraph) -> List[List[str]]:
        """Кластеризовать концепты"""
        # Упрощенная версия: используем связность
        concept_ids = list(graph.concepts.keys())
        clusters = []
        visited = set()

        for cid in concept_ids:
            if cid in visited:
                continue

            # BFS для нахождения компоненты связности
            cluster = self._bfs_component(graph, cid)
            visited.update(cluster)
            clusters.append(cluster)

        return clusters

    def _bfs_component(self, graph: KnowledgeGraph, start: str) -> List[str]:
        """BFS для нахождения компоненты связности"""
        from collections import deque

        component = []
        queue = deque([start])
        visited = {start}

        while queue:
            current = queue.popleft()
            component.append(current)

            for neighbor in graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return component

    def _select_central_concepts(self, clusters: List[List[str]],
                                graph: KnowledgeGraph) -> List[str]:
        """Выбрать центральные концепты из каждого кластера"""
        centrality = graph.compute_centrality()
        central_concepts = []

        for cluster in clusters:
            # Выбираем концепт с максимальной центральностью
            best = max(cluster, key=lambda c: centrality.get(c, 0))
            central_concepts.append(best)

        # Сортируем по центральности
        central_concepts.sort(key=lambda c: centrality.get(c, 0), reverse=True)

        return central_concepts

    def _build_article_structure(self, central_concepts: List[str],
                                 graph: KnowledgeGraph) -> Dict:
        """Построить структуру статьи"""
        structure = {
            'title': 'Generated Encyclopedia Article',
            'introduction': central_concepts[:3] if len(central_concepts) >= 3 else central_concepts,
            'main_sections': [],
            'conclusion': []
        }

        # Разбиваем на секции по 3-5 концептов
        remaining = central_concepts[3:]
        section_size = 4

        for i in range(0, len(remaining), section_size):
            section_concepts = remaining[i:i+section_size]
            structure['main_sections'].append({
                'title': f"Section {len(structure['main_sections']) + 1}",
                'concepts': section_concepts
            })

        return structure

    def _generate_article_text(self, structure: Dict, segments: List[Segment],
                               graph: KnowledgeGraph) -> str:
        """Сгенерировать текст статьи"""
        lines = []

        # Заголовок
        lines.append(f"# {structure['title']}\n")

        # Введение
        lines.append("## Introduction\n")
        for concept_id in structure['introduction']:
            concept = graph.concepts.get(concept_id)
            if concept:
                lines.append(f"**{concept.name}**: {concept.definition}")

                # Найти сегменты, содержащие этот концепт
                sources = self._find_concept_sources(concept_id, segments)
                if sources:
                    lines.append(f" [Sources: {', '.join(sources)}]")

                lines.append("\n")

        # Основные секции
        for section in structure['main_sections']:
            lines.append(f"## {section['title']}\n")

            for concept_id in section['concepts']:
                concept = graph.concepts.get(concept_id)
                if concept:
                    lines.append(f"**{concept.name}**: {concept.definition}\n")

                    # Связанные концепты
                    related = graph.get_neighbors(concept_id)
                    if related:
                        related_names = [graph.concepts[r].name for r in list(related)[:3]
                                       if r in graph.concepts]
                        if related_names:
                            lines.append(f"*Related concepts*: {', '.join(related_names)}\n")

                    sources = self._find_concept_sources(concept_id, segments)
                    if sources:
                        lines.append(f"[Sources: {', '.join(sources)}]\n")

        # Заключение
        lines.append("## Conclusion\n")
        lines.append("This article summarized the key concepts from multiple research sources.\n")

        return '\n'.join(lines)

    def _find_concept_sources(self, concept_id: str, segments: List[Segment]) -> List[str]:
        """Найти источники, содержащие концепт"""
        sources = set()

        for segment in segments:
            for concept in segment.concepts:
                if concept.id == concept_id:
                    source_id = segment.metadata.get('source_id', 'unknown')
                    sources.add(source_id)

        return list(sources)


# ============================================================================
# DEMO
# ============================================================================

def demo_dissertation_to_wiki():
    """Демонстрация: диссертация → энциклопедия"""
    print("=" * 80)
    print("DEMO: Dissertation → Encyclopedia")
    print("=" * 80)

    # Пример текста диссертации
    dissertation_text = """
    Neural Networks and Deep Learning

    Neural networks are computational models inspired by biological neural networks.
    Deep Learning is a subset of machine learning based on artificial neural networks.

    Convolutional Neural Networks (CNNs) are specialized for processing grid-like data.
    CNNs have been particularly successful in Computer Vision tasks.

    Recurrent Neural Networks (RNNs) are designed for sequential data.
    Long Short-Term Memory (LSTM) networks are a type of RNN that can learn long-term dependencies.

    Transformers revolutionized Natural Language Processing.
    BERT and GPT are examples of transformer-based models.

    Transfer Learning allows models trained on one task to be adapted for another.
    Fine-tuning is a common technique in Transfer Learning.
    """

    # Декомпозиция
    print("\n1. Decomposing dissertation...")
    decomposer = DissertationDecomposer(use_ml=False)
    segments = decomposer.decompose(
        dissertation_text,
        metadata={'source_id': 'Dissertation_001', 'author': 'John Doe'}
    )

    print(f"   Extracted {len(segments)} segments")
    print(f"   Total concepts: {sum(len(s.concepts) for s in segments)}")

    # Агрегация
    print("\n2. Aggregating to encyclopedia article...")
    aggregator = WikiAggregator(target_length=500)
    article = aggregator.aggregate(segments, topic="Neural Networks")

    print("\n3. Generated article:\n")
    print(article)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("Knowledge Transformation System - Demo\n")
    demo_dissertation_to_wiki()
