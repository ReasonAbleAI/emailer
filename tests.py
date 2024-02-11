import pytest
from app import app, db
from models import User

@pytest.fixture(scope='module')
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.create_all()

    with app.test_client() as client:
        yield client

    db.session.remove()
    db.drop_all()

def test_create_user(client):
    response = client.post('/users', data={
        'username': 'testuser',
        'email': 'testuser@example.com'
    })

    assert response.status_code == 200
    assert b'User created successfully!' in response.data

    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'testuser@example.com'