import random

from collections.abc import Iterator
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .maze import MazeGenerator


def generate_dfs(
    maze: "MazeGenerator",
    blocked: set[tuple[int, int]],
    seed: int | None = None,
) -> Iterator[
    tuple[
        tuple[int, int],
        tuple[int, int],
    ]
]:
    """Carve a reproducible perfect maze using iterative DFS."""

    maze._validate_blocked(blocked)
    maze._validate_seed(seed)

    maze.grid = maze._create_grid()

    if seed is None:
        maze.seed_utilizada = random.randint(0, 1000000)
    else:
        maze.seed_utilizada = seed

    rng = random.Random(maze.seed_utilizada)

    visited: set[tuple[int, int]] = {
        maze.entry_pos
    }

    stack: list[tuple[int, int]] = [
        maze.entry_pos
    ]

    while stack:
        current = stack[-1]

        neighbors = maze._get_available_neighbors(
            current[0],
            current[1],
            visited,
            blocked,
        )

        if not neighbors:
            stack.pop()
            continue

        next_pos = rng.choice(neighbors)

        maze.open_passage(
            current[0],
            current[1],
            next_pos[0],
            next_pos[1],
        )

        visited.add(next_pos)
        stack.append(next_pos)

        yield (current, next_pos)

    traversable_cells = (
        maze.width
        * maze.height
        - len(blocked)
    )

    if len(visited) != traversable_cells:
        raise ValueError(
            "traversable cells must form one connected area"
        )
