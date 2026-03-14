"""
Dissertation Structure Visualizer
Визуализатор структуры диссертации

Создает графы, тепловые карты и диаграммы для анализа структуры

Author: AI Research Assistant
Date: 2026-02-04
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx
from typing import List, Dict
import seaborn as sns
from matplotlib import cm


class DissertationVisualizer:
    """Визуализация структуры диссертации"""

    def __init__(self, optimizer):
        """
        Parameters:
        -----------
        optimizer: экземпляр DissertationOptimizer
        """
        self.optimizer = optimizer
        self.chapters = optimizer.chapters

        # Настройка стиля
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")

    def plot_distance_matrix(self, save_path: str = None):
        """
        Визуализация матрицы когнитивных дистанций

        Тепловая карта показывает "близость" глав друг к другу
        """
        fig, ax = plt.subplots(figsize=(12, 10))

        # Получаем метки
        chapter_ids = list(self.optimizer.id_to_index.keys())
        labels = [self.chapters[ch_id].title for ch_id in chapter_ids]

        # Тепловая карта
        im = ax.imshow(self.optimizer.distance_matrix, cmap='RdYlGn_r', aspect='auto')

        # Настройка осей
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)

        # Добавление значений в ячейки
        for i in range(len(labels)):
            for j in range(len(labels)):
                text = ax.text(j, i, f'{self.optimizer.distance_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)

        # Заголовок и colorbar
        ax.set_title("Матрица когнитивных дистанций между главами\n"
                    "(чем зеленее, тем ближе главы по смыслу)",
                    fontsize=14, pad=20)
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Когнитивная дистанция', rotation=270, labelpad=20)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Матрица дистанций сохранена: {save_path}")

        plt.show()

    def plot_dependency_graph(self, save_path: str = None):
        """
        Визуализация графа зависимостей

        Показывает, какие главы должны предшествовать другим
        """
        G = nx.DiGraph()

        # Добавляем вершины и рёбра
        for ch_id, chapter in self.chapters.items():
            G.add_node(ch_id, title=chapter.title)

            for prereq_id in chapter.prerequisites:
                G.add_edge(prereq_id, ch_id)

        # Иерархический layout
        try:
            pos = nx.spring_layout(G, k=2, iterations=50)
        except:
            pos = nx.spring_layout(G)

        fig, ax = plt.subplots(figsize=(14, 10))

        # Рисуем граф
        nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue',
                              edgecolors='black', linewidths=2, ax=ax)

        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True,
                              arrowsize=20, arrowstyle='->', ax=ax,
                              connectionstyle='arc3,rad=0.1')

        # Метки
        labels = {ch_id: f"{ch_id}\n{ch.title}" for ch_id, ch in self.chapters.items()}
        nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold', ax=ax)

        ax.set_title("Граф зависимостей глав диссертации\n"
                    "(стрелка A → B означает: A должна быть раньше B)",
                    fontsize=14, pad=20)
        ax.axis('off')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Граф зависимостей сохранен: {save_path}")

        plt.show()

    def plot_path_comparison(self, paths: Dict[str, List[str]], save_path: str = None):
        """
        Сравнение нескольких путей (структур)

        Parameters:
        -----------
        paths: dict {'название': [путь]}
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        costs = []
        names = []

        for name, path in paths.items():
            cost = self.optimizer.path_cost(path)
            costs.append(cost)
            names.append(name)

        # Bar chart
        bars = ax.bar(names, costs, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])

        # Добавление значений на столбцы
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{cost:.2f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel('Когнитивная стоимость', fontsize=12)
        ax.set_title('Сравнение различных структур диссертации\n(чем ниже, тем лучше)',
                    fontsize=14, pad=20)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Сравнение путей сохранено: {save_path}")

        plt.show()

    def plot_path_flow(self, path: List[str], save_path: str = None):
        """
        Визуализация потока повествования

        Показывает последовательность глав и когнитивную нагрузку переходов
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])

        # График 1: Последовательность глав с дистанциями
        positions = np.arange(len(path))
        titles = [self.chapters[ch_id].title for ch_id in path]

        # Вычисляем дистанции между соседними главами
        distances = []
        for i in range(len(path) - 1):
            from_idx = self.optimizer.id_to_index[path[i]]
            to_idx = self.optimizer.id_to_index[path[i+1]]
            dist = self.optimizer.distance_matrix[from_idx][to_idx]
            distances.append(dist)

        # Нормализация для цветовой карты
        max_dist = max(distances) if distances else 1
        colors = [plt.cm.RdYlGn_r(d / max_dist) for d in distances]

        # Рисуем главы как узлы
        ax1.scatter(positions, [0] * len(positions), s=500, c='lightblue',
                   edgecolors='black', linewidths=2, zorder=3)

        # Рисуем переходы с цветовой кодировкой
        for i in range(len(path) - 1):
            ax1.arrow(positions[i], 0, positions[i+1] - positions[i] - 0.15, 0,
                     head_width=0.15, head_length=0.1, fc=colors[i], ec=colors[i],
                     linewidth=3, zorder=2)

            # Подпись дистанции
            mid_x = (positions[i] + positions[i+1]) / 2
            ax1.text(mid_x, 0.25, f'{distances[i]:.2f}',
                    ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Метки глав
        for pos, title in zip(positions, titles):
            ax1.text(pos, -0.3, title, ha='center', fontsize=9,
                    rotation=45, va='top')

        ax1.set_xlim(-0.5, len(path) - 0.5)
        ax1.set_ylim(-2, 1)
        ax1.axis('off')
        ax1.set_title('Последовательность глав и когнитивные переходы\n'
                     '(красный = сложный переход, зеленый = легкий)',
                     fontsize=14, pad=20)

        # График 2: Гистограмма дистанций
        ax2.bar(range(len(distances)), distances, color=colors, edgecolor='black')
        ax2.set_xlabel('Переход между главами', fontsize=11)
        ax2.set_ylabel('Когнитивная дистанция', fontsize=11)
        ax2.set_title('Когнитивная нагрузка на каждом переходе', fontsize=12)
        ax2.axhline(y=np.mean(distances), color='blue', linestyle='--',
                   label=f'Средняя: {np.mean(distances):.2f}')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Поток повествования сохранен: {save_path}")

        plt.show()

    def plot_metrics_radar(self, paths: Dict[str, List[str]], save_path: str = None):
        """
        Радарная диаграмма метрик для сравнения структур

        Parameters:
        -----------
        paths: dict {'название': [путь]}
        """
        metrics_data = {}

        for name, path in paths.items():
            metrics = self.optimizer.evaluate_structure(path)

            # Нормализуем метрики для визуализации (0-1)
            metrics_data[name] = {
                'Связность': metrics['coherence'],
                'Простота чтения': 1 - metrics['reader_complexity'],
                'Соблюдение зависимостей': 1 if metrics['dependency_violations'] == 0 else 0.5,
                'Низкая когнитивная стоимость': 1 / (1 + metrics['cognitive_cost'] / 10),
            }

        # Настройка радарной диаграммы
        categories = list(next(iter(metrics_data.values())).keys())
        N = len(categories)

        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # Рисуем каждый путь
        colors = ['blue', 'orange', 'green', 'red']
        for (name, metrics), color in zip(metrics_data.items(), colors):
            values = list(metrics.values())
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2, label=name, color=color)
            ax.fill(angles, values, alpha=0.15, color=color)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_title('Сравнение структур по метрикам качества\n(чем дальше от центра, тем лучше)',
                    fontsize=14, pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Радарная диаграмма сохранена: {save_path}")

        plt.show()

    def plot_writing_timeline(self, path: List[str], save_path: str = None):
        """
        Временная шкала написания диссертации

        Показывает оценку времени на каждую главу
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        titles = []
        durations = []
        cumulative_time = [0]

        for ch_id in path:
            chapter = self.chapters[ch_id]
            duration = self.optimizer._estimate_writing_time(chapter)

            titles.append(chapter.title)
            durations.append(duration)
            cumulative_time.append(cumulative_time[-1] + duration)

        # Gantt chart
        colors = cm.viridis(np.linspace(0, 1, len(titles)))

        for i, (title, duration, start) in enumerate(zip(titles, durations, cumulative_time[:-1])):
            ax.barh(i, duration, left=start, height=0.8, color=colors[i],
                   edgecolor='black', linewidth=1.5)

            # Подпись длительности
            mid_point = start + duration / 2
            ax.text(mid_point, i, f'{duration:.0f}ч', ha='center', va='center',
                   fontsize=9, fontweight='bold', color='white')

        ax.set_yticks(range(len(titles)))
        ax.set_yticklabels(titles, fontsize=10)
        ax.set_xlabel('Накопленное время (часы)', fontsize=12)
        ax.set_title(f'Оценка временной шкалы написания диссертации\n'
                    f'Общее время: {cumulative_time[-1]:.0f} часов ≈ {cumulative_time[-1]/40:.1f} недель (по 40ч/нед)',
                    fontsize=14, pad=20)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Временная шкала сохранена: {save_path}")

        plt.show()

    def plot_complexity_flow(self, path: List[str], save_path: str = None):
        """
        График изменения сложности и новизны по мере развития диссертации
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        positions = np.arange(len(path))
        titles = [self.chapters[ch_id].title for ch_id in path]
        complexities = [self.chapters[ch_id].complexity for ch_id in path]
        novelties = [self.chapters[ch_id].novelty for ch_id in path]

        # График 1: Сложность
        ax1.plot(positions, complexities, 'o-', linewidth=2, markersize=8,
                color='darkred', label='Сложность')
        ax1.fill_between(positions, complexities, alpha=0.3, color='red')
        ax1.set_ylabel('Сложность изложения', fontsize=12)
        ax1.set_ylim(0, 1.1)
        ax1.grid(alpha=0.3)
        ax1.legend(fontsize=11)
        ax1.set_title('Динамика сложности и новизны материала', fontsize=14, pad=20)

        # График 2: Новизна
        ax2.plot(positions, novelties, 's-', linewidth=2, markersize=8,
                color='darkblue', label='Новизна')
        ax2.fill_between(positions, novelties, alpha=0.3, color='blue')
        ax2.set_ylabel('Научная новизна', fontsize=12)
        ax2.set_ylim(0, 1.1)
        ax2.grid(alpha=0.3)
        ax2.legend(fontsize=11)

        # Метки глав
        ax2.set_xticks(positions)
        ax2.set_xticklabels(titles, rotation=45, ha='right')
        ax2.set_xlabel('Главы', fontsize=12)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"График сложности сохранен: {save_path}")

        plt.show()

    def generate_report(self, path: List[str], output_dir: str = './'):
        """
        Генерирует полный визуальный отчет по структуре

        Parameters:
        -----------
        path: оптимизированный путь
        output_dir: директория для сохранения
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        print("Генерация визуального отчета...")
        print("=" * 60)

        # 1. Матрица дистанций
        print("\n1. Создание матрицы дистанций...")
        self.plot_distance_matrix(f"{output_dir}/distance_matrix.png")

        # 2. Граф зависимостей
        print("\n2. Создание графа зависимостей...")
        self.plot_dependency_graph(f"{output_dir}/dependency_graph.png")

        # 3. Поток повествования
        print("\n3. Создание графика потока повествования...")
        self.plot_path_flow(path, f"{output_dir}/narrative_flow.png")

        # 4. Временная шкала
        print("\n4. Создание временной шкалы...")
        self.plot_writing_timeline(path, f"{output_dir}/writing_timeline.png")

        # 5. График сложности
        print("\n5. Создание графика сложности...")
        self.plot_complexity_flow(path, f"{output_dir}/complexity_flow.png")

        print("\n" + "=" * 60)
        print(f"✅ Отчет сгенерирован в директории: {output_dir}")
        print("=" * 60)


def demo_visualizer():
    """Демонстрация визуализатора"""
    from dissertation_optimizer import DissertationOptimizer, create_sample_dissertation

    print("Dissertation Visualizer - Demo\n")

    # Создаем пример
    chapters, start, end = create_sample_dissertation()
    optimizer = DissertationOptimizer(chapters, start, end)

    # Оптимизируем структуру
    print("Оптимизация структуры...")
    optimal_path, optimal_cost = optimizer.optimize(method='simulated_annealing')

    # Создаем визуализатор
    visualizer = DissertationVisualizer(optimizer)

    # Генерируем отчет
    visualizer.generate_report(optimal_path, output_dir='./visualization_output')


if __name__ == "__main__":
    demo_visualizer()
