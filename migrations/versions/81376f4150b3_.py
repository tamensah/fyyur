"""empty message

Revision ID: 81376f4150b3
Revises: 525db600c4ce
Create Date: 2022-08-20 19:57:11.334867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81376f4150b3'
down_revision = '525db600c4ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('Artist', 'website')
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Venue', 'website_link')
    op.add_column('Artist', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###