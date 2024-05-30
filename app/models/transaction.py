from sqlalchemy import Enum, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(UUID(), primary_key=True)
    user_id = db.Column(UUID(), db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    transaction_type = db.Column(Enum('DEPOSIT', 'WITHDRAW', name='transaction_types'), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True, default=func.now())
    resulting_balance = db.Column(db.Numeric(precision=10, scale=2), nullable=False, index=True)
    transaction_uuid = db.Column(UUID(), unique=True, nullable=False)

    __table_args__ = (
        db.CheckConstraint('resulting_balance >= 0', name='resulting_balance_positive'),
        db.CheckConstraint('amount > 0', name='amount_positive'),
    )
