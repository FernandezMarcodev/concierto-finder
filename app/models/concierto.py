from app.extensions import db

# Largo máximo de nombre y artista. El scraper recorta los textos a este largo antes de guardar.
LARGO_TEXTO = 50


class Concierto(db.Model):
    __tablename__ = "conciertos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(LARGO_TEXTO), nullable=False)
    artista = db.Column(db.String(LARGO_TEXTO), nullable=False)
    url_evento = db.Column(db.Text)  # sin límite: las URLs de entradas suelen superar los 100 caracteres
    ubicacion = db.Column(db.Integer, db.ForeignKey("ubicaciones.id", ondelete="CASCADE"))
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time)

    ubicacion_ref = db.relationship("Ubicacion", back_populates="conciertos")
