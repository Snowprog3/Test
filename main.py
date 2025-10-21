import argparse
import csv
import sys
from collections import defaultdict
from tabulate import tabulate

def parse_args():
    p = argparse.ArgumentParser(description='rating')
    p.add_argument("--files", nargs="+", required=True, help="Входные CSV файлы")
    p.add_argument("--report", required=True, help="Название отчёта - average-rating")
    return p.parse_args()

def read_ratings_from_file(path, brand_sums, brand_counts):
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Проверка заголовков
            if 'brand' not in reader.fieldnames or 'rating' not in reader.fieldnames:
                print(f"Warning: файл '{path}' не содержит поля 'brand' или 'rating' — пропускаю", file=sys.stderr)
                return

            for i, row in enumerate(reader, start=2):  # start=2 — учитываем заголовок как строку 1
                brand = row.get('brand')
                rating = row.get('rating')
                if brand is None or brand.strip() == "":
                    # Пропустить строки без бренда
                    print(f"Warning: пропущена строка {i} в '{path}' — пустое поле 'brand'", file=sys.stderr)
                    continue
                if rating is None or rating.strip() == "":
                    print(f"Warning: пропущена строка {i} в '{path}' — пустое поле 'rating'", file=sys.stderr)
                    continue
                try:
                    r = float(rating)
                except ValueError:
                    print(f"Warning: в файле '{path}', строка {i} — некорректный рейтинг '{rating}' (пропуск)", file=sys.stderr)
                    continue

                key = brand.strip()
                brand_sums[key] += r
                brand_counts[key] += 1
    except FileNotFoundError:
        print(f"Error: файл '{path}' не найден", file=sys.stderr)
    except PermissionError:
        print(f"Error: нет доступа к файлу '{path}'", file=sys.stderr)
    except Exception as e:
        print(f"Error: при чтении файла '{path}' произошла ошибка: {e}", file=sys.stderr)

def make_report(files):
    brand_sums = defaultdict(float)
    brand_counts = defaultdict(int)

    for path in files:
        read_ratings_from_file(path, brand_sums, brand_counts)

    # Собираем результаты
    rows = []
    for brand, total in brand_sums.items():
        count = brand_counts[brand]
        if count > 0:
            avg = total / count
            rows.append((brand, avg))

    if not rows:
        print("No data to report (нет валидных записей с рейтингами).", file=sys.stderr)
        return 1

    # Сортируем по среднему рейтингу по убыванию, при равенстве — по имени бренда
    rows.sort(key=lambda x: (-x[1], x[0].lower()))

    # Формируем таблицу и печатаем
    table = [(brand, f"{avg:.2f}") for brand, avg in rows]
    print(tabulate(table, headers=["Brand", "Average rating"], tablefmt="github"))

    return 0

def main():
    args = parse_args()
    if args.report != "average-rating":
        print("Error: поддерживается только отчёт 'average-rating'", file=sys.stderr)
        sys.exit(2)
    ret = make_report(args.files)
    sys.exit(ret if isinstance(ret, int) else 0)

if __name__ == "__main__":
    main()