import sys
from typing import Optional
from configparser import ConfigParser
from pydantic import BaseModel, Field, NewPath, model_validator, BeforeValidator
from typing_extensions import Annotated


def parse_coordinate_string(v: any) -> tuple[int, int]:
    """Función para convertir una cadena 'x,y' en una tupla (x, y) antes de validar"""
    if isinstance(v, str):
        try:
            parts = v.strip().split(",")
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            raise ValueError("Debe tener el formato 'entero,entero' (ej: 1,2)")
    return v

# Definimos un tipo personalizado que aplica la conversión automáticamente
CoordinateTuple = Annotated[tuple[int, int], BeforeValidator(parse_coordinate_string)]


# 1. Definimos el modelo principal de configuración con sus reglas
class MazeConfig(BaseModel):
    width: int = Field(..., ge=1, le=45)
    height: int = Field(..., ge=1, le=45)
    entry: CoordinateTuple
    exit: CoordinateTuple
    output_file: NewPath  # Valida que sea una ruta válida donde se pueda escribir
    perfect: bool
    seed: Optional[int] = None

    @model_validator(mode="after")
    def validate_maze_rules(self) -> "MazeConfig":
        # Regla: La entrada y la salida no pueden ser iguales
        if self.entry == self.exit:
            raise ValueError("Entry & exit must not be the same point")
        
        # Regla: Coordenadas dentro de los límites del laberinto
        # self.entry[0] es 'x', self.entry[1] es 'y'
        if self.entry[0] >= self.width or self.entry[1] >= self.height:
            raise ValueError("Entry coordinates out of range")
            
        if self.exit[0] >= self.width or self.exit[1] >= self.height:
            raise ValueError("Exit coordinates out of range")
            
        # Regla complementaria: Las coordenadas no deben ser negativas
        if self.entry[0] < 0 or self.entry[1] < 0:
            raise ValueError("Entry coordinates cannot be negative")
        if self.exit[0] < 0 or self.exit[1] < 0:
            raise ValueError("Exit coordinates cannot be negative")
            
        return self


# 2. La clase de Parsing simplificada
class Parsing:
    """Parsing class utilizando Pydantic"""
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        # Inicializamos los atributos actualizados a Tuple
        self.WIDTH: int = 0
        self.HEIGHT: int = 0
        self.ENTRY: tuple[int, int] = (0, 0)
        self.EXIT: tuple[int, int] = (0, 0)
        self.OUTPUT_FILE: str = ""
        self.PERFECT: Optional[bool] = None
        self.SEED: Optional[int] = None

    def set_config(self) -> None:
        try:
            # Leer el archivo con un bloque 'with' seguro
            config = ConfigParser()
            with open(self.config_file, 'r') as f:
                config_string = '[root]\n' + f.read()
                config.read_string(config_string)
            
            root_data = dict(config['root'])
            
            # Pydantic llamará automáticamente a 'parse_coordinate_string' gracias al BeforeValidator
            validated_data = MazeConfig(**root_data)

            # Mapear los datos validados a los atributos de la clase
            self.WIDTH = validated_data.width
            self.HEIGHT = validated_data.height
            self.ENTRY = validated_data.entry  # Ahora guarda una tupla (x, y)
            self.EXIT = validated_data.exit    # Ahora guarda una tupla (x, y)
            self.OUTPUT_FILE = str(validated_data.output_file)
            self.PERFECT = validated_data.perfect
            self.SEED = validated_data.seed

        except FileNotFoundError:
            print(f"There no {self.config_file} file")
            sys.exit(1)
        except PermissionError:
            print("You have no permission to read/write files")
            sys.exit(1)
        except Exception as e:
            print(f"Error in parsing:\n{e}")
            sys.exit(1)
