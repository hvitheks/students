import requests

base_url = 'http://localhost:8000'
register_url = f'{base_url}/register'
login_url = f'{base_url}/login'

new_student = {
    "name": "John Doe",
    "login": "john_doe",
    "password": "password123"
}

def test_health_check():
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Service alive"}


def test_login_student():
    response = requests.post(login_url, json={"login": new_student['login'], "password": new_student['password']})
    assert response.status_code == 200
    assert 'id' in response.json()
    assert response.json()['name'] == new_student['name']
