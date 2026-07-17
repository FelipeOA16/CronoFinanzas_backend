"""Seed subcategorías predeterminadas para categorías de sistema

Revision ID: 0010_subcategorias_sistema
Revises: 0009_presupuestos
Create Date: 2026-05-31 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_subcategorias_sistema"
down_revision = "0009_presupuestos"
branch_labels = None
depends_on = None

# Subcategorías por categoría padre (usuario_id=NULL = sistema)
# Formato: (padre_nombre, nombre_hija, color, icono)
SUBCATEGORIAS = [
    # Alimentación
    ("Alimentación", "Supermercado",       "#FF5722", "shopping_cart"),
    ("Alimentación", "Restaurantes",       "#FF5722", "restaurant"),
    ("Alimentación", "Cafeterías",         "#FF5722", "coffee"),
    ("Alimentación", "Comida a domicilio", "#FF5722", "delivery_dining"),

    # Transporte
    ("Transporte", "Gasolina",              "#2196F3", "local_gas_station"),
    ("Transporte", "Transporte público",    "#2196F3", "directions_bus"),
    ("Transporte", "Taxi / Uber",           "#2196F3", "local_taxi"),
    ("Transporte", "Mantenimiento vehículo","#2196F3", "build"),
    ("Transporte", "Peajes / Estacionamiento","#2196F3","payments"),

    # Vivienda
    ("Vivienda", "Alquiler",          "#795548", "home"),
    ("Vivienda", "Hipoteca",          "#795548", "account_balance"),
    ("Vivienda", "Agua / Luz / Gas",  "#795548", "electrical_services"),
    ("Vivienda", "Internet / Cable",  "#795548", "wifi"),
    ("Vivienda", "Mantenimiento",     "#795548", "handyman"),

    # Salud
    ("Salud", "Médico / Consulta",  "#E91E63", "medical_services"),
    ("Salud", "Farmacia",           "#E91E63", "local_pharmacy"),
    ("Salud", "Gimnasio",           "#E91E63", "fitness_center"),
    ("Salud", "Seguro médico",      "#E91E63", "health_and_safety"),
    ("Salud", "Odontología",        "#E91E63", "dentistry"),

    # Entretenimiento
    ("Entretenimiento", "Streaming",       "#9C27B0", "subscriptions"),
    ("Entretenimiento", "Cine / Teatro",   "#9C27B0", "theaters"),
    ("Entretenimiento", "Videojuegos",     "#9C27B0", "sports_esports"),
    ("Entretenimiento", "Viajes",          "#9C27B0", "flight"),
    ("Entretenimiento", "Eventos / Salidas","#9C27B0","event"),

    # Ropa
    ("Ropa", "Ropa",        "#FF9800", "checkroom"),
    ("Ropa", "Calzado",     "#FF9800", "steps"),
    ("Ropa", "Accesorios",  "#FF9800", "watch"),

    # Educación
    ("Educación", "Cursos / Estudios",  "#3F51B5", "school"),
    ("Educación", "Libros / Materiales","#3F51B5", "menu_book"),
    ("Educación", "Idiomas",            "#3F51B5", "translate"),
    ("Educación", "Software / Tools",   "#3F51B5", "laptop"),

    # Inversiones (ingreso)
    ("Inversiones", "Acciones",         "#FFC107", "trending_up"),
    ("Inversiones", "Fondos",           "#FFC107", "pie_chart"),
    ("Inversiones", "Criptomonedas",    "#FFC107", "currency_bitcoin"),
    ("Inversiones", "Bienes raíces",    "#FFC107", "apartment"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for padre_nombre, nombre_hija, color, icono in SUBCATEGORIAS:
        conn.execute(
            sa.text(
                """
                INSERT INTO categorias (nombre, tipo, color, icono, padre_id, usuario_id)
                SELECT :nombre, c.tipo, :color, :icono, c.id, NULL
                FROM categorias c
                WHERE c.nombre = :padre_nombre
                  AND c.usuario_id IS NULL
                  AND c.padre_id IS NULL
                  AND c.deleted_at IS NULL
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "nombre": nombre_hija,
                "color": color,
                "icono": icono,
                "padre_nombre": padre_nombre,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM categorias
            WHERE usuario_id IS NULL
              AND padre_id IS NOT NULL
            """
        )
    )
