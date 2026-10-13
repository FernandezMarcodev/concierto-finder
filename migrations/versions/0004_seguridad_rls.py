"""Seguridad: RLS en las tablas de public y sin permisos para los roles de la Data API.

En producción la base está en Supabase, que publica el esquema `public` a través de su
propia API REST (la "Data API", con los roles `anon` y `authenticated`). Esta app no la usa:
el frontend habla solo con la API de Flask. Pero si las tablas no tienen seguridad a nivel de
fila (RLS), cualquiera con la URL del proyecto y la clave pública podría leer, editar o borrar
los datos salteándose la API (aviso `rls_disabled_in_public` de Supabase).

1. Se habilita RLS en las tablas de `public` cuyo dueño es el usuario que corre la migración.
   Sin políticas, RLS no deja ver ni tocar ninguna fila a otros roles. La API de Flask no se
   ve afectada: se conecta con el usuario dueño de las tablas, y en PostgreSQL el dueño no
   está sujeto a RLS (salvo FORCE ROW LEVEL SECURITY, que no se usa).
2. Si existen los roles `anon` y `authenticated` (solo en Supabase), se les quitan los
   permisos sobre las tablas, también sobre las que se creen en el futuro.

Una tabla con otro dueño (por ejemplo, `spatial_ref_sys` si la creó otro usuario al instalar
PostGIS) no se toca: se informa con un NOTICE en lugar de fallar, para que el deploy no se
caiga por una tabla ajena al proyecto.

Revision ID: 0004_seguridad_rls
Revises: 0003_historial_conciertos
Create Date: 2026-10-13
"""

from alembic import op

revision = "0004_seguridad_rls"
down_revision = "0003_historial_conciertos"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DO $$
        DECLARE
            tabla record;
            rol text;
        BEGIN
            FOR tabla IN
                SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public'
            LOOP
                IF tabla.tableowner = current_user THEN
                    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tabla.tablename);
                ELSE
                    RAISE NOTICE 'RLS no habilitado en public.% (dueño: %)', tabla.tablename, tabla.tableowner;
                END IF;
            END LOOP;

            FOREACH rol IN ARRAY ARRAY['anon', 'authenticated'] LOOP
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = rol) THEN
                    EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM %I', rol);
                    EXECUTE format('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM %I', rol);
                    EXECUTE format(
                        'ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM %I', rol
                    );
                END IF;
            END LOOP;
        END
        $$;
    """)


def downgrade():
    # Solo se desactiva RLS. Los permisos quitados a anon y authenticated no se devuelven:
    # volver a exponer las tablas tiene que ser una decisión explícita, no un efecto del downgrade.
    op.execute("""
        DO $$
        DECLARE
            tabla record;
        BEGIN
            FOR tabla IN
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public' AND tableowner = current_user
            LOOP
                EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', tabla.tablename);
            END LOOP;
        END
        $$;
    """)
