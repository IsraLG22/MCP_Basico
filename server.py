from mcp.server.fastmcp import FastMCP
from pathlib import Path
import json
import requests

mcp = FastMCP()

BASE_DIR = Path(__file__).parent
TASKS_FILE = BASE_DIR / "tasks.json"

if not TASKS_FILE.exists():
    TASKS_FILE.write_text("[]", encoding="utf-8")

def load_tasks():
    return json.loads(TASKS_FILE.read_text(encoding="utf-8"))

def save_tasks(tasks):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


@mcp.tool()
def sumar(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def analizar_archivo(archivo: Path) -> dict:
    path = Path(archivo)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"El archivo {path} no existe.")
    
    return {
        "nombre": path.name,
        "extension": path.suffix,
        "contenido": path.read_text(encoding="utf-8"),
        "tamaño_bytes": path.stat().st_size,
        "fecha_de_creacion": path.stat().st_ctime
    }

@mcp.tool()
def clima_por_ciudad(ciudad: str) -> dict:
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1"
    geo = requests.get(geo_url).json()

    if "results" not in geo or len(geo["results"]) == 0:
        raise ValueError(f"No se encontró la ciudad '{ciudad}'")

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )
    clima = requests.get(weather_url).json()

    return {
        "ciudad": ciudad,
        "latitud": lat,
        "longitud": lon,
        "clima": clima.get("current_weather", {})
    }



@mcp.tool()
def agregar_tarea(descripcion: str) -> dict:
    tasks = load_tasks()
    nueva = {
        "id": len(tasks) + 1,
        "descripcion": descripcion,
        "completada": False
    }
    tasks.append(nueva)
    save_tasks(tasks)
    return nueva

@mcp.tool()
def listar_tareas() -> list:
    return load_tasks()

@mcp.tool()
def completar_tarea(task_id: int) -> dict:
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["completada"] = True
            save_tasks(tasks)
            return t
    raise ValueError("ID no encontrado.")

@mcp.tool()
def eliminar_tarea(task_id: int) -> dict:
    tasks = load_tasks()
    nuevas = [t for t in tasks if t["id"] != task_id]
    if len(nuevas) == len(tasks):
        raise ValueError("ID no encontrado.")
    save_tasks(nuevas)
    return {"eliminada": task_id}


# ---- RUN ----
if __name__ == "__main__":
    mcp.run()
