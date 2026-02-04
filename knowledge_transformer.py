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

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json
import re

# Optional numpy import
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Fallback implementations
    class np:
        @staticmethod
        def mean(lst):
            return sum(lst) / len(lst) if lst else 0

        @staticmethod
        def argmax(lst):
            return max(range(len(lst)), key=lambda i: lst[i]) if lst else 0


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
# WIKI DECOMPOSER
# ============================================================================

class WikiDecomposer:
    """Декомпозиция энциклопедических статей в факты"""

    def __init__(self, use_ml: bool = False):
        """
        Parameters:
        -----------
        use_ml: использовать NLP для извлечения триплетов
        """
        self.use_ml = use_ml

    def decompose(self, wiki_text: str, metadata: Dict = None) -> List[Fact]:
        """
        Декомпозировать статью Википедии в факты (SPO триплеты)

        Parameters:
        -----------
        wiki_text: текст статьи
        metadata: метаданные (источник, дата)

        Returns:
        --------
        facts: список фактов (Subject-Predicate-Object триплетов)
        """
        # Шаг 1: Разбиение на предложения
        sentences = self._split_into_sentences(wiki_text)

        # Шаг 2: Извлечение триплетов
        facts = []
        for sentence in sentences:
            triplets = self._extract_triplets(sentence)

            for subj, pred, obj in triplets:
                fact = Fact(
                    subject=subj,
                    predicate=pred,
                    object=obj,
                    certainty=0.9,
                    sources=[metadata.get('source', 'wikipedia') if metadata else 'wikipedia'],
                    context=sentence
                )
                facts.append(fact)

        # Шаг 3: Дедупликация
        facts = self._deduplicate_facts(facts)

        return facts

    def _split_into_sentences(self, text: str) -> List[str]:
        """Разбить текст на предложения"""
        # Простое разбиение по точкам
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences

    def _extract_triplets(self, sentence: str) -> List[Tuple[str, str, str]]:
        """
        Извлечь SPO триплеты из предложения

        Использует простые паттерны и эвристики
        """
        triplets = []

        # Паттерн 1: X is Y
        pattern1 = r'([A-Z][a-zA-Z\s]+?)\s+(?:is|are)\s+([a-z].*?)(?:\.|,|$)'
        matches = re.findall(pattern1, sentence)
        for subj, obj in matches:
            triplets.append((subj.strip(), "is_a", obj.strip()))

        # Паттерн 2: X has Y
        pattern2 = r'([A-Z][a-zA-Z\s]+?)\s+(?:has|have)\s+([a-z].*?)(?:\.|,|$)'
        matches = re.findall(pattern2, sentence)
        for subj, obj in matches:
            triplets.append((subj.strip(), "has", obj.strip()))

        # Паттерн 3: X causes Y
        pattern3 = r'([A-Z][a-zA-Z\s]+?)\s+(?:causes?|leads? to)\s+([a-z].*?)(?:\.|,|$)'
        matches = re.findall(pattern3, sentence)
        for subj, obj in matches:
            triplets.append((subj.strip(), "causes", obj.strip()))

        # Паттерн 4: X used for Y
        pattern4 = r'([A-Z][a-zA-Z\s]+?)\s+(?:used for|applied to)\s+([a-z].*?)(?:\.|,|$)'
        matches = re.findall(pattern4, sentence)
        for subj, obj in matches:
            triplets.append((subj.strip(), "used_for", obj.strip()))

        # Если ничего не найдено, извлекаем субъект и первое существительное
        if not triplets:
            words = sentence.split()
            if len(words) >= 3:
                # Простая эвристика: первое слово с заглавной - субъект
                subj = words[0]
                if subj[0].isupper() and len(subj) > 2:
                    # Ищем следующее существительное
                    for i, word in enumerate(words[1:], 1):
                        if len(word) > 3 and word[0].islower():
                            obj = ' '.join(words[i:min(i+5, len(words))])
                            triplets.append((subj, "related_to", obj))
                            break

        return triplets

    def _deduplicate_facts(self, facts: List[Fact]) -> List[Fact]:
        """Удалить дубликаты фактов"""
        seen = set()
        unique_facts = []

        for fact in facts:
            key = (fact.subject.lower(), fact.predicate, fact.object.lower())
            if key not in seen:
                seen.add(key)
                unique_facts.append(fact)

        return unique_facts


# ============================================================================
# DISSERTATION SYNTHESIZER
# ============================================================================

class DissertationSynthesizer:
    """Синтез новых идей диссертаций из фактов энциклопедии"""

    def __init__(self, min_novelty: float = 0.6):
        """
        Parameters:
        -----------
        min_novelty: минимальный порог новизны для идеи
        """
        self.min_novelty = min_novelty

    def synthesize(self, facts: List[Fact], domain: str = "general") -> List[Dict]:
        """
        Синтезировать идеи диссертаций из фактов

        Parameters:
        -----------
        facts: факты из энциклопедий
        domain: целевая область исследования

        Returns:
        --------
        proposals: список предложений диссертаций с оценками
        """
        # Шаг 1: Построить граф знаний из фактов
        knowledge_graph = self._build_graph_from_facts(facts)

        # Шаг 2: Найти исследовательские пробелы
        gaps = self._identify_research_gaps(knowledge_graph)

        # Шаг 3: Сгенерировать идеи
        proposals = []
        for gap in gaps:
            proposal = self._generate_proposal(gap, knowledge_graph, facts)
            if proposal['novelty'] >= self.min_novelty:
                proposals.append(proposal)

        # Шаг 4: Ранжировать по качеству
        proposals = self._rank_proposals(proposals)

        return proposals

    def _build_graph_from_facts(self, facts: List[Fact]) -> KnowledgeGraph:
        """Построить граф знаний из фактов"""
        graph = KnowledgeGraph()

        # Создать концепты из субъектов и объектов
        concept_map = {}

        for fact in facts:
            # Субъект
            if fact.subject not in concept_map:
                concept = Concept(
                    id=f"c_{hash(fact.subject) % 100000}",
                    name=fact.subject,
                    definition=f"Concept: {fact.subject}",
                    domain="extracted",
                    sources=fact.sources
                )
                concept_map[fact.subject] = concept
                graph.add_concept(concept)

            # Объект
            if fact.object not in concept_map:
                concept = Concept(
                    id=f"c_{hash(fact.object) % 100000}",
                    name=fact.object,
                    definition=f"Concept: {fact.object}",
                    domain="extracted",
                    sources=fact.sources
                )
                concept_map[fact.object] = concept
                graph.add_concept(concept)

            # Связь
            relation = Relation(
                source=concept_map[fact.subject].id,
                target=concept_map[fact.object].id,
                relation_type=fact.predicate,
                strength=fact.certainty
            )
            graph.add_relation(relation)

        return graph

    def _identify_research_gaps(self, graph: KnowledgeGraph) -> List[Dict]:
        """
        Идентифицировать исследовательские пробелы

        Типы пробелов:
        1. Слабые связи (низкая центральность)
        2. Отсутствующие связи (концепты рядом, но не связаны)
        3. Неисследованные комбинации
        """
        gaps = []

        # Тип 1: Концепты с низкой центральностью
        centrality = graph.compute_centrality()
        low_centrality_concepts = [
            cid for cid, score in centrality.items()
            if score < np.mean(list(centrality.values())) * 0.5
        ]

        for cid in low_centrality_concepts[:10]:  # Топ 10
            concept = graph.concepts[cid]
            gaps.append({
                'type': 'under_researched',
                'concept': concept,
                'centrality': centrality[cid],
                'neighbors': list(graph.get_neighbors(cid))
            })

        # Тип 2: Отсутствующие связи между близкими концептами
        # Находим пары концептов, которые имеют общих соседей, но не связаны напрямую
        concept_ids = list(graph.concepts.keys())
        for i, cid1 in enumerate(concept_ids[:50]):  # Ограничиваем для производительности
            for cid2 in concept_ids[i+1:i+20]:
                if cid2 not in graph.get_neighbors(cid1):
                    # Проверяем общих соседей
                    common = graph.get_neighbors(cid1) & graph.get_neighbors(cid2)
                    if len(common) >= 2:  # Есть общие соседи
                        gaps.append({
                            'type': 'missing_link',
                            'concept1': graph.concepts[cid1],
                            'concept2': graph.concepts[cid2],
                            'common_neighbors': len(common),
                            'bridge_concepts': [graph.concepts[c] for c in list(common)[:3]]
                        })

        return gaps

    def _generate_proposal(self, gap: Dict, graph: KnowledgeGraph,
                          facts: List[Fact]) -> Dict:
        """Сгенерировать предложение диссертации из пробела"""
        proposal = {
            'gap_type': gap['type'],
            'novelty': 0.0,
            'impact': 0.0,
            'feasibility': 0.0,
            'title': '',
            'description': '',
            'research_questions': [],
            'methodology': '',
            'expected_contributions': []
        }

        if gap['type'] == 'under_researched':
            concept = gap['concept']
            proposal['title'] = f"Advanced Study of {concept.name}"
            proposal['description'] = (
                f"This research aims to deeply investigate {concept.name}, "
                f"which is currently under-researched in the literature. "
                f"Current centrality: {gap['centrality']:.3f}"
            )
            proposal['novelty'] = 0.7 + 0.3 * (1 - gap['centrality'])
            proposal['impact'] = 0.5
            proposal['feasibility'] = 0.8
            proposal['research_questions'] = [
                f"What are the fundamental properties of {concept.name}?",
                f"How does {concept.name} interact with related concepts?",
                f"What applications can be derived from {concept.name}?"
            ]

        elif gap['type'] == 'missing_link':
            c1 = gap['concept1']
            c2 = gap['concept2']
            proposal['title'] = f"Bridging {c1.name} and {c2.name}"
            proposal['description'] = (
                f"This research explores the relationship between {c1.name} and {c2.name}, "
                f"which share {gap['common_neighbors']} common connections but lack direct research linking them."
            )
            proposal['novelty'] = 0.8
            proposal['impact'] = 0.6 + 0.2 * min(gap['common_neighbors'] / 5, 1.0)
            proposal['feasibility'] = 0.7
            proposal['research_questions'] = [
                f"What is the nature of the relationship between {c1.name} and {c2.name}?",
                f"Can insights from {c1.name} be applied to {c2.name}?",
                f"What new applications emerge from combining {c1.name} and {c2.name}?"
            ]
            proposal['methodology'] = "Comparative analysis, experimental validation, theoretical framework development"

        # Вычислить общую оценку
        proposal['overall_score'] = (
            0.4 * proposal['novelty'] +
            0.4 * proposal['impact'] +
            0.2 * proposal['feasibility']
        )

        return proposal

    def _rank_proposals(self, proposals: List[Dict]) -> List[Dict]:
        """Ранжировать предложения по качеству"""
        proposals.sort(key=lambda p: p['overall_score'], reverse=True)
        return proposals


# ============================================================================
# KNOWLEDGE RATIONALIZER
# ============================================================================

class KnowledgeRationalizer:
    """
    Система рационализации научного знания

    Оптимизация представления знаний через:
    1. Компрессию избыточности
    2. Максимизацию покрытия
    3. Минимизацию сложности
    """

    def __init__(self, compression_target: float = 0.5):
        """
        Parameters:
        -----------
        compression_target: целевой коэффициент компрессии (0-1)
        """
        self.compression_target = compression_target

    def rationalize(self, knowledge_graph: KnowledgeGraph,
                   optimization_goal: str = "balanced") -> Dict:
        """
        Рационализировать граф знаний

        Parameters:
        -----------
        knowledge_graph: исходный граф знаний
        optimization_goal: цель оптимизации
            - "compression": максимальная компрессия
            - "coverage": максимальное покрытие
            - "balanced": баланс

        Returns:
        --------
        result: оптимизированный граф и метрики
        """
        # Шаг 1: Анализ текущего состояния
        initial_metrics = self._compute_metrics(knowledge_graph)

        # Шаг 2: Идентификация избыточности
        redundancies = self._identify_redundancies(knowledge_graph)

        # Шаг 3: Оптимизация структуры
        optimized_graph = self._optimize_structure(
            knowledge_graph,
            redundancies,
            optimization_goal
        )

        # Шаг 4: Вычисление финальных метрик
        final_metrics = self._compute_metrics(optimized_graph)

        # Шаг 5: Формирование результата
        result = {
            'optimized_graph': optimized_graph,
            'initial_metrics': initial_metrics,
            'final_metrics': final_metrics,
            'redundancies_removed': len(redundancies),
            'compression_ratio': final_metrics['size'] / initial_metrics['size'],
            'coverage_preserved': final_metrics['coverage'] / initial_metrics['coverage'],
            'transformations': []
        }

        return result

    def _compute_metrics(self, graph: KnowledgeGraph) -> Dict:
        """Вычислить метрики графа знаний"""
        n_concepts = len(graph.concepts)
        n_relations = len(graph.relations)

        # Размер (сложность)
        size = n_concepts + n_relations

        # Покрытие (связность)
        if n_concepts > 0:
            avg_degree = 2 * n_relations / n_concepts
        else:
            avg_degree = 0

        # Центральность
        centrality = graph.compute_centrality()
        avg_centrality = np.mean(list(centrality.values())) if centrality else 0

        # Избыточность (транзитивные связи)
        redundancy = self._compute_redundancy(graph)

        return {
            'size': size,
            'concepts': n_concepts,
            'relations': n_relations,
            'avg_degree': avg_degree,
            'avg_centrality': avg_centrality,
            'redundancy': redundancy,
            'coverage': avg_degree * avg_centrality  # Комбинированная метрика
        }

    def _compute_redundancy(self, graph: KnowledgeGraph) -> float:
        """Вычислить уровень избыточности"""
        # Подсчет транзитивных связей
        redundant_count = 0
        total_relations = len(graph.relations)

        if total_relations == 0:
            return 0.0

        # Для каждой связи A->C проверяем, есть ли путь A->B->C
        for relation in graph.relations[:min(100, total_relations)]:  # Ограничиваем для производительности
            source = relation.source
            target = relation.target

            # Ищем промежуточные узлы
            for intermediate in graph.get_neighbors(source):
                if intermediate != target and target in graph.get_neighbors(intermediate):
                    redundant_count += 1
                    break

        return redundant_count / min(100, total_relations)

    def _identify_redundancies(self, graph: KnowledgeGraph) -> List[Dict]:
        """Идентифицировать избыточные элементы"""
        redundancies = []

        # Тип 1: Транзитивные связи
        for relation in graph.relations:
            source = relation.source
            target = relation.target

            # Проверяем существование обходного пути
            for intermediate in graph.get_neighbors(source):
                if intermediate != target and target in graph.get_neighbors(intermediate):
                    redundancies.append({
                        'type': 'transitive_relation',
                        'relation': relation,
                        'path': [source, intermediate, target]
                    })
                    break

        # Тип 2: Дублирующиеся концепты (похожие названия)
        concept_list = list(graph.concepts.values())
        for i, c1 in enumerate(concept_list):
            for c2 in concept_list[i+1:]:
                similarity = self._string_similarity(c1.name, c2.name)
                if similarity > 0.85:  # Очень похожие
                    redundancies.append({
                        'type': 'duplicate_concept',
                        'concept1': c1,
                        'concept2': c2,
                        'similarity': similarity
                    })

        return redundancies

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Вычислить схожесть строк (простое Jaccard расстояние)"""
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        # Jaccard similarity по символьным биграммам
        bigrams1 = set([s1_lower[i:i+2] for i in range(len(s1_lower)-1)])
        bigrams2 = set([s2_lower[i:i+2] for i in range(len(s2_lower)-1)])

        if not bigrams1 and not bigrams2:
            return 1.0 if s1_lower == s2_lower else 0.0

        intersection = len(bigrams1 & bigrams2)
        union = len(bigrams1 | bigrams2)

        return intersection / union if union > 0 else 0.0

    def _optimize_structure(self, graph: KnowledgeGraph,
                           redundancies: List[Dict],
                           goal: str) -> KnowledgeGraph:
        """Оптимизировать структуру графа"""
        # Создаем копию графа
        optimized = KnowledgeGraph()

        # Копируем все концепты
        for concept in graph.concepts.values():
            optimized.add_concept(concept)

        # Создаем set из идентификаторов избыточных связей (source, target, type)
        redundant_relation_ids = {
            (r['relation'].source, r['relation'].target, r['relation'].relation_type)
            for r in redundancies
            if r['type'] == 'transitive_relation'
        }

        # Добавляем только неизбыточные связи
        for relation in graph.relations:
            relation_id = (relation.source, relation.target, relation.relation_type)

            if goal == "compression":
                # Агрессивное удаление избыточности
                if relation_id not in redundant_relation_ids:
                    optimized.add_relation(relation)
            elif goal == "coverage":
                # Сохраняем все связи
                optimized.add_relation(relation)
            else:  # balanced
                # Удаляем только явную избыточность
                if relation_id not in redundant_relation_ids or relation.strength > 0.8:
                    optimized.add_relation(relation)

        # Объединяем дублирующиеся концепты
        duplicate_pairs = [
            (r['concept1'], r['concept2'])
            for r in redundancies
            if r['type'] == 'duplicate_concept'
        ]

        for c1, c2 in duplicate_pairs:
            if c1.id in optimized.concepts and c2.id in optimized.concepts:
                # Объединяем источники
                c1.sources.extend(c2.sources)
                # Удаляем дубликат
                del optimized.concepts[c2.id]

        return optimized


# ============================================================================
# DEMO
# ============================================================================

def demo_dissertation_to_wiki():
    """Демонстрация: диссертация → энциклопедия"""
    print("=" * 80)
    print("DEMO 1: Dissertation → Encyclopedia")
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

    print("\n3. Generated article preview:\n")
    print(article[:500] + "...\n")

    print("=" * 80)


def demo_wiki_to_dissertation():
    """Демонстрация: энциклопедия → диссертация"""
    print("\n" + "=" * 80)
    print("DEMO 2: Encyclopedia → Dissertation Proposals")
    print("=" * 80)

    # Пример статьи Википедии
    wiki_text = """
    Machine Learning is a field of artificial intelligence.
    Machine Learning has applications in computer vision.
    Deep Learning is a subset of machine learning.
    Neural Networks are used for pattern recognition.
    Supervised Learning requires labeled training data.
    Unsupervised Learning works with unlabeled data.
    Reinforcement Learning learns through trial and error.
    """

    # Декомпозиция
    print("\n1. Decomposing Wikipedia article...")
    wiki_decomposer = WikiDecomposer(use_ml=False)
    facts = wiki_decomposer.decompose(
        wiki_text,
        metadata={'source': 'Wikipedia: Machine Learning'}
    )

    print(f"   Extracted {len(facts)} facts")
    for i, fact in enumerate(facts[:5], 1):
        print(f"   {i}. ({fact.subject}) --{fact.predicate}--> ({fact.object})")

    # Синтез идей
    print("\n2. Synthesizing dissertation proposals...")
    synthesizer = DissertationSynthesizer(min_novelty=0.5)
    proposals = synthesizer.synthesize(facts, domain="Machine Learning")

    print(f"\n3. Generated {len(proposals)} proposals:\n")
    for i, prop in enumerate(proposals[:3], 1):
        print(f"   Proposal {i}: {prop['title']}")
        print(f"   Novelty: {prop['novelty']:.2f}, Impact: {prop['impact']:.2f}")
        print(f"   {prop['description'][:100]}...")
        print()

    print("=" * 80)


def demo_rationalization():
    """Демонстрация: рационализация знаний"""
    print("\n" + "=" * 80)
    print("DEMO 3: Knowledge Rationalization")
    print("=" * 80)

    # Создаем простой граф знаний
    graph = KnowledgeGraph()

    # Добавляем концепты
    concepts_data = [
        ("AI", "Artificial Intelligence"),
        ("ML", "Machine Learning"),
        ("DL", "Deep Learning"),
        ("NN", "Neural Networks"),
        ("CV", "Computer Vision")
    ]

    concept_map = {}
    for cid, name in concepts_data:
        concept = Concept(
            id=cid,
            name=name,
            definition=f"Definition of {name}",
            domain="AI"
        )
        graph.add_concept(concept)
        concept_map[cid] = concept

    # Добавляем связи (включая избыточные)
    relations_data = [
        ("AI", "ML", "includes"),
        ("ML", "DL", "includes"),
        ("AI", "DL", "includes"),  # Транзитивная (избыточная)
        ("DL", "NN", "uses"),
        ("NN", "CV", "applied_to"),
        ("DL", "CV", "applied_to"),  # Транзитивная
    ]

    for src, tgt, rel_type in relations_data:
        relation = Relation(
            source=src,
            target=tgt,
            relation_type=rel_type,
            strength=0.9
        )
        graph.add_relation(relation)

    print("\n1. Initial knowledge graph:")
    print(f"   Concepts: {len(graph.concepts)}")
    print(f"   Relations: {len(graph.relations)}")

    # Рационализация
    print("\n2. Rationalizing...")
    rationalizer = KnowledgeRationalizer(compression_target=0.5)
    result = rationalizer.rationalize(graph, optimization_goal="compression")

    print(f"\n3. Results:")
    print(f"   Redundancies removed: {result['redundancies_removed']}")
    print(f"   Compression ratio: {result['compression_ratio']:.2f}")
    print(f"   Coverage preserved: {result['coverage_preserved']:.2f}")
    print(f"   Final concepts: {result['final_metrics']['concepts']}")
    print(f"   Final relations: {result['final_metrics']['relations']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("Knowledge Transformation System - Complete Demo\n")

    demo_dissertation_to_wiki()
    demo_wiki_to_dissertation()
    demo_rationalization()

    print("\n✓ All demos completed successfully!")
