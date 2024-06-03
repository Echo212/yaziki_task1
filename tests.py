import json
import pytest
from webtest import TestApp
from main import application


@pytest.fixture
def app():
    return TestApp(application)


def test_get_current_time(app):
    response = app.get('/')
    assert response.status_code == 200
    assert 'Current time in GMT' in response.text

    response = app.get('/Europe/Moscow')
    assert response.status_code == 200
    assert 'Current time in Europe/Moscow' in response.text

    response = app.get('/Invalid/Timezone')
    assert response.status_code == 200
    assert 'Unknown timezone' in response.text


def test_convert_time(app):
    data = {
        "date": "12.20.2021 22:21:05",
        "tz": "EST",
        "target_tz": "Europe/Moscow"
    }
    response = app.post('/api/v1/convert',
                        params=json.dumps(data),
                        headers={'Content-Type': 'application/json'},
                        expect_errors=True)
    assert response.status_code == 200
    print(f'\nFrom test_convert_time: type(response)={type(response)}, response={response}\n')
    response_data = response.json
    assert 'converted_time' in response_data


def test_convert_time_invalid_tz(app):
    data = {
        "date": "12.20.2021 22:21:05",
        "tz": "INVALID",
        "target_tz": "Europe/Moscow"
    }
    response = app.post('/api/v1/convert',
                        params=json.dumps(data),
                        headers={'Content-Type': 'application/json'},
                        expect_errors=True)
    assert response.status_code == 400
    response_data = response.json
    assert 'error' in response_data


def test_date_difference(app):
    data = {
        "first_date": "12.06.2024 22:21:05",
        "first_tz": "EST",
        "second_date": "12:30pm 2024-02-01",
        "second_tz": "Europe/Moscow"
    }
    response = app.post('/api/v1/datediff', params=json.dumps(data), headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    response_data = response.json
    assert 'diff_in_seconds' in response_data


def test_date_difference_invalid_tz(app):
    data = {
        "first_date": "12.06.2024 22:21:05",
        "first_tz": "INVALID",
        "second_date": "12:30pm 2024-02-01",
        "second_tz": "Europe/Moscow"
    }
    response = app.post('/api/v1/datediff',
                        params=json.dumps(data),
                        headers={'Content-Type': 'application/json'},
                        expect_errors=True)
    assert response.status_code == 400
    response_data = response.json
    assert 'error' in response_data
