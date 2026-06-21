# astar.py
import heapq

from src.settings.base import GroundMaterial


def _heuristic(a, b):
    # Используем Манхэттенское расстояние для сетки без диагоналей
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct_path(came_from, start, end):
    """Вспомогательная функция для сборки пути от старта до конечной точки."""
    path = []
    current = end
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(start)
    return path[::-1]  # Разворачиваем путь, чтобы он шел от старта


def find_path(tiles, start, goal):
    if not start or not goal:
        return None

    if start == goal:
        return [start]

    # Очередь приоритетов хранит кортежи: (f_score, узел)
    open_set = []
    heapq.heappush(open_set, (0, start))

    # Словарь для отслеживания родителей у каждого узла
    came_from = {}

    # Реальная стоимость пути от старта до текущего узла
    g_score = {start: 0}

    # Множество для быстрого поиска элементов в очереди
    open_set_hash = {start}

    # Переменные для запоминания самой близкой точки к цели на случай блокировки
    closest_node = start
    min_h = _heuristic(start, goal)

    while open_set:
        _, current = heapq.heappop(open_set)
        if current in open_set_hash:
            open_set_hash.remove(current)

        # Если цель достигнута, сразу возвращаем путь
        if current == goal:
            return _reconstruct_path(came_from, start, goal)

        # Оцениваем, насколько текущая точка близка к цели
        current_h = _heuristic(current, goal)
        if current_h < min_h:
            min_h = current_h
            closest_node = current

        # Проверяем 4 соседних направления
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            # Пропускаем стены
            if tiles.get(neighbor) != GroundMaterial.AIR:
                continue

            # Стоимость шага равна 1
            tentative_g_score = g_score[current] + 1

            # Если нашли более выгодный путь к соседу
            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + _heuristic(neighbor, goal)

                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score, neighbor))
                    open_set_hash.add(neighbor)

    # Если мы вышли из цикла, значит, прямого пути к цели нет.
    # Возвращаем путь до наиболее близкой к цели точки, которую удалось посетить.
    return _reconstruct_path(came_from, start, closest_node)