import sys
from typing import Optional, Any, Union, cast
from configparser import ConfigParser, ParsingError
from pathlib import Path
from pydantic import (
    BaseModel,
    Field,
    FilePath,
    AfterValidator,
    model_validator,
    BeforeValidator,
    ConfigDict,
    ValidationError,
    NewPath,
)

from typing_extensions import Annotated


def parse_coordinate_string(
    v: Union[str, tuple[int, int]]
) -> tuple[int, int]:
    """Function for converting a chain 'x,y'
    into a tuple (x, y) before validating"""
    if isinstance(v, str):
        try:
            parts = v.strip().split(",")
            if len(parts) != 2:
                raise ValueError(
                    "Must have the exact format "
                    "'int,int' (ej: 1,2)"
                )
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            raise ValueError(
                "Must have the exact format "
                "'int,int' (eg: 1,2)"
            )
    return v


CoordinateTuple = (
    Annotated[
        tuple[int, int],
        BeforeValidator(parse_coordinate_string),
    ]
)


def validate_txt_extension(v: Path) -> Path:
    """Make sure the file has a .txt extension"""
    if v.suffix.lower() != '.txt':
        raise ValueError(
            "The output file must have a .txt extension"
        )
    return v


TxtFilePath = Annotated[
    FilePath,
    AfterValidator(validate_txt_extension),
]


class MazeConfig(BaseModel):
    """Class to stare and validate every variable"""

    model_config = ConfigDict(extra='allow')

    width: int = Field(..., ge=1, le=45)
    height: int = Field(..., ge=1, le=45)
    entry: CoordinateTuple
    exit: CoordinateTuple
    output_file: Union[FilePath, NewPath] = Field(
        ...,
        discriminator=None,
    )
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "DFS"

    @model_validator(mode="after")
    def validate_maze_rules(self) -> "MazeConfig":
        """Validating every variable from the config file"""
        validate_txt_extension(
            self.output_file
        )

        self.algorithm = (
            self.algorithm.upper()
        )

        if self.algorithm not in (
            "DFS",
            "PRIM",
        ):
            raise ValueError(
                "ALGORITHM must be either DFS or PRIM"
            )

        if self.entry == self.exit:
            raise ValueError(
                "Entry & exit must not be the same point"
            )

        if (
            self.entry[0] >= self.width
            or self.entry[1] >= self.height
        ):
            raise ValueError(
                "Entry coordinates out of range"
            )

        if (
            self.exit[0] >= self.width
            or self.exit[1] >= self.height
        ):
            raise ValueError(
                "Exit coordinates out of range"
            )

        if (
            self.entry[0] < 0
            or self.entry[1] < 0
        ):
            raise ValueError(
                "Entry coordinates cannot be negative"
            )

        if (
            self.exit[0] < 0
            or self.exit[1] < 0
        ):
            raise ValueError(
                "Exit coordinates cannot be negative"
            )

        return self


class Parsing:
    """Parsing class using Pydantic"""

    def __init__(
        self,
        config_file: str,
    ) -> None:
        self.config_file = config_file

        self.WIDTH: int = 0
        self.HEIGHT: int = 0
        self.ENTRY: tuple[int, int] = (0, 0)
        self.EXIT: tuple[int, int] = (0, 0)
        self.OUTPUT_FILE: str = ""
        self.PERFECT: Optional[bool] = None
        self.SEED: Optional[int] = None
        self.ALGORITHM: str = "DFS"

    def set_config(self) -> None:
        """Create a MazeConfig object,
        get the variabls and manage errors"""
        try:
            # Leer el archivo con un bloque 'with' seguro
            config = ConfigParser(delimiters=('=',))

            with open(
                self.config_file,
                'r',
            ) as f:
                config_string = (
                    '[root]\n'
                    + f.read()
                )

                config.read_string(
                    config_string
                )

            root_data = dict(
                config['root']
            )

            validated_data = MazeConfig(
                **cast(
                    dict[str, Any],
                    root_data,
                )
            )

            if validated_data.model_extra:
                extra_keys = ", ".join(
                    validated_data.model_extra.keys()
                )

                print(
                    f"WARNING: The variables "
                    f"'{extra_keys}' found in "
                    f"the {self.config_file} file "
                    f"are not being used"
                )

            self.WIDTH = (
                validated_data.width
            )

            self.HEIGHT = (
                validated_data.height
            )

            self.ENTRY = (
                validated_data.entry
            )

            self.EXIT = (
                validated_data.exit
            )

            self.OUTPUT_FILE = str(
                validated_data.output_file
            )

            self.PERFECT = (
                validated_data.perfect
            )

            self.SEED = (
                validated_data.seed
            )

            self.ALGORITHM = (
                validated_data.algorithm
            )

        except FileNotFoundError:
            print(
                f"There no "
                f"{self.config_file} file"
            )

            sys.exit(1)

        except PermissionError:
            print(
                "You have no permission "
                "to read/write files"
            )

            sys.exit(1)

        except ValidationError as e:
            print(
                "Error in parsing:"
            )

            for error in e.errors():
                if not error['loc']:
                    print(
                        f"  [!] Global rule: "
                        f"{error['msg']}"
                    )

                else:
                    field = " -> ".join(
                        str(x)
                        for x in error['loc']
                    )

                    print(
                        f"  [!] {field}: "
                        f"{error['msg']}"
                    )

            sys.exit(1)

        except ParsingError as e:
            print("Error in configuration file format:")
            print(
                "  [!] Make sure to only use the "
                "'=' sign to assign values."
            )
            print(f"  Details: {e}")
            sys.exit(1)

        except Exception as e:
            print(
                f"Unexpected error in parsing:\n"
                f"{e}"
            )

            sys.exit(1)
