from app import colors
from app.interfaz import Opciones, interfaz

import os
import time


def main() -> None:
    """Create, generate and display the maze application."""
    width: int = 10
    height: int = 10

    entry_pos: tuple[int, int] = (0, 0)
    exit_pos: tuple[int, int] = (9, 9)

    blocked: set[tuple[int, int]] = set()

    generador = interfaz(
        width=width,
        height=height,
        entry_pos=entry_pos,
        exit_pos=exit_pos,
    )

    # Generamos primero el laberinto.
    for _ in generador._generate_dfs(
        blocked=blocked,
        seed=42,
    ):
        pass

    # Animación del BFS.
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
                maze_color=colors.CYAN,
                blocked=blocked,
                visited=data,
            )

            print(
                f"\nBFS visited cells: {len(data)}"
            )

            time.sleep(0.10)

        elif event == "solution":
            if not isinstance(data, list):
                raise RuntimeError(
                    "invalid BFS solution event"
                )

            generador.draw_solid(
                maze_color=colors.CYAN,
                blocked=blocked,
                path=data,
            )

            directions = (
                generador.path_to_directions(data)
            )

            print("\n=== BFS SOLUTION ===")
            print(
                f"Cells in path: {len(data)}"
            )
            print(
                f"Movements: {len(directions)}"
            )
            print(
                f"Directions: {directions}"
            )
            print("====================")

            time.sleep(2)

        else:
            raise RuntimeError(
                f"unknown BFS event: {event}"
            )

    # Entramos al menú normal después de terminar la animación.
    generador.draw_solid(
        maze_color=colors.CYAN,
        blocked=blocked,
    )

    Opciones(
        generador,
        blocked,
    )


if __name__ == "__main__":
    try:
        main()

    except TypeError as error:
        print(
            f"[ERROR] Invalid type: {error}"
        )

    except ValueError as error:
        print(
            f"[ERROR] Invalid value: {error}"
        )

    except RuntimeError as error:
        print(
            f"[ERROR] Runtime error: {error}"
        )

    except OSError as error:
        print(
            f"[ERROR] System or file error: {error}"
        )

    except KeyboardInterrupt:
        print(
            "\n[INFO] Program interrupted by user."
        )

    except EOFError:
        print(
            "\n[INFO] Input stream closed."
        )