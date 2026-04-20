"""create persistence tables"""

from alembic import op
import sqlalchemy as sa


revision = "20260418_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "startup_projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("idea", sa.String(length=500), nullable=False),
        sa.Column("audience", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idea", "audience", name="uq_project_user_idea_audience"),
    )
    op.create_index(op.f("ix_startup_projects_id"), "startup_projects", ["id"], unique=False)
    op.create_index(
        op.f("ix_startup_projects_user_id"), "startup_projects", ["user_id"], unique=False
    )

    op.create_table(
        "generations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("startup_project_id", sa.Integer(), nullable=False),
        sa.Column("idea", sa.String(length=500), nullable=False),
        sa.Column("audience", sa.String(length=255), nullable=False),
        sa.Column("provider_used", sa.String(length=255), nullable=False),
        sa.Column("outputs", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["startup_project_id"], ["startup_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generations_id"), "generations", ["id"], unique=False)
    op.create_index(
        op.f("ix_generations_startup_project_id"),
        "generations",
        ["startup_project_id"],
        unique=False,
    )
    op.create_index(op.f("ix_generations_user_id"), "generations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_generations_user_id"), table_name="generations")
    op.drop_index(op.f("ix_generations_startup_project_id"), table_name="generations")
    op.drop_index(op.f("ix_generations_id"), table_name="generations")
    op.drop_table("generations")

    op.drop_index(op.f("ix_startup_projects_user_id"), table_name="startup_projects")
    op.drop_index(op.f("ix_startup_projects_id"), table_name="startup_projects")
    op.drop_table("startup_projects")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
