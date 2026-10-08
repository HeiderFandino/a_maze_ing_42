# Actualizaciones

## 08/10/2026 - actualizacion M08 y M09

### M08: anadido regeneracion y cambio de colores

Al generar un laberinto ahora te pide un numero para elegir entre varias opciones.

El programa comprueba que el usuario ponga un numero haciendo try / except y que no sea mas grande que las opciones disponibles.

Las opciones estan en un bucle while que se detiene solo con la opcion 0)

0) Detiene el codigo y te permite volver a utilizar la terminal haciendo un break
1) Vuelve a hacer un bucle de generate-dfs para crear el nuevo laberinto y despues draw-solid para imprimirlo
2) Cambia el color al siguiente de la lista y vuelve a imprimir el laberinto con draw-solid
3) Crea un archivo y escribe el laberinto en hexadecimal junto a entry-pos y exit-pos

Los colores estan en un archivo a parte llamado colors.py e importados a interfaz.py

### M09: anadido animacion al laberinto

Hay una cuarta opcion que permite activar y desactivar la animacion.

Cuando esta opcion se activa, se activa un bool que permite imprimir cada paso del algoritmo dfs cada un 0.04s.

Cada paso tiene que limpiar la terminal para que pueda ser una animacion.

## 07/10/2026 — actualización H02 y cierre de H03

### Cambio de contrato de `MazeGenerator`

El generador ahora recibe entrada y salida desde su construcción:

`MazeGenerator(width, height, entry_pos, exit_pos)`

La entrada y la salida pasan a formar parte del estado del objeto:

- `self.entry_pos`
- `self.exit_pos`

Esto evita mantener distintas entradas o salidas en diferentes partes del motor.

El constructor realiza ahora este flujo:

1. Comprueba que `width` y `height` sean positivos.
2. Guarda las dimensiones.
3. Guarda `entry_pos` y `exit_pos`.
4. Ejecuta `_validate_endpoints()`.
5. Crea la cuadrícula.

### H02: validación de parámetros

`_validate_endpoints()` ya no recibe parámetros externos.

Valida directamente:

- `self.entry_pos` dentro del tablero.
- `self.exit_pos` dentro del tablero.
- `self.entry_pos != self.exit_pos`.

De esta forma, si se consigue crear una instancia de `MazeGenerator`, sus dimensiones, entrada y salida básicas ya son válidas.

### Validación de celdas bloqueadas

`_generate_dfs()` recibe:

- `blocked`
- `seed`

Ya no recibe `entry_pos`: utiliza directamente `self.entry_pos`.

Antes de generar:

- Comprueba que todas las posiciones de `blocked` estén dentro del tablero.
- Comprueba que `self.entry_pos` no esté bloqueada.
- Comprueba que `self.exit_pos` no esté bloqueada.

Las celdas de `blocked` se consideran completamente no transitables y el DFS nunca entra en ellas.

Esto servirá posteriormente para reservar las celdas completamente cerradas del patrón «42».

### H03: generación perfecta

La implementación actual utiliza DFS iterativo:

- `visited` registra las celdas visitadas.
- `stack` mantiene el recorrido y permite hacer backtracking.
- Solo se seleccionan vecinos que:
  - estén dentro del tablero;
  - no hayan sido visitados;
  - no estén bloqueados.
- `random.Random(seed)` controla la aleatoriedad.
- `open_passage()` mantiene coherentes las paredes compartidas.
- Cada nueva celda se conecta una sola vez al árbol existente.
- Al terminar se verifica que todas las celdas transitables hayan sido alcanzadas.

Como el algoritmo conecta todas las celdas transitables sin abrir conexiones hacia celdas ya visitadas, la estructura generada es un árbol y, por tanto, no contiene ciclos.

En consecuencia, en este modo existe un único camino entre cualquier par de celdas transitables, incluida la entrada y la salida.

### Reproducibilidad

Se comprobó que:

- mismos parámetros + misma `seed` producen exactamente la misma cuadrícula;
- diferentes semillas producen laberintos distintos;
- la propiedad de laberinto perfecto se mantiene con distintos tamaños y semillas.

### Pruebas ejecutadas para H03

Se ejecutó `python3 pruebas.py` con los siguientes resultados:

- `[OK] Same seed produces the same maze`
- `[OK] Different seeds produce different mazes`
- `[OK] Maze has V - 1 passages`
- `[OK] No cycles detected`
- `[OK] 3x3, seed=1`
- `[OK] 5x5, seed=25`
- `[OK] 10x10, seed=42`
- `[OK] 15x8, seed=100`
- `[OK] Blocked cell remains fully closed`
- `[OK] Perfect invariant survives blocked cells`

Resultado final:

`All H03 tests passed.`

### Estado actual

- H01 — estructura de celdas, coordenadas y paredes: TERMINADO Y PROBADO.
- H02 — validaciones básicas del motor: TERMINADO Y PROBADO.
- H03 — generación perfecta con semilla reproducible: TERMINADO Y PROBADO.

Las validaciones específicas que dependan posteriormente del patrón «42» o de otros modos de generación se ampliarán cuando se implementen esas funcionalidades.

### Impacto para la interfaz

La interfaz debe construir ahora el generador proporcionando también entrada y salida:

`MazeGenerator(width, height, entry_pos, exit_pos)`

La generación ya no recibe una entrada independiente:

`_generate_dfs(blocked=..., seed=...)`

La entrada oficial está disponible en:

`self.entry_pos`

y la salida oficial en:

`self.exit_pos`.

Para evitar inconsistencias, la interfaz debería utilizar esas posiciones como fuente de verdad al mostrar `S` y `E`.

## 06/10/2026 — 18:37

### Validaciones básicas — H02

- Se creó `_validate_endpoints()` para comprobar que entrada y salida estén dentro de la cuadrícula y sean diferentes.
- Las coordenadas inválidas producen `ValueError` con un mensaje descriptivo.

### Avances en la generación perfecta — H03

- `_get_neighbors(x, y)` obtiene los vecinos dentro de los límites, en orden norte, este, sur y oeste.
- `_get_available_neighbors(...)` excluye las celdas visitadas y bloqueadas.
- `_generate_dfs(...)` construye el laberinto mediante DFS iterativo, utilizando una pila y un conjunto de celdas visitadas.
- La generación comienza con todas las paredes cerradas y utiliza una semilla para controlar las decisiones aleatorias.
- Cada apertura modifica las dos paredes compartidas.
- Al terminar, se comprueba que todas las celdas transitables hayan sido visitadas.
- Se preparó soporte para excluir celdas reservadas, necesario posteriormente para el patrón «42».

### Información para Michele

- Importación del paquete: `from mazegen.maze import MazeGenerator`.
- Coordenadas: `(x, y)`.
- Acceso a las celdas: `maze.grid[y][x]`.
- Paredes: `True` significa cerrada y `False` significa abierta.
- Los métodos que empiezan por `_` son internos del motor.
- `_generate_dfs()` entrega pasos mediante un iterador.
- Cada paso tiene la forma:
  `((x_origen, y_origen), (x_destino, y_destino))`.
- El paso se entrega después de abrir las paredes correspondientes, por lo que la interfaz puede consultar `maze.grid` y representar el nuevo estado.

## 06/10/2026 — 16:14

### H01: estructura del motor y apertura de pasos

#### Cambios realizados

- Creada la clase `MazeGenerator` con una cuadrícula de celdas independientes y todas las paredes inicialmente cerradas.
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
