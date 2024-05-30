from sqlalchemy.dialects.postgresql import UUID

from app.models.base import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(), primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    patronymic = db.Column(db.String(30), nullable=True)
    age = db.Column(db.Integer(), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    __table_args__ = (
        db.CheckConstraint('age > 18', name='age_minimum_requirement'),
        db.CheckConstraint('balance >= 0', name='balance_positive_requirement'),
    )
