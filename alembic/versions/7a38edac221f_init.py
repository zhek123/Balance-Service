"""Init

Revision ID: 7a38edac221f
Revises: 
Create Date: 2024-05-30 20:36:47.630170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7a38edac221f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=30), nullable=False),
    sa.Column('last_name', sa.String(length=30), nullable=False),
    sa.Column('patronymic', sa.String(length=30), nullable=True),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.CheckConstraint('age > 18', name='age_minimum_requirement'),
    sa.CheckConstraint('balance >= 0', name='balance_positive_requirement'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('transactions',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=False),
    sa.Column('transaction_type', sa.Enum('DEPOSIT', 'WITHDRAW', name='transaction_types'), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('resulting_balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('transaction_uuid', postgresql.UUID(), nullable=False),
    sa.CheckConstraint('amount > 0', name='amount_positive'),
    sa.CheckConstraint('resulting_balance >= 0', name='resulting_balance_positive'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_uuid')
    )
    op.create_index(op.f('ix_transactions_created_at'), 'transactions', ['created_at'], unique=False)
    op.create_index(op.f('ix_transactions_resulting_balance'), 'transactions', ['resulting_balance'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_resulting_balance'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_created_at'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_table('users')
    # ### end Alembic commands ###
