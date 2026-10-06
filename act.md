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

## 06/10/2026 — 18:37

### Validaciones básicas — H02

- Se añadió `_validate_endpoints(entry_pos, exit_pos)` para comprobar que entrada y salida estén dentro de la cuadrícula y sean diferentes.
- Las coordenadas inválidas producen `ValueError` con un mensaje descriptivo.

### Avances en la generación perfecta — H03

- `_get_neighbors(x, y)` obtiene los vecinos dentro de los límites, en orden norte, este, sur y oeste.
- `_get_available_neighbors(...)` excluye las celdas visitadas y bloqueadas.
- `_generate_dfs(...)` construye el laberinto mediante DFS, utilizando una pila y un conjunto de celdas visitadas.
- La generación comienza con todas las paredes cerradas y utiliza una semilla para controlar las decisiones aleatorias.
- Cada apertura modifica las dos paredes compartidas.
- Al terminar, se comprueba que todas las celdas transitables hayan sido visitadas.
- Se preparó el soporte para excluir las celdas reservadas del patrón «42».

### Información para Michele

- Importación actual: `from mazegen.maze import MazeGenerator`.
- Coordenadas: `(x, y)`. Acceso a las celdas: `maze.grid[y][x]`.
- Paredes: `True` significa cerrada y `False` significa abierta.
- Los métodos que empiezan por `_` son internos del motor.
- `_generate_dfs` entrega pasos mediante un iterador. El recorrido avanza cuando se consumen esos pasos.
- Cada paso contiene `((x_origen, y_origen), (x_destino, y_destino))` y se entrega después de abrir el paso.
- La interfaz puede consultar `maze.grid` en ese momento para representar el estado actualizado.

### Organización y comprobaciones

- Se añadió `mazegen/__init__.py` para identificar el paquete.
- El motor permanece en `mazegen/maze.py`:
- Se comprobaron posiciones de entrada y salida válidas, fuera de los límites e iguales.
- La prueba de 3 × 2 conectó las seis celdas mediante cinco aperturas, sin ciclos.