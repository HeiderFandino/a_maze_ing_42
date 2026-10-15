from collections.abc import Iterator

from .generation import generate_dfs
from .pathfinding import (
    path_to_directions as find_path_directions,
    reconstruct_path as build_path,
    shortest_path as find_shortest_path,
    shortest_path_steps as find_shortest_path_steps,
)


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
        if type(width) is not int or type(height) is not int:
            raise TypeError(
                "width and height must be integers"
            )

        if width <= 0 or height <= 0:
            raise ValueError(
                "width and height must be greater than 0"
            )

        self.width: int = width
        self.height: int = height

        self._validate_coordinate(
            entry_pos,
            "entry_pos",
        )
        self._validate_coordinate(
            exit_pos,
            "exit_pos",
        )

        self.entry_pos: tuple[int, int] = entry_pos
        self.exit_pos: tuple[int, int] = exit_pos

        self._validate_endpoints()

        self.grid: list[
            list[
                dict[str, bool]
            ]
        ] = self._create_grid()

    @staticmethod
    def _validate_coordinate(
        position: object,
        name: str,
    ) -> None:
        """Validate the structure and types of a coordinate."""
        if type(position) is not tuple:
            raise TypeError(
                f"{name} must be a tuple"
            )

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

    def _create_grid(
        self,
    ) -> list[list[dict[str, bool]]]:
        """Create a grid with all cell walls closed."""
        grid: list[
            list[
                dict[str, bool]
            ]
        ] = []

        for _y in range(self.height):
            row: list[dict[str, bool]] = []

            for _x in range(self.width):
                row.append(
                    create_cell()
                )

            grid.append(row)

        return grid

    def is_in_bounds(
        self,
        x: int,
        y: int,
    ) -> bool:
        """Return whether coordinates are inside the grid."""
        if type(x) is not int or type(y) is not int:
            raise TypeError(
                "x and y must be integers"
            )

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
        coordinates = (
            x1,
            y1,
            x2,
            y2,
        )

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
            (
                y1 == y2
                and abs(x1 - x2) == 1
            )
            or
            (
                x1 == x2
                and abs(y1 - y2) == 1
            )
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

    def _validate_endpoints(
        self,
    ) -> None:
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
            raise TypeError(
                "x and y must be integers"
            )

        if not self.is_in_bounds(x, y):
            raise ValueError(
                "coordinates must be inside the grid"
            )

        candidates: list[
            tuple[int, int]
        ] = [
            (x, y - 1),
            (x + 1, y),
            (x, y + 1),
            (x - 1, y),
        ]

        neighbors: list[
            tuple[int, int]
        ] = []

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
        neighbors: list[
            tuple[int, int]
        ] = []

        for position in self._get_neighbors(
            x,
            y,
        ):
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

            if not self.is_in_bounds(
                x,
                y,
            ):
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
    def _validate_seed(
        seed: object,
    ) -> None:
        """Validate the random-generation seed."""
        if (
            seed is not None
            and type(seed) is not int
        ):
            raise TypeError(
                "seed must be an integer or None"
            )

    def _get_42_pattern(
        self,
    ) -> set[tuple[int, int]]:
        """Return blocked cells forming a centered 42 pattern."""
        pattern_height = 5

        four_pattern: set[
            tuple[int, int]
        ] = {
            (0, 0),
            (2, 0),
            (0, 1),
            (2, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (2, 4),
        }

        two_pattern: set[
            tuple[int, int]
        ] = {
            (0, 0),
            (1, 0),
            (2, 0),
            (2, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (0, 3),
            (0, 4),
            (1, 4),
            (2, 4),
        }

        center_gap = 1

        digit_width = 3
        pattern_width = (
            digit_width
            + center_gap
            + digit_width
        )

        required_width = (
            pattern_width + 2
        )
        required_height = (
            pattern_height + 2
        )

        if (
            self.width < required_width
            or self.height < required_height
        ):
            print(
                "WARNING: maze is too small "
                "to contain the 42 pattern"
            )
            print(
                "CREATING MAZE WITHOUT "
                "42 PATTERN"
            )

            return set()

        start_x = (
            self.width
            - pattern_width
        ) // 2

        start_y = (
            self.height
            - pattern_height
        ) // 2

        blocked: set[
            tuple[int, int]
        ] = set()

        for (
            relative_x,
            relative_y,
        ) in four_pattern:
            blocked.add(
                (
                    start_x + relative_x,
                    start_y + relative_y,
                )
            )

        two_start_x = (
            start_x
            + digit_width
            + center_gap
        )

        for (
            relative_x,
            relative_y,
        ) in two_pattern:
            blocked.add(
                (
                    two_start_x + relative_x,
                    start_y + relative_y,
                )
            )

        if self.entry_pos in blocked:
            raise ValueError(
                "42 pattern must not overlap entry_pos"
            )

        if self.exit_pos in blocked:
            raise ValueError(
                "42 pattern must not overlap exit_pos"
            )

        return blocked

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
        """Generate a perfect maze using iterative DFS."""
        return generate_dfs(
            self,
            blocked,
            seed,
        )

    def _get_open_neighbors(
        self,
        x: int,
        y: int,
    ) -> list[tuple[int, int]]:
        """Return neighbors reachable through coherent open walls."""
        if type(x) is not int or type(y) is not int:
            raise TypeError(
                "x and y must be integers"
            )

        if not self.is_in_bounds(
            x,
            y,
        ):
            raise ValueError(
                "coordinates must be inside the grid"
            )

        cell = self.grid[y][x]

        directions = [
            (
                "north",
                "south",
                0,
                -1,
            ),
            (
                "east",
                "west",
                1,
                0,
            ),
            (
                "south",
                "north",
                0,
                1,
            ),
            (
                "west",
                "east",
                -1,
                0,
            ),
        ]

        neighbors: list[
            tuple[int, int]
        ] = []

        for (
            wall,
            opposite_wall,
            dx,
            dy,
        ) in directions:
            if wall not in cell:
                raise RuntimeError(
                    f"cell {(x, y)} "
                    f"is missing wall '{wall}'"
                )

            if type(cell[wall]) is not bool:
                raise RuntimeError(
                    f"wall '{wall}' "
                    f"in cell {(x, y)} "
                    "must be bool"
                )

            nx = x + dx
            ny = y + dy

            if not self.is_in_bounds(
                nx,
                ny,
            ):
                if cell[wall] is False:
                    raise ValueError(
                        f"cell {(x, y)} "
                        "has an open wall "
                        "leading outside the grid"
                    )

                continue

            neighbor = self.grid[ny][nx]

            if opposite_wall not in neighbor:
                raise RuntimeError(
                    f"cell {(nx, ny)} "
                    "is missing wall "
                    f"'{opposite_wall}'"
                )

            if (
                type(
                    neighbor[
                        opposite_wall
                    ]
                )
                is not bool
            ):
                raise RuntimeError(
                    f"wall '{opposite_wall}' "
                    f"in cell {(nx, ny)} "
                    "must be bool"
                )

            if (
                cell[wall]
                != neighbor[
                    opposite_wall
                ]
            ):
                raise ValueError(
                    "incoherent walls between "
                    f"{(x, y)} and {(nx, ny)}"
                )

            if cell[wall] is False:
                neighbors.append(
                    (
                        nx,
                        ny,
                    )
                )

        return neighbors

    def _reconstruct_path(
        self,
        parents: dict[
            tuple[int, int],
            tuple[int, int] | None,
        ],
    ) -> list[tuple[int, int]]:
        """Reconstruct a path from exit to entry."""
        return build_path(
            self,
            parents,
        )

    def shortest_path(
        self,
    ) -> list[tuple[int, int]]:
        """Return the shortest path from entry to exit."""
        return find_shortest_path(
            self
        )

    def path_to_directions(
        self,
        path: list[tuple[int, int]],
    ) -> str:
        """Convert a path into N, E, S and W directions."""
        return find_path_directions(
            self,
            path,
        )

    def shortest_path_steps(
        self,
    ) -> Iterator[
        tuple[
            str,
            set[tuple[int, int]]
            | list[tuple[int, int]],
        ]
    ]:
        """Expose BFS states and the final shortest path."""
        return find_shortest_path_steps(
            self
        )