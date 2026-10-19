from mazegen.maze import MazeGenerator
from app import colors

import time
import os
import sys


class interfaz(MazeGenerator):
    def __init__(self, width: int, height: int, entry_pos:
                 tuple[int, int], exit_pos: tuple[int, int]) -> None:
        super().__init__(width, height, entry_pos, exit_pos)
        self.animation: bool = False

    def draw_solid(
        self,
        maze_color: str = "\033[37m",
        blocked: set[tuple[int, int]] | None = None,
        path: list[tuple[int, int]] | None = None,
        visited: set[tuple[int, int]] | None = None
    ) -> None:
        """Draw the maze using solid blocks."""
        if not hasattr(self, 'grid') or not self.grid or len(self.grid) == 0:
            raise RuntimeError(
                "Unable to draw: The maze's grid "
                "is not initialized or is empty."
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
                f"The entry coordinate 'entry_pos' "
                f"{self.entry_pos} is outside the limits of the maze."
            )

        for pos in blocked:
            if not self.is_in_bounds(pos[0], pos[1]):
                raise ValueError(
                    f"The blocked cell {pos} "
                    f"is outside the limits of the maze."
                )

        w = "█"
        path_set = set(path)

        for y in range(self.height):
            line1 = ""
            line2 = ""

            for x in range(self.width):
                current = (x, y)

                if current in blocked:
                    blocked_up = (x, y - 1) in blocked
                    blocked_left = (x - 1, y) in blocked
                    blocked_right = (x + 1, y) in blocked

                    if blocked_up:
                        line1 += (
                            f"{maze_color}{w}"
                            f"{colors.GRAY}{w}{w}{w}"
                            f"{maze_color}{w}"
                        )
                    else:
                        line1 += (
                            f"{maze_color}{w}{w}{w}{w}{w}"
                        )

                    line2 += (
                        f"{colors.GRAY if blocked_left else maze_color}{w}"
                        f"{colors.GRAY}{w}{w}{w}"
                        f"{colors.GRAY if blocked_right else maze_color}{w}"
                    )

                    continue

                cell = self.grid[y][x]

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
        """Translates the grid of dictionaries
         in a string made of hexadecimal numbers."""
        output = ""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

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
        """Saves the structure of the maze into
         a .txt file in a hexadecimal format."""
        if not hasattr(self, 'grid') or not self.grid or len(self.grid) == 0:
            raise RuntimeError("Unable to save: The "
                               "grid is not initialized.")

        if not self.is_in_bounds(self.entry_pos[0], self.entry_pos[1]):
            raise ValueError(f"The entry coordinate 'entry_pos' "
                             f"{self.entry_pos} is outside the"
                             f" limits of the maze.")

        if not self.is_in_bounds(self.exit_pos[0], self.exit_pos[1]):
            raise ValueError(f"The entry coordinate 'exit_pos' "
                             f"{self.exit_pos} is outside the"
                             f" limits of the maze.")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_maze_str())
            f.write(f"\n{self.entry_pos[0]},{self.entry_pos[1]}")
            f.write(f"\n{self.exit_pos[0]},{self.exit_pos[1]}\n")
            try:
                f.write(f"{self.path_to_directions(self.shortest_path())}\n")
            except Exception as error:
                print(f"[ERROR] An error ocurred: {error}")
                return

        print(f"[+] Maze has been saved into: {filename}")


def draw_dfs_again(generator: interfaz, maze_color: str,
                   blocked: set[tuple[int, int]]) -> None:
    """A complementaary function that helps
    draw the mazes solution into the terminal"""
    for event, data in generator.shortest_path_steps():
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

            generator.draw_solid(
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

            generator.draw_solid(
                maze_color=maze_color,
                blocked=blocked,
                path=data,
            )


def flush_input() -> None:
    """Makes the program not take user
    input during animations"""
    if sys.platform == "win32":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        from termios import tcflush, TCIFLUSH
        tcflush(sys.stdin, TCIFLUSH)


def Opciones(
    generator: interfaz,
    obstaculos: set[tuple[int, int]],
    file_name: str,
    perfect: bool,
    algorithm: str,
) -> None:
    """Displays options menu into the termial
    and lets user pick an option"""
    COLORS: list[str] = [
        colors.WHITE, colors.RED, colors.GREEN,
        colors.BLUE, colors.MAGENTA,
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
        print(
            f"5) "
            f"{'Disable' if generator.animation else 'Enable'} "
            f"Animation"
        )
        print("----------")
        print("0) Quit\n")

        try:
            pt: str = "Chose from 0-5: "
            flush_input()
            raw: str = input(pt).strip()
            choice: int = int(raw)

        except ValueError:
            print(
                "\n[!] Invalid choice, "
                "please choose from 0-5"
            )
            continue

        if not 0 <= choice <= 5:
            generator.draw_solid(
                maze_color=maze_color,
                blocked=obstaculos,
            )

            print(
                "\n[!] Invalid choice, "
                "please choose from 0-5"
            )
            continue

        if choice == 0:
            print("Quitting...")
            break

        elif choice == 1:
            if algorithm == "DFS":
                maze_generation = generator._generate_dfs(
                    blocked=obstaculos,
                    seed=None,
                )

            elif algorithm == "PRIM":
                maze_generation = generator._generate_prim(
                    blocked=obstaculos,
                    seed=None,
                )

            else:
                raise ValueError(
                    "Algorithm must be DFS or PRIM"
                )

            for _ in maze_generation:
                if generator.animation is True:
                    os.system(
                        'clear'
                        if os.name == 'posix'
                        else 'cls'
                    )

                    generator.draw_solid(
                        maze_color=maze_color,
                        blocked=obstaculos,
                    )

                    time.sleep(0.04)

                else:
                    pass

            if not perfect:
                generator.braid(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                    max_dead_ends=0,
                    min_loops=2,
                )

            os.system(
                'clear'
                if os.name == 'posix'
                else 'cls'
            )

            if path_show is True:
                draw_dfs_again(
                    generator,
                    maze_color,
                    obstaculos,
                )

            elif path_show is False:
                generator.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos,
                )

        elif choice == 2:
            os.system(
                'clear'
                if os.name == 'posix'
                else 'cls'
            )

            color_index = (
                color_index + 1
            ) % len(COLORS)

            maze_color = COLORS[
                color_index
            ]

            if algorithm == "DFS":
                maze_generation = generator._generate_dfs(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                )

            elif algorithm == "PRIM":
                maze_generation = generator._generate_prim(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                )

            else:
                raise ValueError(
                    "Algorithm must be DFS or PRIM"
                )

            for _ in maze_generation:
                if generator.animation is True:
                    os.system(
                        'clear'
                        if os.name == 'posix'
                        else 'cls'
                    )

                    generator.draw_solid(
                        maze_color=maze_color,
                        blocked=obstaculos,
                    )

                    time.sleep(0.04)

                else:
                    pass

            if not perfect:
                generator.braid(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                    max_dead_ends=0,
                    min_loops=2,
                )

            os.system(
                'clear'
                if os.name == 'posix'
                else 'cls'
            )

            if path_show is True:
                draw_dfs_again(
                    generator,
                    maze_color,
                    obstaculos,
                )

            elif path_show is False:
                generator.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos,
                )

        elif choice == 3:
            generator.save_maze(
                file_name
            )

        elif choice == 4:
            path_show = not path_show

            if path_show is True:
                draw_dfs_again(
                    generator,
                    maze_color,
                    obstaculos,
                )

            elif path_show is False:
                os.system(
                    'clear'
                    if os.name == 'posix'
                    else 'cls'
                )

                generator.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos,
                )

        elif choice == 5:
            print(
                f"\nAnimation "
                f"{'Disabled' if generator.animation else 'Enabled'}!"
            )

            generator.change_animation()

            if algorithm == "DFS":
                maze_generation = generator._generate_dfs(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                )

            elif algorithm == "PRIM":
                maze_generation = generator._generate_prim(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                )

            else:
                raise ValueError(
                    "Algorithm must be DFS or PRIM"
                )

            for _ in maze_generation:
                if generator.animation is True:
                    os.system(
                        'clear'
                        if os.name == 'posix'
                        else 'cls'
                    )

                    generator.draw_solid(
                        maze_color=maze_color,
                        blocked=obstaculos,
                    )

                    time.sleep(0.04)

                else:
                    pass

            if not perfect:
                generator.braid(
                    blocked=obstaculos,
                    seed=generator.seed_utilizada,
                    max_dead_ends=0,
                    min_loops=2,
                )

            os.system(
                'clear'
                if os.name == 'posix'
                else 'cls'
            )

            if path_show is True:
                draw_dfs_again(
                    generator,
                    maze_color,
                    obstaculos,
                )

            elif path_show is False:
                os.system(
                    'clear'
                    if os.name == 'posix'
                    else 'cls'
                )

                generator.draw_solid(
                    maze_color=maze_color,
                    blocked=obstaculos,
                )
