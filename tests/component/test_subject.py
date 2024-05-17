import requests
from datetime import date

base_url = 'http://localhost:8001'
add_subject_url = f'{base_url}/add_subject'
get_subjects_url = f'{base_url}/subjects'
get_subject_by_id_url = f'{base_url}/get_subject_by_id'
delete_subject_url = f'{base_url}/delete_subject'

new_subject = {
    "id": 99,
    "subject_name": "Mathematics",
    "retake_date": "2024-05-14",
    "total_seats": 50,
    "remaining_seats": 10
}


def test_health_check():
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json() == {"message": "Service alive"}


def test_1_add_subject():
    response = requests.post(add_subject_url, json=new_subject)
    assert response.status_code == 200


def test_2_get_subjects():
    response = requests.get(get_subjects_url)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_3_get_subject_by_id():
    response = requests.get(f"{get_subject_by_id_url}/99")
    assert response.status_code == 200
    assert response.json()['id'] == 99


def test_4_delete_subject():
    delete_response = requests.delete(f"{delete_subject_url}/99")
    assert delete_response.status_code == 200

    response = requests.get(f"{get_subject_by_id_url}/99")
    assert response.status_code == 404
