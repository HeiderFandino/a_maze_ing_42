def create_cell() -> dict[str, bool]:
    """Create a new cell with all four walls closed."""
    return {
        "north": True,
        "east": True,
        "south": True,
        "west": True,
    }


class MazeGenerator:
    """Generate mazes using a grid of independent cells."""

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

    
