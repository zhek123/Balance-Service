from datetime import datetime
import requests
import uuid
import random
import string

# Тесты работают с запущенным приложением, в текущей базе. Нужно создать клиент с фикстурами, асинхронные тесты. 
def generate_random_email():
    random_letters = ''.join(random.choices(string.ascii_lowercase, k=10))
    email = f"{random_letters}@example.com"
    return email

def assert_balance(user, expected_balance, date=None):
    url = f'http://localhost:8000/v1/user/{user["id"]}/balance'
    if date:
        url += f'?date={date}'
    balance_resp = requests.get(url)
    assert balance_resp.status_code == 200
    assert balance_resp.json()['balance'] == expected_balance


def test_api():
    user_resp = requests.post('http://localhost:8000/v1/user', json={
        'first_name': 'Petya',
        'last_name': 'Ivanov',
        'patronymic': 'Petrovich',
        'age': 30,
        'email': generate_random_email(),
        'password': 'securepassword123'
    })
    assert user_resp.status_code == 201
    user = user_resp.json()
    assert user['name'] == 'Petya'

    assert_balance(user, '0.00')

    txn = {
        'transaction_type': 'DEPOSIT',
        'amount': '100.0',
        'user_id': user['id'],
        'timestamp': datetime(2023, 1, 4).isoformat(),  # technical field to make tests possible
        'transaction_uuid': str(uuid.uuid4())
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '100.00')
    detail_resp = requests.get(f'http://localhost:8000/v1/transaction/{txn_resp.json()["transaction_id"]}')
    assert detail_resp.json()['transaction_type'] == 'DEPOSIT'
    assert detail_resp.json()['amount'] == '100.00'

    txn = {
        'transaction_type': 'WITHDRAW',
        'amount': '50.0',
        'user_id': user['id'],
        'timestamp': datetime(2023, 1, 5).isoformat(),  # technical field to make tests possible
        'transaction_uuid': str(uuid.uuid4())
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '50.00')
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 409  # transaction already processed

    txn = {
        'transaction_type': 'WITHDRAW',
        'amount': '60.0',
        'user_id': user['id'],
        'timestamp': datetime.utcnow().isoformat(),  # technical field to make tests possible
        'transaction_uuid': str(uuid.uuid4())
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 402  # insufficient funds
    assert_balance(user, '50.00')

    txn = {
        'transaction_type': 'WITHDRAW',
        'amount': '10.0',
        'user_id': user['id'],
        'timestamp': datetime(2023, 2, 5).isoformat(),  # technical field to make tests possible
        'transaction_uuid': str(uuid.uuid4())
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '40.00')

