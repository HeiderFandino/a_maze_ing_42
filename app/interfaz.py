from mazegen.maze import MazeGenerator
from app import colors

import time
import os


class interfaz(MazeGenerator):
    def __init__(self, width: int, height: int, entry_pos: tuple[int, int], exit_pos: tuple[int, int]) -> None:
        super().__init__(width, height, entry_pos, exit_pos)
        self.animation: bool = False

    def draw_solid(
        self,
        maze_color: str = "\033[37m",
        blocked: set[tuple[int, int]] | None = None,
        path: list[tuple[int, int]] | None = None,
        visited: set[tuple[int, int]] | None = None
    ) -> None:
        """Dibuja el laberinto usando bloques sólidos."""
        if not hasattr(self, 'grid') or not self.grid or len(self.grid) == 0:
            raise RuntimeError(
                "No se puede dibujar: La cuadrícula del laberinto "
                "no está inicializada o está vacía."
            )

        if blocked is None:
            blocked = set()

        if path is None:
            path = []

        if visited is None:
            visited = set()

        if not self.is_in_bounds(
            self.entry_pos[0],
            self.entry_pos[1]
        ):
            raise ValueError(
                f"La coordenada de inicio 'entry_pos' "
                f"{self.entry_pos} está fuera de los límites del laberinto."
            )

        for pos in blocked:
            if not self.is_in_bounds(pos[0], pos[1]):
                raise ValueError(
                    f"La celda bloqueada {pos} "
                    f"está fuera de los límites del laberinto."
                )

        w = "█"
        path_set = set(path)

        for y in range(self.height):
            line1 = ""
            line2 = ""

            for x in range(self.width):
                current = (x, y)

                if current in blocked:
                    line1 += (
                        f"{colors.GRAY}"
                        f"{w}{w}{w}{w}{w}"
                        f"{maze_color}"
                    )
                    line2 += (
                        f"{colors.GRAY}"
                        f"{w}{w}{w}{w}{w}"
                        f"{maze_color}"
                    )
                    continue

                cell = self.grid[y][x]

                # Pared norte
                if cell["north"]:
                    line1 += f"{w}{w}{w}{w}{w}"
                else:
                    north = (x, y - 1)

                    if (
                        current in path_set
                        and north in path_set
                    ):
                        line1 += (
                            f"{w}"
                            f"{colors.YELLOW}"
                            f"███"
                            f"{maze_color}"
                            f"{w}"
                        )
                    else:
                        line1 += f"{w}   {w}"

                # Pared izquierda
                if cell["west"]:
                    left = w
                elif (
                    current in path_set
                    and (x - 1, y) in path_set
                ):
                    left = (
                        f"{colors.YELLOW}"
                        f"█"
                        f"{maze_color}"
                    )
                else:
                    left = " "

                # Pared derecha
                if cell["east"]:
                    right = w
                elif (
                    current in path_set
                    and (x + 1, y) in path_set
                ):
                    right = (
                        f"{colors.YELLOW}"
                        f"█"
                        f"{maze_color}"
                    )
                else:
                    right = " "

                # Contenido de la celda
                if current == self.entry_pos:
                    cell_representation = " S "

                elif current == self.exit_pos:
                    cell_representation = " E "

                elif current in path_set:
                    cell_representation = (
                        f"{colors.YELLOW}"
                        f"███"
                        f"{maze_color}"
                    )

                elif current in visited:
                    cell_representation = " * "

                else:
                    cell_representation = "   "

                line2 += (
                    f"{left}"
                    f"{cell_representation}"
                    f"{right}"
                )

            print(f"{maze_color}{line1}")
            print(f"{maze_color}{line2}")

        print(
            f"{maze_color}"
            f"{w}{w}{w}{w}{w}" * self.width
        )
        
    def change_animation(self) -> None:
        self.animation = not self.animation

    def get_maze_str(self) -> str:
        """Convierte la cuadrícula de diccionarios
         en un string de caracteres hexadecimales."""
        output = ""
        # Accedemos directamente a self.height y self.width de la clase padre
        for y in range(self.height):
            for x in range(self.width):
                # Accedemos directamente a self.grid de la clase padre
                cell = self.grid[y][x]

                # Calculamos el valor decimal sumando
                # el peso de cada pared cerrada
                val = 0
                if cell["north"]:
                    val += 1  # Bit 0
                if cell["east"]:
                    val += 2  # Bit 1
                if cell["south"]:
                    val += 4  # Bit 2
                if cell["west"]:
                    val += 8  # Bit 3

                output += f"{val:X}"
            output += "\n"
        return output

    def save_maze(self, filename: str) -> None:
        """Guarda la estructura del laberinto en un
         archivo de texto en formato hexadecimal."""
        # Validacion de seguridad heredando el uso seguro con hasattr
        if not hasattr(self, 'grid') or not self.grid or len(self.grid) == 0:
            raise RuntimeError("No se puede guardar: La "
                               "cuadrícula no está inicializada.")

        if not self.is_in_bounds(self.entry_pos[0], self.entry_pos[1]):
            raise ValueError(f"La coordenada 'entry_pos' "
                             f"{self.entry_pos} está fuera de los límites.")
        
        if not self.is_in_bounds(self.exit_pos[0], self.exit_pos[1]):
            raise ValueError(f"La coordenada 'exit_pos' "
                             f"{self.exit_pos} está fuera de los límites.")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_maze_str())
            f.write(f"\n{self.entry_pos[0]},{self.entry_pos[1]}")
            f.write(f"\n{self.exit_pos[0]},{self.exit_pos[1]}\n")
            try:
                f.write(f"{self.path_to_directions(self.shortest_path())}")
            except Exception as error:
                print(f"[ERROR] An error ocurred: {error}")
                return

        print(f"[+] Laberinto guardado desde clase heredada en: {filename}")

def draw_dfs_again(generador: MazeGenerator, maze_color: str,
    blocked: set[tuple[int, int]]) -> None:
    for event, data in generador.shortest_path_steps():
        os.system(
            "clear"
            if os.name == "posix"
            else "cls"
        )

        if event == "search":
            if not isinstance(data, set):
                raise RuntimeError(
                    "invalid BFS search event"
                )

            generador.draw_solid(
                maze_color=maze_color,
                blocked=blocked,
                visited=data,
            )

            print(
                f"\nBFS visited cells: {len(data)}"
            )

            time.sleep(0.04)

        elif event == "solution":
            if not isinstance(data, list):
                raise RuntimeError(
                    "invalid BFS solution event"
                )

            generador.draw_solid(
                maze_color=maze_color,
                blocked=blocked,
                path=data,
            )

def Opciones(generador: interfaz, obstaculos: set[tuple[int, int]]) -> None:
    COLORS: list[str] = [
            colors.WHITE, colors.RED, colors.GREEN,
            colors.YELLOW, colors.BLUE, colors.MAGENTA,
            colors.CYAN, colors.BROWN, colors.BLACK
        ]
    maze_color: str = colors.CYAN
    color_index: int = 7
    path_show: bool = False

    while True:
        print(f"{colors.WHITE}\n=====  A-MAZE-ING  =====")
        print("1) Regenerate a New Maze")
        print("2) Change Maze Colors")
        print("3) Save Hex Maze to a File")
        print(f"4) {'Hide' if path_show else 'Show'} Path")
        print(f"5) {'Disable' if generador.animation else 'Enable'} Animation")
        print("----------")
        print("0) Quit\n")
        
        try:
            pt: str = "Chose from 0-5: "
            raw: str = input(pt).strip()
            choice: int = int(raw)

        except ValueError:
            print("\n[!] Invalid choice, please choose from 0-9")
            continue
        
        if not 0 <= choice <= 5:
            generador.draw_solid(
                maze_color=maze_color,
                blocked=obstaculos,
            )
            print("\n[!] Invalid choice, please choose from 0-9")
            continue

        if choice == 0:
            print("Quitting...")
            break

        elif choice == 1:
            for _ in generador._generate_dfs(
                blocked=obstaculos,
                seed=None,
            ):
                if generador.animation == True:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    generador.draw_solid(maze_color=maze_color, blocked=obstaculos)
                    time.sleep(0.04)
                else:
                    pass
            os.system('clear' if os.name == 'posix' else 'cls')
            if path_show == True:
                draw_dfs_again(generador, maze_color, obstaculos)
            elif path_show == False:
                generador.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos, 
                )

        elif choice == 2:
            os.system('clear' if os.name == 'posix' else 'cls')
            color_index: int = (color_index + 1) % len(COLORS)
            maze_color: str = COLORS[color_index]
            for _ in generador._generate_dfs(
                blocked=obstaculos,
                seed=generador.seed_utilizada,
            ):
                if generador.animation == True:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    generador.draw_solid(maze_color=maze_color, blocked=obstaculos)
                    time.sleep(0.04)
                else:
                    pass
            os.system('clear' if os.name == 'posix' else 'cls')
            if path_show == True:
                draw_dfs_again(generador, maze_color, obstaculos)
            elif path_show == False:
                generador.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos, 
                )
        elif choice == 3:
            generador.save_maze(
                "mi_laberinto.txt"
            )
        
        elif choice == 4:
            path_show = not path_show
            if path_show == True:
                draw_dfs_again(generador, maze_color, obstaculos)
            elif path_show == False:
                os.system('clear' if os.name == 'posix' else 'cls')
                generador.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos, 
                )

        elif choice == 5:
            print(f"\nAnimation {'Disabled' if generador.animation else 'Enabled'}!")
            generador.change_animation()
            for _ in generador._generate_dfs(
                blocked=obstaculos,
                seed=generador.seed_utilizada,
            ):
                if generador.animation == True:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    generador.draw_solid(maze_color=maze_color, blocked=obstaculos)
                    time.sleep(0.04)
                else:
                    pass
            os.system('clear' if os.name == 'posix' else 'cls')
            if path_show == True:
                draw_dfs_again(generador, maze_color, obstaculos)
            elif path_show == False:
                os.system('clear' if os.name == 'posix' else 'cls')
                generador.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos, 
                )
