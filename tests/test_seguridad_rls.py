"""Migración 0004: las tablas del proyecto tienen RLS y un rol ajeno (como `anon` de Supabase) no ve filas."""

from sqlalchemy import text

TABLAS_DEL_PROYECTO = ("conciertos", "ubicaciones", "alembic_version")


def test_las_tablas_del_proyecto_tienen_rls(base):
    filas = base.execute(
        text("SELECT relname, relrowsecurity FROM pg_class WHERE relname = ANY(:tablas)"),
        {"tablas": list(TABLAS_DEL_PROYECTO)},
    ).all()

    assert {nombre: activo for nombre, activo in filas} == dict.fromkeys(TABLAS_DEL_PROYECTO, True)


def test_un_rol_ajeno_no_ve_filas_aunque_tenga_permiso_de_lectura(base, crear_concierto):
    """
    Simula la Data API de Supabase: un rol con SELECT pero sin políticas de RLS no ve nada,
    mientras que el dueño de las tablas (el usuario de la API de Flask) sigue viendo todo.
    Todo ocurre en una transacción que se revierte: el rol de prueba no queda creado.
    """
    crear_concierto(nombre="Visible solo para el dueño")

    base.execute(text("CREATE ROLE anon_prueba NOLOGIN"))
    base.execute(text("GRANT SELECT ON conciertos TO anon_prueba"))
    base.execute(text("SET LOCAL ROLE anon_prueba"))
    filas_para_anon = base.execute(text("SELECT count(*) FROM conciertos")).scalar()
    base.execute(text("RESET ROLE"))
    filas_para_el_duenio = base.execute(text("SELECT count(*) FROM conciertos")).scalar()
    base.rollback()

    assert filas_para_anon == 0
    assert filas_para_el_duenio == 1
