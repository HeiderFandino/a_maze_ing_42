import random
import os
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

    def _validate_endpoints(self, entry_pos: tuple[int, int], exit_pos: tuple[int, int]) -> None:
        """Validate that entry and exit are distinct cells inside the grid."""
        if not self.is_in_bounds(entry_pos[0], entry_pos[1]):
            raise ValueError("Entry must be inside the grid")

        if not self.is_in_bounds(exit_pos[0], exit_pos[1]):
            raise ValueError("Exit must be inside the grid")

        if entry_pos == exit_pos:
            raise ValueError("Entry and exit must be different")

    def _get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return in-bounds neighbors in north, east, south, west order."""
        candidates: list[tuple[int, int]] = [
            (x, y - 1),
            (x + 1, y),
            (x, y + 1),
            (x - 1, y),
        ]

        neighbors: list[tuple[int, int]] = []

        for position in candidates:
            if self.is_in_bounds(position[0], position[1]):
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
            if position not in visited and position not in blocked:
                neighbors.append(position)

        return neighbors

    def _generate_dfs(
        self,
        entry_pos: tuple[int, int],
        blocked: set[tuple[int, int]],
        seed: int | None = None,
    ) -> Iterator[tuple[tuple[int, int], tuple[int, int]]]:
        """Carve a perfect maze from entry_pos, skipping blocked cells.

        Use seed for reproducible choices. Yield each opened passage as
        a pair of coordinates. Raise ValueError for invalid positions
        or disconnected traversable cells.
        """
        if not self.is_in_bounds(entry_pos[0], entry_pos[1]):
            raise ValueError("Entry must be inside the grid")

        for position in blocked:
            if not self.is_in_bounds(position[0], position[1]):
                raise ValueError("Blocked cells must be inside the grid")

        if entry_pos in blocked:
            raise ValueError("Entry must not be a blocked cell")

        self.grid = self._create_grid()
        rng = random.Random(seed)
        visited: set[tuple[int, int]] = {entry_pos}
        stack: list[tuple[int, int]] = [entry_pos]

        while stack:
            current = stack[-1]
            neighbors = self._get_available_neighbors(
                current[0], current[1], visited, blocked,
            )

            if not neighbors:
                stack.pop()
            else:
                next_pos = rng.choice(neighbors)
                self.open_passage(
                    current[0], current[1], next_pos[0], next_pos[1],
                )
                visited.add(next_pos)
                stack.append(next_pos)
                os.system('clear' if os.name == 'posix' else 'cls')
                yield (current, next_pos)

        if len(visited) != self.width * self.height - len(blocked):
            raise ValueError("Traversable cells must form one connected area")

    def draw_solid(self, maze_color: str = "\033[37m",
                   blocked: set[tuple[int, int]] = None) -> None:
        """Dibuja el laberinto usando bloques
        sólidos
        maze_color: Código ANSI para el color (por defecto blanco).
        blocked: Conjunto de celdas que actúan como obstáculos sólidos.
        """
        if blocked is None:
            blocked = set()

        w = "█"  # Carácter de pared sólida

        # Iteramos por cada fila de celdas
        for y in range(self.height):
            line1 = ""
            line2 = ""

            for x in range(self.width):
                # Si la celda actual o sus vecinas son bloques, pintamos todo
                if (x, y) in blocked:
                    line1 += f"{w}{w}{w}{w}{w}"
                    line2 += f"{w}{w}{w}{w}{w}"
                    continue

                cell = self.grid[y][x]

                # --- LÍNEA 1: Pared Norte ---
                if cell["north"]:
                    line1 += f"{w}{w}{w}{w}{w}"
                else:
                    # Si no hay pared norte, dejamos el pasillo abierto,
                    # pero mantenemos las esquinas sólidas
                    line1 += f"{w}   {w}"

                # --- LÍNEA 2: Paredes Oeste, Centro y Este ---
                left = f"{w}" if cell["west"] else " "
                right = f"{w}" if cell["east"] else " "

                # Representación del centro de la celda (vacío)
                cell_representation = "   "

                line2 += f"{left}{cell_representation}{right}"

            # Imprimimos las dos líneas procesadas para esta fila
            print(f"{maze_color}{line1}")
            print(f"{maze_color}{line2}")

        # Al igual que el segundo código, añadimos la línea de cierre inferior
        print(f"{maze_color}{w}{w}{w}{w}{w}" * self.width)


if __name__ == "__main__":
    # Configuración del tamaño del laberinto
    ANCHO = 20
    ALTO = 20

    # Creamos la instancia del generador
    generador = MazeGenerator(width=ANCHO, height=ALTO)

    # Definimos celdas bloqueadas (obstáculos)
    obstaculos = {(1, 1)}

    # Coordenada de inicio para empezar a generar
    punto_inicio = (0, 0)

    # Códigos ANSI de color
    COLOR_CYAN = "\033[96m"
    COLOR_RESET = "\033[0m"

    print("Generando el laberinto en segundo plano...")

    # Consumimos todo el generador por completo para que calcule el laberinto
    # sin imprimir nada en pantalla todavía.
    for _ in generador._generate_dfs(entry_pos=punto_inicio,
                                     blocked=obstaculos, seed=None):
        pass  # No hacemos nada en cada paso, solo dejamos que termine

    # ¡Un único dibujo al final del proceso!
    generador.draw_solid(maze_color=COLOR_CYAN, blocked=obstaculos)

    print(f"\n{COLOR_RESET}[+] ¡Laberinto generado y dibujado con éxito!")
