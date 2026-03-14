"""
Автоматическая демонстрация системы трансформации знаний
(без интерактивного ввода)

Быстрый обзор всех возможностей системы
"""

from practical_examples import (
    example_multiple_dissertations_to_encyclopedia,
    example_encyclopedia_to_dissertation_proposals,
    example_knowledge_rationalization,
    example_full_pipeline
)


def main():
    """Автоматический запуск всех примеров"""
    print("\n" + "=" * 80)
    print("АВТОМАТИЧЕСКАЯ ДЕМОНСТРАЦИЯ СИСТЕМЫ ТРАНСФОРМАЦИИ ЗНАНИЙ")
    print("=" * 80 + "\n")

    try:
        # Пример 1
        print("\n⏳ Запуск примера 1 из 4...\n")
        example_multiple_dissertations_to_encyclopedia()

        # Пример 2
        print("\n⏳ Запуск примера 2 из 4...\n")
        example_encyclopedia_to_dissertation_proposals()

        # Пример 3
        print("\n⏳ Запуск примера 3 из 4...\n")
        example_knowledge_rationalization()

        # Пример 4
        print("\n⏳ Запуск примера 4 из 4...\n")
        example_full_pipeline()

        print("\n" + "=" * 80)
        print("✅ ВСЕ ДЕМОНСТРАЦИИ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("=" * 80)
        print("\nСистема готова к использованию.")
        print("\nДоступные компоненты:")
        print("  • DissertationDecomposer - декомпозиция диссертаций")
        print("  • WikiAggregator - агрегация в энциклопедии")
        print("  • WikiDecomposer - декомпозиция энциклопедий")
        print("  • DissertationSynthesizer - синтез новых идей")
        print("  • KnowledgeRationalizer - рационализация знаний")
        print("\nСм. файлы:")
        print("  • knowledge_transformer.py - основной модуль")
        print("  • practical_examples.py - детальные примеры")
        print("  • knowledge_transformation_theory.md - теория")
        print("  • README_MASTER.md - документация")
        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
