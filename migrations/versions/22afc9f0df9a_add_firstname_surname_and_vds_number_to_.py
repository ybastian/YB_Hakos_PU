"""Add firstname, surname and vds_number to Users

Revision ID: 22afc9f0df9a
Revises: c494cc8daa7c
Create Date: 2024-09-28 18:55:22.495647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22afc9f0df9a'
down_revision = 'c494cc8daa7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.alter_column(column_name='groupname', new_column_name='name')

    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column(column_name='rolename', new_column_name='name')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(column_name='username', new_column_name='name')
        batch_op.add_column(sa.Column('surname', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('firstname', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('vds_number', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(column_name='name', new_column_name='username')
        batch_op.drop_column('vds_number')
        batch_op.drop_column('firstname')
        batch_op.drop_column('surname')

    with op.batch_alter_table('role', schema=None) as batch_op:
        batch_op.alter_column(column_name='name', new_column_name='rolename')

    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.alter_column(column_name='name', new_column_name='groupname')


    # ### end Alembic commands ###