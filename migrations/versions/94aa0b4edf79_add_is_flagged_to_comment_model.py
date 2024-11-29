"""Add is_flagged to Comment model

Revision ID: 94aa0b4edf79
Revises: e3cd0bdd04d1
Create Date: 2024-11-29 08:26:28.320024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94aa0b4edf79'
down_revision = 'e3cd0bdd04d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_flagged', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_column('is_flagged')

    # ### end Alembic commands ###