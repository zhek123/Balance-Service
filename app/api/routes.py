from aiohttp import web
from datetime import datetime
from decimal import Decimal
from uuid import uuid4, UUID

from app.models import User, Transaction
from app.models.base import db

async def create_user(request):
    data = await request.json()
    async with db.transaction():
        new_user = await User.create(
            id=str(uuid4()),
            first_name=data['first_name'],
            last_name=data['last_name'],
            patronymic=data.get('patronymic'),
            age=data['age'],
            email=data['email'],
            password=data['password'],
            balance=Decimal('0.00')
        )
    return web.json_response({'id': str(new_user.id), 'name': new_user.first_name}, status=201)

async def add_transaction(request):
    data = await request.json()
    user_id_str = data['user_id']
    transaction_uuid_str = data['transaction_uuid']
    try:
        user_id = UUID(user_id_str)
    except ValueError as e:
        return web.json_response({'error': f'Invalid UUID format for user_id: {user_id_str}'}, status=400)
    try:
        transaction_uuid = UUID(transaction_uuid_str)
    except ValueError as e:
        return web.json_response({'error': f'Invalid UUID format for transaction_uuid: {transaction_uuid_str}'}, status=400)
    transaction_type = data['transaction_type']
    amount = Decimal(data['amount'])

    async with db.transaction():
        user = await User.query.where(User.id == str(user_id)).with_for_update().gino.first()
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)

        existing_transaction = await Transaction.query.where(
            Transaction.transaction_uuid == str(transaction_uuid)).gino.first()
        if existing_transaction:
            return web.json_response({'error': 'Transaction already processed'}, status=409)
        if transaction_type == 'WITHDRAW' and user.balance < amount:
            return web.json_response({'error': 'Insufficient funds'}, status=402)

        if transaction_type == 'WITHDRAW':
            user.balance -= amount
        elif transaction_type == 'DEPOSIT':
            user.balance += amount
        else:
            return web.json_response({'error': 'Invalid transaction type'}, status=400)

        new_transaction = await Transaction.create(
            id=str(uuid4()),
            user_id=str(user_id),
            transaction_type=transaction_type,
            amount=amount,
            resulting_balance=user.balance,
            transaction_uuid=str(transaction_uuid),
        )

        await user.update(balance=user.balance).apply()

    return web.json_response({
        'transaction_id': str(new_transaction.id),
        'resulting_balance': str(new_transaction.resulting_balance),
        'transaction_type': new_transaction.transaction_type
    }, status=200)

async def get_transaction(request):
    transaction_id = request.match_info['id']
    transaction = await Transaction.get(transaction_id)
    if not transaction:
        return web.json_response({'error': 'Transaction not found'}, status=404)

    return web.json_response({
        'id': str(transaction.id),
        'user_id': str(transaction.user_id),
        'transaction_type': transaction.transaction_type,
        'amount': str(transaction.amount),
        'created_at': transaction.created_at.isoformat(),
        'resulting_balance': str(transaction.resulting_balance)
    })

async def get_user_balance(request):
    user_id = request.match_info['id']
    date = request.query.get('date')

    if date:
        if date > datetime.now().isoformat():
            return web.json_response({'error': 'Date cannot be in the future'}, status=400)
        date = datetime.fromisoformat(date)
        transaction = await Transaction.query.where(
            Transaction.user_id == user_id).where(
            Transaction.created_at <= date).order_by(
            Transaction.created_at.desc()
        ).gino.first()
        if transaction:
            balance = transaction.resulting_balance
        else:
            return web.json_response({'error': 'No transactions found for the given date'}, status=404)
    else:
        user = await User.get(user_id)
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        balance = user.balance

    return web.json_response({'balance': str(balance)})

def add_routes(app):
    app.router.add_route('POST', '/v1/user', create_user, name='create_user')
    app.router.add_route('GET', '/v1/user/{id}/balance', get_user_balance, name='get_user_balance')
    app.router.add_route('POST', '/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', '/v1/transaction/{id}', get_transaction, name='get_transaction')
