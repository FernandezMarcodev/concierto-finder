"""Comandos de consola: `flask --app app <comando>`. No arrancan las tareas en segundo plano."""

import os

import click
from flask import Flask

from app.extensions import db
from app.repositories.concierto_repository import contar_conciertos, vaciar_conciertos_y_ubicaciones
from app.services import datos_ficticios
from app.services.fechas import hoy_argentina


@click.command("sembrar")
@click.option("--cantidad", default=400, show_default=True, help="Cantidad de conciertos a generar.")
@click.option("--meses", default=12, show_default=True, help="Meses hacia atrás (y 3 hacia adelante).")
@click.option("--semilla", default=42, show_default=True, help="Misma semilla = mismos datos.")
@click.option("--vaciar", is_flag=True, help="Borra TODOS los conciertos y lugares antes de sembrar.")
def sembrar(cantidad, meses, semilla, vaciar):
    """Llena la base con conciertos ficticios (solo para desarrollo)."""
    # Render define la variable RENDER en sus servicios: en producción no se siembra nunca.
    if os.getenv("RENDER"):
        raise click.ClickException("No se siembran datos ficticios en producción.")

    existentes = contar_conciertos()
    if existentes and not vaciar:
        raise click.ClickException(
            f"La base ya tiene {existentes} conciertos. Para no mezclar datos reales con ficticios, "
            "agregá --vaciar (borra todos los conciertos y lugares) o usá otra base."
        )
    if vaciar:
        vaciar_conciertos_y_ubicaciones()
        db.session.commit()
        click.echo(f"Se borraron {existentes} conciertos y todos los lugares.")

    guardados = datos_ficticios.sembrar(hoy_argentina(), cantidad, meses, semilla)
    click.echo(f"Se guardaron {guardados} conciertos ficticios en {len(datos_ficticios.LUGARES)} lugares.")


def registrar_comandos(app: Flask):
    app.cli.add_command(sembrar)
