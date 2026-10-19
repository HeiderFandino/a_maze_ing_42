import random

from collections.abc import Iterator
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .maze import MazeGenerator


Position = tuple[int, int]
GenerationEvent = tuple[str, object]


def generate_dfs(
    maze: "MazeGenerator",
    blocked: set[Position],
    seed: int | None = None,
) -> Iterator[GenerationEvent]:
    """Generate a perfect maze using iterative depth-first search."""
    maze._validate_blocked(blocked)
    maze._validate_seed(seed)

    maze.grid = maze._create_grid()

    if seed is None:
        maze.seed_utilizada = random.SystemRandom().randrange(
            0,
            2**32,
        )
    else:
        maze.seed_utilizada = seed

    rng = random.Random(
        maze.seed_utilizada
    )

    traversable: list[Position] = []

    for y in range(maze.height):
        for x in range(maze.width):
            position = (x, y)

            if position not in blocked:
                traversable.append(
                    position
                )

    if not traversable:
        raise ValueError(
            "maze has no traversable cells"
        )

    if maze.entry_pos in blocked:
        raise ValueError(
            "entry_pos cannot be blocked"
        )

    if maze.exit_pos in blocked:
        raise ValueError(
            "exit_pos cannot be blocked"
        )

    start = maze.entry_pos

    visited: set[Position] = {
        start
    }

    stack: list[Position] = [
        start
    ]

    yield (
        "start",
        start,
    )

    while stack:
        current = stack[-1]

        x, y = current

        candidates: list[Position] = []

        for neighbor in maze._get_neighbors(
            x,
            y,
        ):
            if neighbor in blocked:
                continue

            if neighbor in visited:
                continue

            candidates.append(
                neighbor
            )

        if not candidates:
            stack.pop()

            yield (
                "backtrack",
                current,
            )

            continue

        next_cell = rng.choice(
            candidates
        )

        maze.open_passage(
            current[0],
            current[1],
            next_cell[0],
            next_cell[1],
        )

        visited.add(
            next_cell
        )

        stack.append(
            next_cell
        )

        yield (
            "passage",
            (
                current,
                next_cell,
            ),
        )

    expected = (
        maze.width
        * maze.height
        - len(blocked)
    )

    if len(visited) != expected:
        raise ValueError(
            "maze generation did not reach "
            "all traversable cells"
        )


def generate_prim(
    maze: "MazeGenerator",
    blocked: set[Position],
    seed: int | None = None,
) -> Iterator[GenerationEvent]:
    """Generate a perfect maze using randomized Prim."""
    maze._validate_blocked(blocked)
    maze._validate_seed(seed)

    maze.grid = maze._create_grid()

    if seed is None:
        maze.seed_utilizada = random.SystemRandom().randrange(
            0,
            2**32,
        )
    else:
        maze.seed_utilizada = seed

    rng = random.Random(
        maze.seed_utilizada
    )

    if maze.entry_pos in blocked:
        raise ValueError(
            "entry_pos cannot be blocked"
        )

    if maze.exit_pos in blocked:
        raise ValueError(
            "exit_pos cannot be blocked"
        )

    traversable_count = (
        maze.width
        * maze.height
        - len(blocked)
    )

    if traversable_count <= 0:
        raise ValueError(
            "maze has no traversable cells"
        )

    start = maze.entry_pos

    visited: set[Position] = {
        start
    }

    frontier: list[Position] = []

    for neighbor in maze._get_neighbors(
        start[0],
        start[1],
    ):
        if neighbor in blocked:
            continue

        if neighbor in visited:
            continue

        frontier.append(
            neighbor
        )

    yield (
        "start",
        start,
    )

    while frontier:
        frontier_index = rng.randrange(
            len(frontier)
        )

        current = frontier.pop(
            frontier_index
        )

        if current in visited:
            continue

        visited_neighbors: list[Position] = []

        for neighbor in maze._get_neighbors(
            current[0],
            current[1],
        ):
            if neighbor in blocked:
                continue

            if neighbor in visited:
                visited_neighbors.append(
                    neighbor
                )

        if not visited_neighbors:
            continue

        parent = rng.choice(
            visited_neighbors
        )

        maze.open_passage(
            current[0],
            current[1],
            parent[0],
            parent[1],
        )

        visited.add(
            current
        )

        yield (
            "passage",
            (
                parent,
                current,
            ),
        )

        for neighbor in maze._get_neighbors(
            current[0],
            current[1],
        ):
            if neighbor in blocked:
                continue

            if neighbor in visited:
                continue

            if neighbor in frontier:
                continue

            frontier.append(
                neighbor
            )

    if len(visited) != traversable_count:
        raise ValueError(
            "Prim generation did not reach "
            "all traversable cells"
        )
