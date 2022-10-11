"""Add deleted_date

Revision ID: 1e22e78e9613
Revises: ed7fbb8da1ab
Create Date: 2022-10-11 13:05:03.146153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e22e78e9613'
down_revision = 'ed7fbb8da1ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('date_deleted', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'date_deleted')
    # ### end Alembic commands ###
