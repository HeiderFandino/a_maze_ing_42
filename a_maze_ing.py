from app import colors
from app.interfaz import Opciones, interfaz


def main() -> None:
    """Create, generate and display the maze application."""
    width: int = 15
    height: int = 15

    entry_pos: tuple[int, int] = (0, 0)
    exit_pos: tuple[int, int] = (14, 14)

    generador = interfaz(
        width=width,
        height=height,
        entry_pos=entry_pos,
        exit_pos=exit_pos,
    )

    blocked = generador._get_42_pattern()

    for _ in generador._generate_dfs(
        blocked=blocked,
        seed=42,
    ):
        pass

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