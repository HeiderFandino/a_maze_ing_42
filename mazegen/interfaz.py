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
                if (x, y) == start_pos:
                    # Colocamos la 'S'
                    cell_representation = " S "
                else:
                    # Representacion del centro de la celda ordinaria (vacío)
                    cell_representation = "   "

                line2 += f"{left}{cell_representation}{right}"

            # Imprimimos las dos lineas procesadas para esta fila
            print(f"{maze_color}{line1}")
            print(f"{maze_color}{line2}")

        # Anadimos la linea de cierre inferior
        print(f"{maze_color}{w}{w}{w}{w}{w}" * self.width)

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

    def save_maze(self, filename: str, start_pos:
                  tuple[int, int] = (0, 0)) -> None:
        """Guarda la estructura del laberinto en un
         archivo de texto en formato hexadecimal."""
        # Validacion de seguridad heredando el uso seguro con hasattr
        if not hasattr(self, 'grid') or not self.grid or len(self.grid) == 0:
            raise RuntimeError("No se puede guardar: La "
                               "cuadrícula no está inicializada.")

        if not self.is_in_bounds(start_pos[0], start_pos[1]):
            raise ValueError(f"La coordenada 'start_pos' "
                             f"{start_pos} está fuera de los límites.")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_maze_str())
            f.write(f"\n{start_pos[0]},{start_pos[1]}\n")

        print(f"[+] Laberinto guardado desde clase heredada en: {filename}")


if __name__ == "__main__":
    # Configuracion del tamano del laberinto
    ANCHO = 10
    ALTO = 10

    # Creamos la instancia del generador
    generador = interfaz(width=ANCHO, height=ALTO)

    # Definimos celdas bloqueadas (obstáculos)
    obstaculos = {(1, 1)}

    # Coordenada de inicio para empezar a generar
    punto_inicio = (3, 7)

    # Codigos ANSI de color
    COLOR_CYAN = "\033[96m"
    COLOR_RESET = "\033[0m"

    print("Generando el laberinto en segundo plano...")

    # Consumimos todo el generador por completo para que calcule el laberinto
    # sin imprimir nada en pantalla todavia.
    for _ in generador._generate_dfs(entry_pos=punto_inicio,
                                     blocked=obstaculos, seed=None):
        pass  # No hacemos nada en cada paso, solo dejamos que termine

    # Un unico dibujo al final del proceso
    generador.draw_solid(maze_color=COLOR_CYAN, blocked=obstaculos,
                         start_pos=punto_inicio)

    print(f"\n{COLOR_RESET}[+] ¡Laberinto generado y dibujado con éxito!")
    #SOLO SI QUIERES UN ARCHIVO HEXADECIMAL!!
    #generador.save_maze("mi_laberinto.txt", start_pos=punto_inicio)
