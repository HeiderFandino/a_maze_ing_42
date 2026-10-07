from maze import MazeGenerator


class interfaz(MazeGenerator):
    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)

    def draw_solid(self, maze_color: str = "\033[37m",
                   blocked: set[tuple[int, int]] | None = None,
                   start_pos: tuple[int, int] = (0, 0)) -> None:
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

        if not self.is_in_bounds(start_pos[0], start_pos[1]):
            raise ValueError(f"La coordenada de inicio 'start_pos'"
                             f" {start_pos} está fuera de los "
                             f"límites del laberinto.")

        for pos in blocked:
            if not self.is_in_bounds(pos[0], pos[1]):
                raise ValueError(f"La celda bloqueada {pos} "
                                 f"está fuera de los límites del laberinto.")

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

                # COMPROBACIÓN DE LA ENTRADA
                if (x, y) == start_pos:
                    # Colocamos la 'S' y
                    # volvemos a aplicar el color del laberinto
                    cell_representation = " S "
                else:
                    # Representación del centro de la celda ordinaria (vacío)
                    cell_representation = "   "

                line2 += f"{left}{cell_representation}{right}"

            # Imprimimos las dos líneas procesadas para esta fila
            print(f"{maze_color}{line1}")
            print(f"{maze_color}{line2}")

        # Al igual que el segundo código, añadimos la línea de cierre inferior
        print(f"{maze_color}{w}{w}{w}{w}{w}" * self.width)


if __name__ == "__main__":
    # Configuración del tamaño del laberinto
    ANCHO = 10
    ALTO = 10

    # Creamos la instancia del generador
    generador = interfaz(width=ANCHO, height=ALTO)


    # Definimos celdas bloqueadas (obstáculos)
    obstaculos = {(1, 1)}

    # Coordenada de inicio para empezar a generar
    punto_inicio = (6, 7)

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
    generador.draw_solid(maze_color=COLOR_CYAN, blocked=obstaculos, start_pos=punto_inicio)

    print(f"\n{COLOR_RESET}[+] ¡Laberinto generado y dibujado con éxito!")