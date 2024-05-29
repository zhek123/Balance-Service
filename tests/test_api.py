from datetime import datetime
import requests
import uuid


def assert_balance(user, expected_balance, date=None):
    url = f'http://localhost:8000/v1/user/{user["id"]}'
    if date:
        url += f'?date={date}'
    balance_resp = requests.get(url)
    assert balance_resp.status_code == 200
    assert balance_resp.json()['balance'] == expected_balance



def test_api():
    user_resp = requests.post('http://localhost:8000/v1/user', json={
        'name': 'petya'
    })

    assert user_resp.status_code == 201
    user = user_resp.json()
    assert user['id'] > 0
    assert user['name'] == 'petya'

    assert_balance(user, '0.00')

    txn = {
        'uid': str(uuid.uuid4()),
        'type': 'DEPOSIT',
        'amount': '100.0',
        'user_id': user['id'],
        'timestamp': datetime(2023, 1, 4).isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '100.00')

    detail_resp = requests.get(f'http://localhost:8000/v1/transaction/{txn["uid"]}')
    assert detail_resp.json()['type'] == 'DEPOSIT'
    assert detail_resp.json()['amount'] == '100.00'

    txn = {
        'uid': str(uuid.uuid4()),
        'type': 'WITHDRAW',
        'amount': '50.0',
        'user_id': user['id'],
        'timestamp': datetime(2023, 1, 5).isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '50.00')


    txn = {
        'uid': str(uuid.uuid4()),
        'type': 'WITHDRAW',
        'amount': '60.0',
        'user_id': user['id'],
        'timestamp': datetime.utcnow().isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 402  # insufficient funds
    assert_balance(user, '50.00')

    txn = {
        'uid': str(uuid.uuid4()),
        'type': 'WITHDRAW',
        'amount': '10.0',
        'user_id': user['id'],
        'timestamp': datetime(2023, 2, 5).isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post('http://localhost:8000/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '40.00')

    assert_balance(user, '50.00', date='2023-01-30T00:00:00.00000000')
