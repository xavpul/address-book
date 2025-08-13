"""Initial migration

Revision ID: 37c338698488
Revises:
Create Date: 2025-08-11 01:26:33.205435

"""

from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "37c338698488"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the table
    op.create_table(
        "address",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
                spatial_index=False,  # <-- suppress automatic index
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Create the spatial index only if it does not yet exist
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "idx_address_geom" not in {idx["name"] for idx in insp.get_indexes("address")}:
        op.create_index(
            "idx_address_geom",
            "address",
            ["geom"],
            unique=False,
            postgresql_using="gist",
        )

    # 3. Create the regular index on id
    op.create_index(op.f("ix_address_id"), "address", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_address_id"), table_name="address")
    op.drop_index("idx_address_geom", table_name="address", postgresql_using="gist")
    op.drop_table("address")

