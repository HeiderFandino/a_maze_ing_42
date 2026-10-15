import random

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .maze import MazeGenerator


Position = tuple[int, int]


def _validate_limits(
    max_dead_ends: int,
    min_loops: int,
) -> None:
    """Validate braiding thresholds."""
    if type(max_dead_ends) is not int:
        raise TypeError(
            "max_dead_ends must be an integer"
        )

    if type(min_loops) is not int:
        raise TypeError(
            "min_loops must be an integer"
        )

    if max_dead_ends < 0:
        raise ValueError(
            "max_dead_ends cannot be negative"
        )

    if min_loops < 2:
        raise ValueError(
            "min_loops must be at least 2"
        )


def _wall_between(
    first: Position,
    second: Position,
) -> tuple[str, str]:
    """Return reciprocal wall names between adjacent cells."""
    x1, y1 = first
    x2, y2 = second

    dx = x2 - x1
    dy = y2 - y1

    if dx == 1 and dy == 0:
        return "east", "west"

    if dx == -1 and dy == 0:
        return "west", "east"

    if dx == 0 and dy == 1:
        return "south", "north"

    if dx == 0 and dy == -1:
        return "north", "south"

    raise ValueError(
        "cells must be orthogonally adjacent"
    )


def _is_passage_open(
    maze: "MazeGenerator",
    first: Position,
    second: Position,
) -> bool:
    """Return whether the passage is open from both cells."""
    first_wall, second_wall = _wall_between(
        first,
        second,
    )

    x1, y1 = first
    x2, y2 = second

    return (
        maze.grid[y1][x1][first_wall] is False
        and maze.grid[y2][x2][second_wall] is False
    )


def _close_passage(
    maze: "MazeGenerator",
    first: Position,
    second: Position,
) -> None:
    """Close a passage coherently on both cells."""
    first_wall, second_wall = _wall_between(
        first,
        second,
    )

    x1, y1 = first
    x2, y2 = second

    maze.grid[y1][x1][first_wall] = True
    maze.grid[y2][x2][second_wall] = True


def _is_fully_closed(
    maze: "MazeGenerator",
    position: Position,
) -> bool:
    """Return whether all four walls of a cell are closed."""
    x, y = position

    cell = maze.grid[y][x]

    return (
        cell["north"]
        and cell["east"]
        and cell["south"]
        and cell["west"]
    )


def is_dead_end(
    maze: "MazeGenerator",
    position: Position,
    blocked: set[Position],
) -> bool:
    """Return whether a traversable cell has one open passage."""
    if position in blocked:
        return False

    x, y = position

    if not maze.is_in_bounds(x, y):
        raise ValueError(
            f"position {position} must be inside the maze"
        )

    return (
        len(
            maze._get_open_neighbors(
                x,
                y,
            )
        )
        == 1
    )


def is_real_dead_end(
    maze: "MazeGenerator",
    position: Position,
    blocked: set[Position],
) -> bool:
    """Match the analyzer definition of a real dead-end."""
    if not is_dead_end(
        maze,
        position,
        blocked,
    ):
        return False

    x, y = position

    for neighbor in maze._get_neighbors(
        x,
        y,
    ):
        if _is_passage_open(
            maze,
            position,
            neighbor,
        ):
            continue

        if neighbor in blocked:
            continue

        if _is_fully_closed(
            maze,
            neighbor,
        ):
            continue

        return True

    return False


def find_dead_ends(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> list[Position]:
    """Return all traversable single-opening cells."""
    maze._validate_blocked(blocked)

    result: list[Position] = []

    for y in range(maze.height):
        for x in range(maze.width):
            position = (x, y)

            if is_dead_end(
                maze,
                position,
                blocked,
            ):
                result.append(position)

    return result


def find_real_dead_ends(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> list[Position]:
    """Return only dead-ends counted as real by the analyzer."""
    maze._validate_blocked(blocked)

    result: list[Position] = []

    for y in range(maze.height):
        for x in range(maze.width):
            position = (x, y)

            if is_real_dead_end(
                maze,
                position,
                blocked,
            ):
                result.append(position)

    return result


def _closed_candidates(
    maze: "MazeGenerator",
    position: Position,
    blocked: set[Position],
) -> list[Position]:
    """Return valid neighbours separated by a closed wall."""
    x, y = position

    candidates: list[Position] = []

    for neighbor in maze._get_neighbors(
        x,
        y,
    ):
        if neighbor in blocked:
            continue

        if _is_fully_closed(
            maze,
            neighbor,
        ):
            continue

        if _is_passage_open(
            maze,
            position,
            neighbor,
        ):
            continue

        candidates.append(neighbor)

    return candidates


def _has_open_3x3(
    maze: "MazeGenerator",
) -> bool:
    """Return whether a completely open 3x3 area exists."""
    if maze.width < 3 or maze.height < 3:
        return False

    for start_y in range(
        maze.height - 2
    ):
        for start_x in range(
            maze.width - 2
        ):
            open_area = True

            for y in range(
                start_y,
                start_y + 3,
            ):
                for x in range(
                    start_x,
                    start_x + 2,
                ):
                    if maze.grid[y][x]["east"]:
                        open_area = False
                        break

                if not open_area:
                    break

            if not open_area:
                continue

            for y in range(
                start_y,
                start_y + 2,
            ):
                for x in range(
                    start_x,
                    start_x + 3,
                ):
                    if maze.grid[y][x]["south"]:
                        open_area = False
                        break

                if not open_area:
                    break

            if open_area:
                return True

    return False


def _opening_is_safe(
    maze: "MazeGenerator",
    first: Position,
    second: Position,
) -> bool:
    """Check an opening without keeping it."""
    maze.open_passage(
        first[0],
        first[1],
        second[0],
        second[1],
    )

    invalid = _has_open_3x3(
        maze
    )

    _close_passage(
        maze,
        first,
        second,
    )

    return not invalid


def _count_edges(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> int:
    """Count open passages once."""
    edges = 0

    for y in range(maze.height):
        for x in range(maze.width):
            position = (x, y)

            if position in blocked:
                continue

            for neighbor in maze._get_open_neighbors(
                x,
                y,
            ):
                if neighbor in blocked:
                    continue

                if neighbor > position:
                    edges += 1

    return edges


def _traversable_count(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> int:
    """Return number of non-blocked maze cells."""
    return (
        maze.width
        * maze.height
        - len(blocked)
    )


def count_independent_loops(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> int:
    """Count independent loops using E - V + 1."""
    maze._validate_blocked(blocked)

    nodes = _traversable_count(
        maze,
        blocked,
    )

    if nodes <= 0:
        return 0

    edges = _count_edges(
        maze,
        blocked,
    )

    return edges - nodes + 1


def _reachable_cells(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> set[Position]:
    """Return all cells reachable from entry."""
    if maze.entry_pos in blocked:
        return set()

    visited: set[Position] = {
        maze.entry_pos
    }

    stack: list[Position] = [
        maze.entry_pos
    ]

    while stack:
        current = stack.pop()

        for neighbor in maze._get_open_neighbors(
            current[0],
            current[1],
        ):
            if neighbor in blocked:
                continue

            if neighbor in visited:
                continue

            visited.add(neighbor)
            stack.append(neighbor)

    return visited


def _is_fully_connected(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> bool:
    """Return whether every traversable cell is reachable."""
    reachable = _reachable_cells(
        maze,
        blocked,
    )

    return len(reachable) == _traversable_count(
        maze,
        blocked,
    )


def _key_cells_reachable(
    maze: "MazeGenerator",
    blocked: set[Position],
) -> bool:
    """Match analyzer rules for corners and centre."""
    reachable = _reachable_cells(
        maze,
        blocked,
    )

    corners: set[Position] = {
        (0, 0),
        (maze.width - 1, 0),
        (0, maze.height - 1),
        (
            maze.width - 1,
            maze.height - 1,
        ),
    }

    for corner in corners:
        if corner not in reachable:
            return False

    if maze.width % 2:
        center_x = {
            maze.width // 2
        }
    else:
        center_x = {
            maze.width // 2 - 1,
            maze.width // 2,
        }

    if maze.height % 2:
        center_y = {
            maze.height // 2
        }
    else:
        center_y = {
            maze.height // 2 - 1,
            maze.height // 2,
        }

    center_candidates = {
        (x, y)
        for x in center_x
        for y in center_y
    }

    return any(
        position in reachable
        for position in center_candidates
    )


def _walls_are_coherent(
    maze: "MazeGenerator",
) -> bool:
    """Check reciprocal walls across the whole grid."""
    directions = [
        ("east", "west", 1, 0),
        ("south", "north", 0, 1),
    ]

    for y in range(maze.height):
        for x in range(maze.width):
            for wall, opposite, dx, dy in directions:
                nx = x + dx
                ny = y + dy

                if not maze.is_in_bounds(
                    nx,
                    ny,
                ):
                    continue

                if (
                    maze.grid[y][x][wall]
                    != maze.grid[ny][nx][opposite]
                ):
                    return False

    return True


def braid_maze(
    maze: "MazeGenerator",
    blocked: set[Position],
    seed: int | None = None,
    max_dead_ends: int = 0,
    min_loops: int = 2,
) -> int:
    """Transform a perfect maze into a valid non-perfect maze."""
    maze._validate_blocked(blocked)
    maze._validate_seed(seed)

    _validate_limits(
        max_dead_ends,
        min_loops,
    )

    if not _walls_are_coherent(
        maze
    ):
        raise ValueError(
            "maze walls are incoherent before braiding"
        )

    if not _is_fully_connected(
        maze,
        blocked,
    ):
        raise ValueError(
            "maze must be fully connected before braiding"
        )

    rng = random.Random(seed)

    while True:
        real_dead_ends = find_real_dead_ends(
            maze,
            blocked,
        )

        loops = count_independent_loops(
            maze,
            blocked,
        )

        if (
            len(real_dead_ends) <= max_dead_ends
            and loops >= min_loops
        ):
            break

        rng.shuffle(real_dead_ends)

        opened = False

        for dead_end in real_dead_ends:
            candidates = _closed_candidates(
                maze,
                dead_end,
                blocked,
            )

            rng.shuffle(candidates)

            for candidate in candidates:
                if not _opening_is_safe(
                    maze,
                    dead_end,
                    candidate,
                ):
                    continue

                maze.open_passage(
                    dead_end[0],
                    dead_end[1],
                    candidate[0],
                    candidate[1],
                )

                opened = True
                break

            if opened:
                break

        if opened:
            continue

        if loops < min_loops:
            all_cells: list[Position] = []

            for y in range(maze.height):
                for x in range(maze.width):
                    position = (x, y)

                    if position not in blocked:
                        all_cells.append(position)

            rng.shuffle(all_cells)

            for position in all_cells:
                candidates = _closed_candidates(
                    maze,
                    position,
                    blocked,
                )

                rng.shuffle(candidates)

                for candidate in candidates:
                    if not _opening_is_safe(
                        maze,
                        position,
                        candidate,
                    ):
                        continue

                    maze.open_passage(
                        position[0],
                        position[1],
                        candidate[0],
                        candidate[1],
                    )

                    opened = True
                    break

                if opened:
                    break

        if not opened:
            break

    real_dead_ends = find_real_dead_ends(
        maze,
        blocked,
    )

    loops = count_independent_loops(
        maze,
        blocked,
    )

    if not _walls_are_coherent(
        maze
    ):
        raise ValueError(
            "braiding produced incoherent walls"
        )

    if not _is_fully_connected(
        maze,
        blocked,
    ):
        raise ValueError(
            "braiding broke maze connectivity"
        )

    if _has_open_3x3(
        maze
    ):
        raise ValueError(
            "braiding created a forbidden 3x3 open area"
        )

    if not _key_cells_reachable(
        maze,
        blocked,
    ):
        raise ValueError(
            "corners or centre are not reachable"
        )

    if loops < min_loops:
        raise ValueError(
            f"maze has only {loops} independent loop(s); "
            f"at least {min_loops} required"
        )

    if len(real_dead_ends) > max_dead_ends:
        raise ValueError(
            f"maze has {len(real_dead_ends)} real dead-end(s); "
            f"at most {max_dead_ends} allowed"
        )

    return loops
