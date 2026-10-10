import random

from collections.abc import Iterator


def create_cell() -> dict[str, bool]:
    """Create a new cell with all four walls closed."""
    return {
        "north": True,
        "east": True,
        "south": True,
        "west": True,
    }


class MazeGenerator:
    """Generate mazes using a grid of independent cells.

    Coordinates use (x, y): x increases right and y increases down.
    Cells are stored as grid[y][x].
    Wall values are True for closed and False for open.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry_pos: tuple[int, int],
        exit_pos: tuple[int, int],
    ) -> None:
        """Initialize a maze generator with validated parameters."""

        # Validate dimensions: type first, value second.
        if type(width) is not int or type(height) is not int:
            raise TypeError("width and height must be integers")

        if width <= 0 or height <= 0:
            raise ValueError("width and height must be greater than 0")

        self.width: int = width
        self.height: int = height

        # Validate coordinate structure and component types.
        self._validate_coordinate(entry_pos, "entry_pos")
        self._validate_coordinate(exit_pos, "exit_pos")

        self.entry_pos: tuple[int, int] = entry_pos
        self.exit_pos: tuple[int, int] = exit_pos

        # Validate coordinate values relative to the grid.
        self._validate_endpoints()

        self.grid: list[list[dict[str, bool]]] = self._create_grid()

    @staticmethod
    def _validate_coordinate(
        position: object,
        name: str,
    ) -> None:
        """Validate the structure and types of a coordinate."""

        if type(position) is not tuple:
            raise TypeError(f"{name} must be a tuple")

        if len(position) != 2:
            raise ValueError(
                f"{name} must contain exactly two coordinates"
            )

        x = position[0]
        y = position[1]

        if type(x) is not int or type(y) is not int:
            raise TypeError(
                f"{name} coordinates must be integers"
            )

    def _create_grid(self) -> list[list[dict[str, bool]]]:
        """Create a grid with all cell walls closed."""
        grid: list[list[dict[str, bool]]] = []

        for _y in range(self.height):
            row: list[dict[str, bool]] = []

            for _x in range(self.width):
                row.append(create_cell())

            grid.append(row)

        return grid

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Return whether coordinates are inside the grid."""

        if type(x) is not int or type(y) is not int:
            raise TypeError("x and y must be integers")

        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def open_passage(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> None:
        """Open a passage between two adjacent grid cells."""

        coordinates = (x1, y1, x2, y2)

        for coordinate in coordinates:
            if type(coordinate) is not int:
                raise TypeError(
                    "cell coordinates must be integers"
                )

        if (
            not self.is_in_bounds(x1, y1)
            or not self.is_in_bounds(x2, y2)
        ):
            raise ValueError(
                "both cells must be inside the grid"
            )

        adjacent = (
            (y1 == y2 and abs(x1 - x2) == 1)
            or
            (x1 == x2 and abs(y1 - y2) == 1)
        )

        if not adjacent:
            raise ValueError(
                "cells must be orthogonally adjacent"
            )

        if x2 > x1:
            self.grid[y1][x1]["east"] = False
            self.grid[y2][x2]["west"] = False

        elif x2 < x1:
            self.grid[y1][x1]["west"] = False
            self.grid[y2][x2]["east"] = False

        elif y2 > y1:
            self.grid[y1][x1]["south"] = False
            self.grid[y2][x2]["north"] = False

        elif y2 < y1:
            self.grid[y1][x1]["north"] = False
            self.grid[y2][x2]["south"] = False

    def _validate_endpoints(self) -> None:
        """Validate entry and exit against grid invariants."""

        if not self.is_in_bounds(
            self.entry_pos[0],
            self.entry_pos[1],
        ):
            raise ValueError(
                "entry_pos must be inside the grid"
            )

        if not self.is_in_bounds(
            self.exit_pos[0],
            self.exit_pos[1],
        ):
            raise ValueError(
                "exit_pos must be inside the grid"
            )

        if self.entry_pos == self.exit_pos:
            raise ValueError(
                "entry_pos and exit_pos must be different"
            )

    def _get_neighbors(
        self,
        x: int,
        y: int,
    ) -> list[tuple[int, int]]:
        """Return in-bounds neighbors in N, E, S, W order."""

        if type(x) is not int or type(y) is not int:
            raise TypeError("x and y must be integers")

        if not self.is_in_bounds(x, y):
            raise ValueError(
                "coordinates must be inside the grid"
            )

        candidates: list[tuple[int, int]] = [
            (x, y - 1),
            (x + 1, y),
            (x, y + 1),
            (x - 1, y),
        ]

        neighbors: list[tuple[int, int]] = []

        for position in candidates:
            if self.is_in_bounds(
                position[0],
                position[1],
            ):
                neighbors.append(position)

        return neighbors

    def _get_available_neighbors(
        self,
        x: int,
        y: int,
        visited: set[tuple[int, int]],
        blocked: set[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        """Return neighboring cells that are unvisited and unblocked."""

        neighbors: list[tuple[int, int]] = []

        for position in self._get_neighbors(x, y):
            if (
                position not in visited
                and position not in blocked
            ):
                neighbors.append(position)

        return neighbors

    def _validate_blocked(
        self,
        blocked: object,
    ) -> None:
        """Validate the set of blocked cells."""

        if type(blocked) is not set:
            raise TypeError(
                "blocked must be a set of coordinate tuples"
            )

        for position in blocked:
            self._validate_coordinate(
                position,
                "blocked position",
            )

            x = position[0]
            y = position[1]

            if not self.is_in_bounds(x, y):
                raise ValueError(
                    f"blocked cell {position} "
                    "must be inside the grid"
                )

        if self.entry_pos in blocked:
            raise ValueError(
                "entry_pos must not be blocked"
            )

        if self.exit_pos in blocked:
            raise ValueError(
                "exit_pos must not be blocked"
            )

    @staticmethod
    def _validate_seed(seed: object) -> None:
        """Validate the random-generation seed."""

        if seed is not None and type(seed) is not int:
            raise TypeError(
                "seed must be an integer or None"
            )

    def _generate_dfs(
        self,
        blocked: set[tuple[int, int]],
        seed: int | None = None,
    ) -> Iterator[
        tuple[
            tuple[int, int],
            tuple[int, int],
        ]
    ]:
        """Carve a reproducible perfect maze using iterative DFS.

        Blocked cells are excluded from traversal.
        Each opened passage is yielded as:
        ((x1, y1), (x2, y2)).
        """

        self._validate_blocked(blocked)
        self._validate_seed(seed)

        self.grid = self._create_grid()

        rng = random.Random(seed)

        visited: set[tuple[int, int]] = {
            self.entry_pos
        }

        stack: list[tuple[int, int]] = [
            self.entry_pos
        ]

        while stack:
            current = stack[-1]

            neighbors = self._get_available_neighbors(
                current[0],
                current[1],
                visited,
                blocked,
            )

            if not neighbors:
                stack.pop()
                continue

            next_pos = rng.choice(neighbors)

            self.open_passage(
                current[0],
                current[1],
                next_pos[0],
                next_pos[1],
            )

            visited.add(next_pos)
            stack.append(next_pos)

            yield (current, next_pos)

        traversable_cells = (
            self.width
            * self.height
            - len(blocked)
        )

        if len(visited) != traversable_cells:
            raise ValueError(
                "traversable cells must form one connected area"
            )