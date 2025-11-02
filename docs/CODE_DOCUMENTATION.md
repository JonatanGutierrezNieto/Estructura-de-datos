# Documentación del código

## Resumen rápido
- Lenguaje: Python 3 (3.8+ recomendado)
- Framework GUI: PyQt5
- Patrón arquitectónico: MVC (Model — View — Controller), implementado de forma clásica para aplicaciones de escritorio: la clase `LibraryStore` y las clases de datos son el Modelo, `MainView` es la Vista, y `LibraryController` es el Controlador que conecta eventos de la vista con la lógica del modelo.
- Persistencia: JSON en `library_data.json` (en la raíz del proyecto).
- Archivo de log de acciones: `library_actions.log` (creado/actualizado por el controlador).

---

## Estructura principal de archivos
- `main.py` — Punto de entrada. Inicializa QApplication, crea `LibraryController` y muestra la interfaz.
- `controllers/library_controller.py` — Controlador principal. Conecta señales de la UI con las operaciones del modelo y actualiza la vista.
- `models/library_models.py` — Modelo y clases de dominio: `Book`, `BorrowedBook`, `User` y `LibraryStore` (almacenamiento, operaciones CRUD y lógica de préstamos/colas/deshacer).
- `views/main_view.py` — Interfaz de usuario (PyQt5). Define los widgets y tablas que muestra la aplicación.
- `library_data.json` — Datos persistentes (libros y usuarios). Se carga al iniciar y se guarda tras cambios.
- `README.md` — Instrucciones de uso del proyecto.

---

## Tipo de MVC usado
El proyecto sigue un MVC clásico para aplicaciones de escritorio:
- Modelo: `LibraryStore` + dataclasses `Book`, `User`, `BorrowedBook`.
  - Se encarga de la persistencia en JSON, mantener listas de libros/usuarios, gestionar la cola de reservas y la pila de deshacer.
- Vista: `MainView` (hereda de `QWidget`), contiene todos los widgets (tabs, tablas, botones, filtros, combos) y ofrece nombres de atributos accesibles por el controlador.
- Controlador: `LibraryController` instancia `MainView` y `LibraryStore`, conecta señales (botones, filtros, combos) y realiza llamadas al modelo. También actualiza la vista.

Comentarios:
- No hay un framework MVC estricto; la separación es manual y adecuada para una aplicación PyQt5 pequeña.
- El controlador dirige el flujo: recibe eventos de la vista → valida / transforma datos → invoca métodos del modelo → refresca la vista.

---

## Model: clases y funciones clave (`models/library_models.py`)

Clases principales:
- `Book` (dataclass)
  - Campos: `id`, `title`, `author`, `year`, `copies_total`, `copies_available`, `reservations` (deque)
  - `to_dict` / `from_dict` para serializar a JSON.
- `BorrowedBook` (dataclass)
  - Campos: `book_id`, `fecha`, `quantity` (cantidad prestada de ese libro por usuario).
- `User` (dataclass)
  - Campos: `id`, `name`, `email`, `borrowed` (lista de `BorrowedBook`).

`LibraryStore` (persistencia y lógica):
- __init__(data_file: str = "library_data.json")
  - Carga datos desde JSON y prepara listas `books`, `users` y `undo_stack`.
- `_load()` / `_save()`
  - Lectura/escritura de `library_data.json` con UTF-8.
- `seed_if_empty()`
  - Añade datos de ejemplo si no hay libros/usuarios.
- `find_book(book_id)` / `find_user(user_id)`
  - Búsqueda lineal en listas (O(n)) — apropiado para una demo/ejercicio.
- `add_book(book)` / `add_user(user)`
  - Validación de duplicados por ID, guarda en JSON.
- `borrow_book(user_id, book_id, fecha)`
  - Lógica:
    - Si hay copias disponibles: decrementa `copies_available`, añade o incrementa `BorrowedBook` en `user.borrowed`, empuja operación a `undo_stack`.
    - Si no hay copias: agrega `user_id` a `book.reservations` (cola `deque`) y guarda.
  - Retorna cadenas con prefijos para el controlador: `[✓]`, `[X]`, `[→]`, `[i]`.
- `return_book(user_id, book_id)`
  - Lógica:
    - Verifica que el usuario realmente tenga el préstamo.
    - Decrementa cantidad en `user.borrowed` (o lo elimina si queda 0).
    - Incrementa `book.copies_available`.
    - Si hay reservas, asigna automáticamente la copia al siguiente en cola (reduce `copies_available` y añade `BorrowedBook` a ese usuario), y registra la operación en `undo_stack` con info `autoloan_to_next`.
- `undo_last()`
  - Implementa deshacer para la última operación en `undo_stack` (soporta `borrow` y `return`).

Formato de persistencia (`library_data.json`):
- Objeto con `books` (lista de diccionarios) y `users` (lista de diccionarios).
- `Book.reservations` se guarda como lista de IDs (se reconvierte a `deque` al cargar).

---

## Controller: responsabilidades y funciones (`controllers/library_controller.py`)
Funciones / métodos clave:
- `__init__`:
  - Crea `MainView`, `LibraryStore`, llama `seed_if_empty()`, conecta señales y refresca combos de préstamo.
- `_connect_signals()`:
  - Conecta botones y campos de la vista a métodos como `on_add_book`, `on_list_books`, `on_borrow`, `on_return`, `on_undo`, filtros, etc.
- `_refresh_loan_combos()`:
  - Rellena los `QComboBox` de usuarios y libros con los IDs y textos de disponibilidad; muestra tanto libros disponibles como información de cola.
- `_notify(text, level, timeout_ms)` y `_write_log(text)`:
  - Muestra mensajes al usuario con `QMessageBox` (iconos y emojis según tipo) y escribe una línea en `library_actions.log`.
- Operaciones de libros:
  - `on_add_book()` — valida campos (año y copias enteros), crea `Book`, llama `model.add_book`, refresca vista.
  - `on_toggle_list_books()` / `on_list_books()` — muestra/oculta tabla y la rellena con datos. `filter_books_table(text)` aplica filtrado por texto en la tabla.
- Operaciones de usuarios:
  - `on_add_user()` — valida campos, llama `model.add_user`, limpia inputs y refresca.
  - `on_toggle_list_users()` / `on_list_users()` — rellena tabla de usuarios (incluye lista de libros prestados y conteo) y permite filtrado con `filter_users_table`.
- Préstamos y devoluciones:
  - `on_borrow()` — extrae `user_id` y `book_id` (usa `_extract_user_id` y `_extract_book_id` si procede), valida fecha, llama `model.borrow_book`, actualiza tablas y combos.
  - `on_return()` — extrae ids, llama `model.return_book`, refresca UI.
  - `_extract_user_id(user_text)` / `_extract_book_id(book_text)` — utilidades para parsear el texto editable de los `QComboBox`.
  - `on_undo()` — llama `model.undo_last()` y refresca vistas.
- Listado de prestados/reservas:
  - `on_list_prestados()` / `on_toggle_list_prestados()` y filtros relacionados: muestran filas por cada item prestado combinando datos de usuario y libro.

Notas importantes:
- El controlador interpreta los mensajes retornados por el modelo para mostrar iconos y tipos de mensaje (éxito/advertencia/error/información/cola).
- Muchas funciones repiten la lógica de refrescar vistas tras cambios — buena candidata para consolidar en un método `refresh_all()` si se desea refactorizar.

---

## View: elementos relevantes (`views/main_view.py`)
- La UI está organizada en un `QTabWidget` con 3 pestañas:
  - "Libros": formulario para crear libros, botón de listar, filtro y `QTableWidget` con columnas: ID, Título, Autor, Año, Totales, Disponibles, En cola.
  - "Usuarios": formulario para crear usuarios, botón de listar, filtro y `QTableWidget` con columnas: ID, Nombre, Email, Libros Prestados, Cantidad.
  - "Préstamos": combos para seleccionar usuario/libro, `QDateEdit` para fecha, botones Prestar/Devolver/Deshacer, y secciones para listar préstamos y reservaciones con tablas y filtros.
- Los nombres de atributos de widget son explícitos y usados por el controlador: `btn_add_book`, `table_books`, `book_filter`, `loan_user_combo`, `loan_book_combo`, `prestamo_fecha`, `table_prestamos`, etc.
- Estilos: botones con CSS inline y tablas tuneadas con `_tune_table()`.

---

## Cómo ejecutar
1. Instalar dependencias (PyQt5):

```powershell
pip install PyQt5
```

2. Ejecutar la aplicación:

```powershell
python .\main.py
```

Observaciones:
- El archivo `library_data.json` se lee/escribe en la carpeta del proyecto; cambia la ruta en `LibraryStore` si quieres otro lugar.
- El archivo de log `library_actions.log` se crea en la raíz del proyecto cuando se realizan acciones.

---

## Contrato / Signatures principales (resumen)
- LibraryStore.borrow_book(user_id: str, book_id: str, fecha: str) -> str
  - Entrada: IDs existentes y fecha (ISO `YYYY-MM-DD`).
  - Salida: mensaje string con prefijos `[✓]`, `[X]`, `[→]`, `[i]` indicando éxito/error/cola/info.
- LibraryStore.return_book(user_id: str, book_id: str) -> str
  - Entrada: IDs existentes.
  - Salida: mensaje string similar.
- Controller methods: usan y esperan strings/valores del UI; por ejemplo `on_add_book()` lee widgets `book_year` y `book_copies` y convierten a int.

---

## Casos borde y consideraciones
- Búsqueda lineal (find_book/find_user): con muchos registros, será lento; para escalado usar dicts/indexes o base de datos.
- Concurrencia: la app es de escritorio; no está pensada para accesos concurrentes desde varios procesos. Si se necesitara, usar una base de datos con locking/ACID.
- Validación: la validación en `on_add_book` y `on_add_user` es básica. Podría reforzarse (emails, formato de ID, límites en copias, saneamiento de texto).
- Manejo de errores en IO: `_load()` atrapa excepciones e imprime advertencia; podrías mostrar un diálogo y permitir elegir otro archivo.
- Undo: la pila de `undo_stack` guarda operaciones básicas; en escenarios complejos (autoloan) trata de restaurar coherencia, pero conviene testear casos extremos.

---

## Sugerencias de mejoras (pequeñas y seguras)
- Añadir tests unitarios para `LibraryStore` — cubrir `borrow_book`, `return_book`, `undo_last`, reservas y persistencia.
- Refactor: centralizar refresco de UI en `LibraryController` (método `refresh_all`) para evitar repetición.
- Reemplazar listas por diccionarios indexados por ID o agregar índices en `LibraryStore` para búsquedas O(1).
- Añadir validaciones y mensajes más descriptivos (por ejemplo, mostrar ventana con detalles de error si la escritura a disco falla).
- Internacionalización (i18n) si se desea soportar múltiples idiomas.

---

## Archivos creados / modificados por la aplicación
- `library_data.json` — persistencia principal.
- `library_actions.log` — append con líneas timestamped cuando se muestran notificaciones.

---

## Próximos pasos que puedo hacer por ti
- Añadir un archivo `docs/USAGE.md` con capturas de pantalla y flujo de uso.
- Implementar tests unitarios para `models/library_models.py`.
- Refactorizar el controlador para reducir duplicación y añadir `refresh_all()`.

---

Documentación generada automáticamente en base al contenido actual del repositorio.
