# Importar este paquete registra todos los modelos en el metadata (lo necesitan las migraciones).
from app.models.concierto import Concierto
from app.models.ubicacion import Ubicacion

__all__ = ["Concierto", "Ubicacion"]
