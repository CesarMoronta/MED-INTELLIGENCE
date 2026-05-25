from app import app
client = app.test_client()
with client.session_transaction() as sess:
    sess['user'] = {'id': 1, 'role': 'admin', 'username': 'admin'}
response = client.get('/api/records')
print(response.status_code)
print(response.data.decode('utf-8')[:200])
response2 = client.get('/api/clinical_history')
print(response2.status_code)
print(response2.data.decode('utf-8')[:200])
