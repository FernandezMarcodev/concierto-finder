from app.models.ubicacion import Ubicacion


def obtener_ubicaciones():
    return Ubicacion.query.order_by(Ubicacion.nombre).all()


def buscar_ubicacion_por_nombre(nombre):
    # Coincidencia parcial sin distinguir mayúsculas. Se escapan los comodines
    # de LIKE para que un "%" o "_" en el nombre no amplíe la búsqueda.
    patron = nombre.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return Ubicacion.query.filter(Ubicacion.nombre.ilike(f"%{patron}%", escape="\\")).first()
