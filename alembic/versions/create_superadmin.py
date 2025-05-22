"""Create Superadmin User

Revision ID: create_superadmin
Revises: add_url_table
Create Date: 2023-06-10 12:00:00.000000

"""
from typing import Sequence, Union
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, Integer, DateTime
import datetime
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = 'create_superadmin'
down_revision: Union[str, None] = 'add_url_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Configuración para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def upgrade() -> None:
    """Crear usuario superadmin."""
    # Obtener credenciales de las variables de entorno
    superadmin_email = os.getenv("SUPERADMIN_EMAIL", "admin@example.com")
    superadmin_password = os.getenv("SUPERADMIN_PASSWORD", "supersecret")

    # Definir la tabla de usuarios
    users = table('users',
        column('id', Integer),
        column('email', String),
        column('hashed_password', String),
        column('is_active', Boolean),
        column('is_superuser', Boolean),
        column('is_verified', Boolean),
        column('role', String),
        column('verification_token', String),
        column('reset_token', String),
        column('created_at', DateTime),
        column('updated_at', DateTime)
    )

    # Hashear la contraseña
    hashed_password = hash_password(superadmin_password)

    # Comprobar si el superadmin ya existe
    conn = op.get_bind()
    result = conn.execute(
        sa.text(f"SELECT id FROM users WHERE email = '{superadmin_email}'")
    ).fetchone()

    # Si no existe, lo creamos
    if not result:
        op.bulk_insert(
            users,
            [
                {
                    'email': superadmin_email,
                    'hashed_password': hashed_password,
                    'is_active': True,
                    'is_superuser': True,
                    'is_verified': True,
                    'role': 'admin',
                    'verification_token': None,
                    'reset_token': None,
                    'created_at': datetime.datetime.now(datetime.timezone.utc),
                    'updated_at': datetime.datetime.now(datetime.timezone.utc)
                }
            ]
        )


def downgrade() -> None:
    """Eliminar usuario superadmin."""
    superadmin_email = os.getenv("SUPERADMIN_EMAIL", "admin@example.com")

    # Ejecutar SQL para eliminar el superadmin
    op.execute(f"DELETE FROM users WHERE email = '{superadmin_email}'")
