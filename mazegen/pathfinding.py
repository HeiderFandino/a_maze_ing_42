from collections import deque
from collections.abc import Iterator
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .maze import MazeGenerator


def reconstruct_path(
    maze: "MazeGenerator",
    parents: dict[
        tuple[int, int],
        tuple[int, int] | None,
    ],
) -> list[tuple[int, int]]:
    """Reconstruct a path from exit back to entry."""

    if type(parents) is not dict:
        raise TypeError("parents must be a dictionary")

    if maze.exit_pos not in parents:
        raise ValueError(
            "exit_pos is missing from the parent map"
        )

    path: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()

    current: tuple[int, int] | None = maze.exit_pos

    while current is not None:
        if current in seen:
            raise RuntimeError(
                "cycle detected while reconstructing path"
            )

        seen.add(current)
        path.append(current)

        if current not in parents:
            raise RuntimeError(
                f"missing parent for cell {current}"
            )

        current = parents[current]

    path.reverse()

    if not path:
        raise RuntimeError(
            "reconstructed path is unexpectedly empty"
        )

    if path[0] != maze.entry_pos:
        raise RuntimeError(
            "reconstructed path does not start at entry_pos"
        )

    if path[-1] != maze.exit_pos:
        raise RuntimeError(
            "reconstructed path does not end at exit_pos"
        )

    return path


def shortest_path(
    maze: "MazeGenerator",
) -> list[tuple[int, int]]:
    """Return the shortest path from entry to exit using BFS."""

    if not hasattr(maze, "grid"):
        raise RuntimeError("grid is not initialized")

    if type(maze.grid) is not list or not maze.grid:
        raise RuntimeError(
            "grid must be a non-empty list"
        )

    queue: deque[tuple[int, int]] = deque(
        [maze.entry_pos]
    )

    visited: set[tuple[int, int]] = {
        maze.entry_pos
    }

    parents: dict[
        tuple[int, int],
        tuple[int, int] | None,
    ] = {
        maze.entry_pos: None
    }

    while queue:
        current = queue.popleft()

        if current == maze.exit_pos:
            return reconstruct_path(
                maze,
                parents,
            )

        neighbors = maze._get_open_neighbors(
            current[0],
            current[1],
        )

        for neighbor in neighbors:
            if neighbor in visited:
                continue

            visited.add(neighbor)
            parents[neighbor] = current
            queue.append(neighbor)

    raise ValueError(
        "no path exists between entry_pos and exit_pos"
    )


def path_to_directions(
    maze: "MazeGenerator",
    path: list[tuple[int, int]],
) -> str:
    """Convert a valid path into N, E, S and W directions."""

    if type(path) is not list:
        raise TypeError(
            "path must be a list of coordinate tuples"
        )

    if not path:
        raise ValueError("path must not be empty")

    for index, position in enumerate(path):
        maze._validate_coordinate(
            position,
            f"path[{index}]",
        )

        if not maze.is_in_bounds(
            position[0],
            position[1],
        ):
            raise ValueError(
                f"path position {position} "
                "must be inside the grid"
            )

    if path[0] != maze.entry_pos:
        raise ValueError(
            "path must start at entry_pos"
        )

    if path[-1] != maze.exit_pos:
        raise ValueError(
            "path must end at exit_pos"
        )

    directions = ""

    for index in range(len(path) - 1):
        current = path[index]
        next_position = path[index + 1]

        open_neighbors = maze._get_open_neighbors(
            current[0],
            current[1],
        )

        if next_position not in open_neighbors:
            raise ValueError(
                f"invalid path step from "
                f"{current} to {next_position}"
            )

        x1, y1 = current
        x2, y2 = next_position

        dx = x2 - x1
        dy = y2 - y1

        if dx == 1 and dy == 0:
            directions += "E"

        elif dx == -1 and dy == 0:
            directions += "W"

        elif dx == 0 and dy == 1:
            directions += "S"

        elif dx == 0 and dy == -1:
            directions += "N"

        else:
            raise RuntimeError(
                "unexpected movement in validated path"
            )

    return directions


def shortest_path_steps(
    maze: "MazeGenerator",
) -> Iterator[
    tuple[
        str,
        set[tuple[int, int]]
        | list[tuple[int, int]],
    ]
]:
    """Expose BFS search states and the final shortest path."""

    queue: deque[tuple[int, int]] = deque(
        [maze.entry_pos]
    )

    visited: set[tuple[int, int]] = {
        maze.entry_pos
    }

    parents: dict[
        tuple[int, int],
        tuple[int, int] | None,
    ] = {
        maze.entry_pos: None
    }

    while queue:
        current = queue.popleft()

        yield (
            "search",
            set(visited),
        )

        if current == maze.exit_pos:
            path = reconstruct_path(
                maze,
                parents,
            )

            yield (
                "solution",
                path,
            )

            return

        for neighbor in maze._get_open_neighbors(
            current[0],
            current[1],
        ):
            if neighbor in visited:
                continue

            visited.add(neighbor)
            parents[neighbor] = current
            queue.append(neighbor)

    raise ValueError(
        "no path exists between entry_pos and exit_pos"
    )
