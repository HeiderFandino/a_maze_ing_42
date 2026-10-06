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
    def __init__(self, width: int, height: int) -> None:
        """Initialize the generator with positive grid dimensions."""
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be greater than 0")

        self.width: int = width
        self.height: int = height
        self.grid: list[list[dict[str, bool]]] = self._create_grid()

    def _create_grid(self) -> list[list[dict[str, bool]]]:
        """Create a grid with all cell walls closed."""
        grid: list[list[dict[str, bool]]] = []

        for y in range(self.height):
            row: list[dict[str, bool]] = []
            for x in range(self.width):
                row.append(create_cell())
            grid.append(row)

        return grid

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Return whether the coordinates are inside the grid."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return True

    def open_passage(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Open the passage between two adjacent cells in the grid."""
        if not self.is_in_bounds(x1, y1) or not self.is_in_bounds(x2, y2):
            raise ValueError("Both cells must be inside the grid")
        adjacent = (
                (y1 == y2 and abs(x1 - x2) == 1)
                or (x1 == x2 and abs(y1 - y2) == 1)
        )

        if not adjacent:
            raise ValueError("Cells must be adjacent")

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
