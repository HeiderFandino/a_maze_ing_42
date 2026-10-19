*This project has been created as part of the 42 curriculum by hfandino, mmarches.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator developed for the 42 curriculum.

The program reads a configuration file, generates a valid maze, displays it in the terminal, computes a shortest path between the entry and exit, and can export the maze using the hexadecimal wall format required by the subject.

The project was designed around a reusable maze engine. The generation logic lives in the standalone `mazegen` package and is kept separate from configuration parsing, terminal rendering, interaction, and file export.

The implementation supports:

- reproducible random generation using a seed;
- perfect mazes with exactly one route between reachable cells;
- non-perfect braided mazes with multiple routes;
- a visible `42` pattern made of fully closed cells when the maze is large enough;
- coherent North/East/South/West walls and closed external borders;
- protection against forbidden `3x3` open areas;
- shortest-path solving with BFS;
- terminal rendering with entry, exit, and optional solution path;
- interactive regeneration, colour changes, path display, saving, and animation;
- two generation algorithms: iterative DFS and randomized Prim;
- a reusable pip-installable `mazegen` package.

## Project structure

```text
.
├── a_maze_ing.py
├── app/
│   ├── __init__.py
│   ├── colors.py
│   └── interfaz.py
├── config.py
├── config.txt
├── LICENSE.md
├── Makefile
├── mazegen/
│   ├── __init__.py
│   ├── braiding.py
│   ├── generation.py
│   ├── maze.py
│   └── pathfinding.py
├── mazegen-1.0.0-py3-none-any.whl
├── pyproject.toml
└── README.md
```

The main responsibilities are separated as follows:

- `a_maze_ing.py`: application entry point and high-level coordination.
- `config.py`: parsing and validation of the configuration file.
- `app/`: terminal rendering, colours, user interaction, and file export.
- `mazegen/`: reusable maze engine, generation algorithms, braiding, and pathfinding.
- `pyproject.toml`: package build configuration.
- `mazegen-1.0.0-py3-none-any.whl`: reusable installable package.
- `LICENSE.md`: reuse and distribution license.

## Requirements

- Python 3.10 or later
- `pydantic`
- `flake8`
- `mypy`
- `build`

A virtual environment is recommended.

## Instructions

### 1. Create and activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate
```

### 2. Install project dependencies

```bash
make install
```

Equivalent command:

```bash
python3 -m pip install flake8 mypy pydantic build
```

### 3. Run the project

```bash
make run
```

or directly:

```bash
python3 a_maze_ing.py config.txt
```

The program accepts exactly one configuration-file argument. A different filename may be used:

```bash
python3 a_maze_ing.py my_config.txt
```

### 4. Debug

```bash
make debug
```

This starts the program with Python's built-in `pdb` debugger.

### 5. Lint and static type checking

```bash
make lint
```

The rule runs the mandatory checks:

```bash
python3 -m flake8 .
python3 -m mypy . \
    --warn-return-any \
    --warn-unused-ignores \
    --ignore-missing-imports \
    --disallow-untyped-defs \
    --check-untyped-defs
```

An additional stricter rule is also available:

```bash
make lint-strict
```

### 6. Clean temporary Python files

```bash
make clean
```

## Configuration file

The configuration file uses one `KEY=VALUE` pair per line. Lines beginning with `#` are treated as comments.

The mandatory keys are:

| Key | Meaning | Example |
| --- | --- | --- |
| `WIDTH` | Maze width in cells | `WIDTH=15` |
| `HEIGHT` | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinate `(x,y)` | `ENTRY=0,0` |
| `EXIT` | Exit coordinate `(x,y)` | `EXIT=14,14` |
| `OUTPUT_FILE` | Output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect or non-perfect mode | `PERFECT=TRUE` |

This implementation also supports:

| Key | Meaning | Default / values |
| --- | --- | --- |
| `SEED` | Reproducible random seed | optional integer |
| `ALGORITHM` | Generation algorithm | `DFS` or `PRIM`; default `DFS` |

The supplied default configuration is:

```text
WIDTH           = 15
HEIGHT          = 15
ENTRY           = 0,0
EXIT            = 14,14
OUTPUT_FILE     = maze.txt
PERFECT         = TRUE
SEED            = 42
ALGORITHM       = DFS
```

Configuration validation checks dimensions, coordinates, entry/exit separation, output-file extension, boolean values, the seed, and the selected generation algorithm. Unknown extra keys are accepted by the parser but reported to the user as unused.

The current implementation limits `WIDTH` and `HEIGHT` to the range `1..45` as a project design choice.

## Maze representation

Internally, the reusable generator stores the maze as:

```python
list[list[dict[str, bool]]]
```

Coordinates use `(x, y)` while storage uses `grid[y][x]`.

Each cell contains four wall states:

```python
{
    "north": True,
    "east": True,
    "south": True,
    "west": True,
}
```

`True` means that the wall is closed and `False` means that the passage is open.

Whenever a passage is opened between two adjacent cells, both sides of the shared wall are updated so wall information remains reciprocal.

## Maze generation

### Primary algorithm: iterative DFS / recursive-backtracker strategy

The primary generation algorithm is an iterative depth-first search using an explicit stack.

At a high level:

1. all cells begin with their four walls closed;
2. a starting traversable cell is selected;
3. an unvisited neighbour is selected randomly;
4. the shared wall is opened;
5. the neighbour is pushed onto the DFS stack;
6. when no unvisited neighbour remains, the algorithm backtracks;
7. generation ends when every non-blocked cell has been visited.

With `PERFECT=TRUE`, DFS constructs a spanning tree over the traversable cells. Because a tree is connected and contains no cycles, there is exactly one route between any two reachable cells.

### Why DFS was chosen

DFS was selected as the primary algorithm because it is compact, deterministic when driven by a fixed seed, naturally produces a perfect maze, works well with excluded cells such as the `42` pattern, and can expose generation events without coupling the engine to the terminal renderer.

The explicit-stack implementation also avoids relying on Python recursion depth for maze generation.

### Randomized Prim

A second generation algorithm, randomized Prim, is available through:

```text
ALGORITHM = PRIM
```

Prim grows the maze from a frontier of cells rather than following the deep backtracking behaviour of DFS. It therefore produces a visibly different maze structure while respecting the same generator contract, seed handling, wall representation, and blocked-cell rules.

Supporting two genuinely different algorithms is an advanced feature of this project.

## Perfect and non-perfect modes

### `PERFECT=TRUE`

The generated traversable maze is a tree:

- full connectivity;
- no loops;
- exactly one route between connected cells.

### `PERFECT=FALSE`

The project transforms the initial perfect maze into a braided maze.

Safe walls are opened to introduce cycles while preserving the maze invariants. The braiding phase verifies wall coherence, connectivity, forbidden open areas, required accessible positions, loop count, and dead-end count.

The implemented non-perfect mode targets a Pac-Man-like board with:

- full connectivity;
- multiple independent routes;
- accessible corners and centre;
- no forbidden `3x3` open areas;
- zero real dead ends in the validated bonus configuration.

## The `42` pattern

When dimensions allow it, a centered `42` is created from fully closed cells.

Those cells are excluded from maze traversal while the rest of the maze remains connected. Entry and exit are not allowed to overlap the pattern.

If the dimensions are too small to contain the pattern, generation continues without it and a clear warning is printed.

## Shortest path

Shortest-path solving is independent from maze generation.

The project uses Breadth-First Search (BFS) over passages that are actually open in the maze. BFS is appropriate because every movement between adjacent cells has the same cost; therefore, the first reconstructed route to the exit is a shortest route.

The resulting coordinate path can also be converted to:

```text
N E S W
```

directions for the output file.

DFS/Prim are generation algorithms. BFS is the pathfinding algorithm; they serve different purposes.

## Output file format

When the maze is saved, each cell is encoded as one hexadecimal digit.

Closed walls set the corresponding bit to `1`:

| Bit | Direction |
| --- | --- |
| `0` | North |
| `1` | East |
| `2` | South |
| `3` | West |

For example:

- `3` = binary `0011`: North and East are closed.
- `A` = binary `1010`: East and West are closed.

Cells are written row by row, one maze row per line.

After the maze there is one empty line, followed by:

```text
entry_x,entry_y
exit_x,exit_y
SHORTEST_PATH_USING_NESW
```

Every line, including the final path line, ends with `\n`.

Example structure:

```text
D539...
97C6...
...

0,0
14,14
EESEN...
```

## Terminal interface

The project uses terminal rendering.

The interface displays:

- maze walls;
- entry;
- exit;
- the closed `42` pattern;
- the shortest path when enabled.

The interactive menu provides:

```text
1) Regenerate a New Maze
2) Change Maze Colors
3) Save Hex Maze to a File
4) Show/Hide Path
5) Enable Animation
0) Quit
```

Regeneration respects the selected generation algorithm. Seed reuse or fresh random generation depends on the selected interaction.

Animation is implemented using generation/search events emitted by the engine, keeping presentation logic outside the reusable generator.

## Reusable `mazegen` package

The reusable maze logic is contained in the standalone `mazegen` package and exposes the `MazeGenerator` class:

```python
from mazegen import MazeGenerator
```

A prebuilt wheel is provided at the repository root:

```text
mazegen-1.0.0-py3-none-any.whl
```

### Install the reusable package

From another virtual environment:

```bash
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
```

Then:

```python
from mazegen import MazeGenerator
```

### Basic use

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=10,
    height=10,
    entry_pos=(0, 0),
    exit_pos=(9, 9),
)

for _ in maze._generate_dfs(
    blocked=set(),
    seed=42,
):
    pass

solution = maze.shortest_path()

print(maze.grid)
print(solution)
print(maze.path_to_directions(solution))
```

The constructor accepts custom maze size and endpoints. The generation method accepts a custom seed, making the generated structure reproducible.

The generated structure is available through:

```python
maze.grid
```

and at least one solution is available through:

```python
maze.shortest_path()
```

The internal grid representation is intentionally independent from the hexadecimal export format.

### Build the package again

All required build metadata is included in the repository.

From the project root:

```bash
python3 -m build
```

This generates a source distribution and a wheel under `dist/`.

During development, the wheel was also tested by installing it into a clean virtual environment and importing `MazeGenerator` from outside the repository directory.

## Advanced features and bonuses

The project implements the following advanced features:

- a second maze-generation algorithm: randomized Prim;
- non-perfect braided mazes;
- zero real dead ends in the validated non-perfect configuration;
- terminal animation;
- runtime wall-colour changes;
- deterministic generation through a custom seed.

The project was validated with the subject-provided maze analyzer in both perfect and non-perfect modes and with both DFS and Prim generation.

## Team and project management

### Roles

**hfandino — core maze engine, algorithms, and validation**

Main responsibilities included:

- internal grid and wall representation;
- engine-level parameter validation;
- seeded perfect-maze generation;
- `42` pattern integration;
- shortest-path solving;
- non-perfect/braided generation;
- zero-dead-end work;
- alternative generation algorithm;

**mmarches — configuration, terminal interface, and application integration**

Main responsibilities included:

- configuration parsing and validation;
- default configuration and option selection;
- terminal rendering;
- hexadecimal file export;
- interactive controls;
- end-to-end application and file testing.
- generation events used by animation.
- type checking, linting, and final technical review.

Both members reviewed each other's work and jointly agreed on the contract between the reusable engine and the application layer.

### Initial planning

The initial plan divided the project by responsibility rather than by individual files:

- Heider focused mainly on the maze engine and algorithmic invariants.
- Michele focused mainly on configuration, presentation, export, and application integration.
- Shared contracts were defined early so each side could progress independently.
- Work was organized in Trello with dependencies, expected evidence, reviewer assignment, and subject references.
- Git was used for incremental integration and cross-review.

The plan prioritized the mandatory project first, with bonuses scheduled after the basic generation, solving, rendering, and export pipeline was functional.

### How the plan evolved

As the project became integrated, the initial separation became less strict.

Configuration, generation, rendering, output, pathfinding, and animation affected one another, so development moved toward shorter integration cycles and cross-review. Requirements were repeatedly checked against the subject instead of considering a feature complete only because its isolated implementation worked.

The final phase concentrated on integration defects and evaluation-readiness: CLI argument handling, exact output newlines, reproducible packaging, `flake8`, `mypy`, Makefile behaviour, analyzer results, and repository cleanup.

### What worked well

- Defining a clear contract between engine and interface early.
- Separating generation, pathfinding, braiding, configuration, and rendering.
- Using reproducible seeds to debug failures.
- Cross-review between team members.
- Testing with the official analyzer rather than relying only on visual inspection.
- Keeping generation independent from rendering so the same engine can be packaged and reused.
- Using Trello to track dependencies and ownership instead of treating every task as independent.

### What could be improved

- Integration could have started even earlier with smaller end-to-end slices.
- Some task-status tracking in Trello lagged behind the actual implementation.
- Packaging and exact evaluation constraints could have been validated earlier rather than mainly during the final review.
- More automated regression tests could reduce the amount of manual rechecking after merges.
- Public reusable API naming could be improved further so consumers do not need generation methods whose current names are internal-style (`_generate_dfs`, `_generate_prim`).

### Tools used

- Python 3
- Git / GitHub
- Trello
- `venv`
- Pydantic
- `flake8`
- `mypy`
- Python `pdb`
- Python packaging via `pyproject.toml`, `setuptools`, `wheel`, and `build`
- the subject-provided `maze_analyzer.py`

## Error handling and validation

The application validates configuration and engine parameters before generation and provides clear error messages for invalid input.

Examples include:

- missing configuration files;
- malformed configuration syntax;
- invalid coordinate format;
- entry or exit outside the maze;
- identical entry and exit;
- unsupported generation algorithm;
- invalid output-file extension;
- invalid maze dimensions;
- insufficient dimensions for the `42` pattern;
- file-write errors.

File operations use context managers so resources are closed correctly.

## Resources

The following references were used to understand the language features, algorithms, tooling, and packaging involved in the project:

- Python documentation — https://docs.python.org/3/
- Python `random` module — https://docs.python.org/3/library/random.html
- Python `collections.deque` — https://docs.python.org/3/library/collections.html#collections.deque
- Python `pdb` debugger — https://docs.python.org/3/library/pdb.html
- Python `venv` — https://docs.python.org/3/library/venv.html
- Python Packaging User Guide — https://packaging.python.org/
- `pyproject.toml` specification / packaging documentation — https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- Pydantic documentation — https://docs.pydantic.dev/
- mypy documentation — https://mypy.readthedocs.io/
- flake8 documentation — https://flake8.pycqa.org/
- Breadth-First Search and Depth-First Search concepts — standard graph traversal algorithms.
- Randomized Prim maze generation — Prim's minimum-spanning-tree strategy adapted to randomized maze generation.
- The A-Maze-ing subject and the provided `maze_analyzer.py` were treated as the authoritative project specification and validation reference.

### Use of AI

AI tools were used as development support, not as a replacement for understanding or peer review.

They were used for:

- explaining Python, graph, maze-generation, pathfinding, typing, and packaging concepts;
- reviewing portions of code against the subject requirements;
- helping diagnose errors reported by `flake8`, `mypy`, Git, and packaging tools;
- suggesting edge cases and validation checks;
- comparing implementation behaviour with the mandatory requirements;
- assisting with packaging/build commands;
- helping organize final verification;
- assisting in drafting and reviewing project documentation, including this README.

AI-generated suggestions were reviewed, adapted, executed, and tested before being kept. Functional behaviour was additionally checked through direct execution, peer review, static analysis, clean-environment package installation, and the subject-provided analyzer.

## License

The reusable maze generator is distributed under the license described in `LICENSE.md`.

The selected license explicitly permits reuse and distribution of the generator in future projects.
