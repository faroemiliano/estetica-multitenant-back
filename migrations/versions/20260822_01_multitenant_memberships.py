"""Agregar membresias multitenant preservando usuarios existentes de Aura."""

from alembic import op
import sqlalchemy as sa


revision = "20260822_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("users"):
        # Instalacion nueva: el modelo actual constituye el esquema inicial.
        import app.models
        from app.database import Base

        Base.metadata.create_all(bind=bind)
        return

    op.create_table(
        "memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("estetica_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), server_default="cliente", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["estetica_id"], ["esteticas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "estetica_id", name="uq_membership_user_estetica"),
    )
    op.create_index(op.f("ix_memberships_id"), "memberships", ["id"], unique=False)

    # Cada usuario actual conserva exactamente su estetica y rol actuales.
    op.execute(
        """
        INSERT INTO memberships (user_id, estetica_id, role, activo)
        SELECT id, estetica_id, COALESCE(role, 'cliente'), TRUE
        FROM users
        WHERE estetica_id IS NOT NULL
        ON CONFLICT (user_id, estetica_id) DO NOTHING
        """
    )

    # El perfil de cliente pasa a ser unico dentro del tenant, no globalmente.
    unique_constraints = sa.inspect(bind).get_unique_constraints("clientes")
    for constraint in unique_constraints:
        columns = set(constraint.get("column_names") or [])
        if columns in ({"google_id"}, {"email"}):
            op.drop_constraint(constraint["name"], "clientes", type_="unique")
    op.create_unique_constraint(
        "uq_cliente_user_estetica", "clientes", ["user_id", "estetica_id"]
    )
    op.create_unique_constraint(
        "uq_cliente_email_estetica", "clientes", ["email", "estetica_id"]
    )


def downgrade():
    op.drop_constraint("uq_cliente_email_estetica", "clientes", type_="unique")
    op.drop_constraint("uq_cliente_user_estetica", "clientes", type_="unique")
    op.create_unique_constraint("clientes_email_key", "clientes", ["email"])
    op.create_unique_constraint("clientes_google_id_key", "clientes", ["google_id"])
    op.drop_index(op.f("ix_memberships_id"), table_name="memberships")
    op.drop_table("memberships")
