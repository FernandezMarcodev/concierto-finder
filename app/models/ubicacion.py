from geoalchemy2 import Geometry

from app.extensions import db


class Ubicacion(db.Model):
    __tablename__ = "ubicaciones"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    capacidad_total = db.Column(db.Integer, nullable=False)  # la fuente no la informa: siempre 0
    coordenadas = db.Column(Geometry("POINT", srid=4326))  # [lng, lat]
    url_maps = db.Column(db.String(100))

    conciertos = db.relationship("Concierto", back_populates="ubicacion_ref", cascade="all, delete")
