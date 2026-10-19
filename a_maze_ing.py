import sys

from app import colors
from app.interfaz import Opciones, interfaz
from config import Parsing


def main() -> None:
    """Create, generate and display the maze application."""
    if len(sys.argv) != 2:
        raise ValueError(
            "Usage: python3 a_maze_ing.py config.txt"
        )

    parser: Parsing = Parsing(sys.argv[1])
    parser.set_config()

    width: int = parser.WIDTH
    height: int = parser.HEIGHT

    entry_pos: tuple[int, int] = parser.ENTRY
    exit_pos: tuple[int, int] = parser.EXIT

    generator = interfaz(
        width=width,
        height=height,
        entry_pos=entry_pos,
        exit_pos=exit_pos,
    )

    blocked = generator._get_42_pattern()

    if parser.ALGORITHM == "DFS":
        for _ in generator._generate_dfs(
            blocked=blocked,
            seed=parser.SEED,
        ):
            pass

    elif parser.ALGORITHM == "PRIM":
        for _ in generator._generate_prim(
            blocked=blocked,
            seed=parser.SEED,
        ):
            pass

    if parser.PERFECT is False:
        generator.braid(
            blocked=blocked,
            seed=generator.seed_utilizada,
            max_dead_ends=0,
            min_loops=2,
        )

    generator.draw_solid(
        maze_color=colors.CYAN,
        blocked=blocked,
    )

    Opciones(
        generator,
        blocked,
        parser.OUTPUT_FILE,
        bool(parser.PERFECT),
        parser.ALGORITHM,
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
