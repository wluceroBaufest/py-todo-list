# TODO List API

Backend REST API para gestión de tareas (TODO list) construido con FastAPI y SQLAlchemy.

Los datos se almacenan en una base de datos SQLite en memoria, por lo que se reinician al detener el servidor.

## Requisitos

- Python 3.12+

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python -m uvicorn app.main:app --reload
```

El servidor se levanta en `http://localhost:8000`.

## Endpoints

| Método   | Ruta            | Descripción                                      |
|----------|-----------------|--------------------------------------------------|
| `POST`   | `/todos/`       | Crear un nuevo todo                              |
| `GET`    | `/todos/`       | Listar todos (filtro opcional `?completed=true`)  |
| `GET`    | `/todos/{id}`   | Obtener un todo por ID                           |
| `PUT`    | `/todos/{id}`   | Actualizar un todo                               |
| `DELETE` | `/todos/{id}`   | Eliminar un todo                                 |
| `POST`   | `/todos/{id}/subtasks/` | Crear una subtarea para un todo            |
| `GET`    | `/todos/{id}/subtasks/` | Listar subtareas (filtro opcional `?completed=true`) |
| `GET`    | `/todos/{id}/subtasks/{subtask_id}` | Obtener una subtarea por ID     |
| `PUT`    | `/todos/{id}/subtasks/{subtask_id}` | Actualizar una subtarea          |
| `DELETE` | `/todos/{id}/subtasks/{subtask_id}` | Eliminar una subtarea            |

## Ejemplos

Crear un todo:

```bash
curl -X POST http://localhost:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Comprar leche", "description": "En el supermercado"}'
```

Listar todos:

```bash
curl http://localhost:8000/todos/
```

Actualizar un todo:

```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

Eliminar un todo:

```bash
curl -X DELETE http://localhost:8000/todos/1
```

Crear una subtarea:

```bash
curl -X POST http://localhost:8000/todos/1/subtasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Ir al supermercado", "description": "Antes de las 18:00"}'
```

Listar subtareas:

```bash
curl http://localhost:8000/todos/1/subtasks/
```
