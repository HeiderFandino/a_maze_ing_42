# Actualizaciones

## 06/10/2026 — 16:14

### H01: estructura del motor y apertura de pasos

#### Cambios realizados

- Creada la clase `MazeGenerator(width, height)` con una cuadrícula de celdas independientes y todas las paredes inicialmente cerradas.
- Añadida la validación de dimensiones positivas.
- Implementado `is_in_bounds(x, y)` para comprobar si unas coordenadas están dentro del tablero.
- Implementado `open_passage(x1, y1, x2, y2)` para abrir pasos entre celdas vecinas, actualizando las dos paredes compartidas.

#### Información para la interfaz

- Las coordenadas son `(x, y)`: columna y fila.
- Se accede a las celdas mediante `maze.grid[y][x]`.
- Cada celda contiene `"north"`, `"east"`, `"south"` y `"west"`.
- `True` significa pared cerrada; `False`, paso abierto.
- Las dimensiones no positivas, las coordenadas fuera del tablero y los pasos entre celdas no adyacentes provocan `ValueError`, que debe manejar la aplicación.

#### Comprobaciones realizadas

- Apertura de pasos en las cuatro direcciones.
- Independencia de las celdas.
- Coherencia de las paredes compartidas.
- Rechazo de dimensiones no positivas y pasos inválidos.
