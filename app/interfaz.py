from mazegen.maze import MazeGenerator
from app import colors

import time
import os


class interfaz(MazeGenerator):
    def __init__(self, width: int, height: int, entry_pos: tuple[int, int], exit_pos: tuple[int, int]) -> None:
        super().__init__(width, height, entry_pos, exit_pos)
        self.animation: bool = False

    def draw_solid(self, maze_color: str = "\033[37m",
                   blocked: set[tuple[int, int]] | None = None) -> None:
        """Dibuja el laberinto usando bloques
        sólidos
        maze_color: Código ANSI para el color (por defecto blanco).
        blocked: Conjunto de celdas que actúan como obstáculos sólidos.
        """
        if not hasattr(self, 'grid') or not self.grid or len(self.grid) == 0:
            raise RuntimeError("No se puede dibujar: La"
                               " cuadrícula del laberinto no está"
                               " inicializada o está vacía.")

        if blocked is None:
            blocked = set()

        if not self.is_in_bounds(self.entry_pos[0], self.entry_pos[1]):
            raise ValueError(f"La coordenada de inicio 'start_pos'"
                             f" {start_pos} está fuera de los "
                             f"límites del laberinto.")

        for pos in blocked:
            if not self.is_in_bounds(pos[0], pos[1]):
                raise ValueError(f"La celda bloqueada {pos} "
                                 f"está fuera de los límites del laberinto.")

        w = "█"  # Caracter de pared solida

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

                # --- LINEA 1: Pared Norte ---
                if cell["north"]:
                    line1 += f"{w}{w}{w}{w}{w}"
                else:
                    # Si no hay pared norte, dejamos el pasillo abierto,
                    # pero mantenemos las esquinas solidas
                    line1 += f"{w}   {w}"

                # --- LINEA 2: Paredes Oeste, Centro y Este ---
                left = f"{w}" if cell["west"] else " "
                right = f"{w}" if cell["east"] else " "

                # COMPROBACION DE LA ENTRADA
                if (x, y) == self.entry_pos:
                    # Colocamos la 'S'
                    cell_representation = " S "
                elif (x, y) == self.exit_pos:
                    # Colocamos la 'E'
                    cell_representation = " E "
                else:
                    # Representacion del centro de la celda ordinaria (vacío)
                    cell_representation = "   "

                line2 += f"{left}{cell_representation}{right}"

            # Imprimimos las dos lineas procesadas para esta fila
            print(f"{maze_color}{line1}")
            print(f"{maze_color}{line2}")

        # Anadimos la linea de cierre inferior
        print(f"{maze_color}{w}{w}{w}{w}{w}" * self.width)
    
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

        print(f"[+] Laberinto guardado desde clase heredada en: {filename}")

def Opciones(generador: interfaz, obstaculos: set[tuple[int, int]]) -> None:
    COLORS: List[str] = [
            colors.WHITE, colors.RED, colors.GREEN,
            colors.YELLOW, colors.BLUE, colors.MAGENTA,
            colors.CYAN, colors.BROWN, colors.BLACK
        ]
    maze_color = colors.CYAN
    color_index = 7

    while True:
        print(f"{colors.WHITE}\n=====  A-MAZE-ING  =====")
        print("1) Regenerate a New Maze")
        print("2) Change Maze Colors")
        print("3) Save Hex Maze to a File")
        print(f"4) {'Disable' if generador.animation else 'Enable'} Animation")
        print("----------")
        print("0) Quit\n")
        
        try:
            pt: str = "Chose from 0-4: "
            raw: str = input(pt).strip()
            choice: int = int(raw)

        except ValueError:
            generador.render_frame(maze_color=maze_color)
            print("\n[!] Invalid choice, please choose from 0-9")
            continue
        
        if not 0 <= choice <= 4:
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
            generador.draw_solid(
                maze_color=maze_color,
                blocked=obstaculos,
            )

        elif choice == 2:
            color_index: int = (color_index + 1) % len(COLORS)
            maze_color: str = COLORS[color_index]
            generador.draw_solid(
                maze_color=maze_color,
                blocked=obstaculos,
            )
        elif choice == 3:
            generador.save_maze(
                "mi_laberinto.txt"
            )

        elif choice == 4:
            print(f"\nAnimation {'Disabled' if generador.animation else 'Enabled'}!")
            generador.change_animation()
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
            generador.draw_solid(
                maze_color=maze_color,
                blocked=obstaculos,
            )


            

def main() -> None:
    ANCHO = 10
    ALTO = 10

    entry_pos = (0, 0)
    exit_pos = (9, 9)
    obstaculos: set[tuple[int, int]] = set()

    generador = interfaz(
        width=ANCHO,
        height=ALTO,
        entry_pos=entry_pos,
        exit_pos=exit_pos,
    )

    for _ in generador._generate_dfs(
        blocked=obstaculos,
        seed=None,
    ):
        pass

    generador.draw_solid(
        maze_color=colors.CYAN,
        blocked=obstaculos,
    )

    Opciones(generador, obstaculos)


if __name__ == "__main__":
    try:
        main()

    except TypeError as error:
        print(f"[ERROR] Invalid type: {error}")

    except ValueError as error:
        print(f"[ERROR] Invalid value: {error}")

    except RuntimeError as error:
        print(f"[ERROR] Runtime error: {error}")

    except OSError as error:
        print(f"[ERROR] System or file error: {error}")

    except KeyboardInterrupt:
        print("\n[INFO] Program interrupted by user.")

    except EOFError:
        print("\n[INFO] Input stream closed.")