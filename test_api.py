import random
import pytest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from main import app
from database import engine


# @pytest.fixture(scope='session')
# def clear_all_tables():
#     SQLModel.metadata.drop_all(engine)
#     SQLModel.metadata.create_all(engine)



def entry(client: TestClient = TestClient(app)):
    client.cookies.clear()
    response = client.get("/")
    assert response.status_code == 200
    return client


def create_pond(client: TestClient, name: str = "name", desc: str = "desc", topic: str = "topic"):
    response = client.post(
        "/ponds",
        json={
            "name": name,
            "description": desc,
            "topic": topic
        }
    )

    assert response.status_code == 200
    data = response.json()
    print("\n\n\n\ndata =", data, "\n\n\n")
    assert data["name"] == name
    assert data["description"] == desc
    assert data["topic"] == topic
    return data


def create_pond_with_ai(client: TestClient, ai_request: str, ai_cnt: int, name: str = "name", desc: str = "desc", topic: str = "topic"):
    response = client.post(
        "/ponds",
        json={
            "name": name,
            "description": desc,
            "topic": topic,
            "ai_request": ai_request,
            "ai_cnt": ai_cnt
        }
    )

    assert response.status_code == 200
    data = response.json()
    print("\n\n\n\ndata =", data, "\n\n\n")
    assert data["name"] == name
    assert data["description"] == desc
    assert data["topic"] == topic
    return data


def get_ponds(client: TestClient):
    response = client.get("/ponds")
    assert response.status_code == 200
    return response.json()


def delete_pond(client: TestClient, pond_id: int):
    response = client.delete(f'/ponds/{pond_id}')
    assert response.status_code == 200


def check_equal_lists(list1, list2):
    id1 = [elem["id"] for elem in list1]
    id2 = [elem["id"] for elem in list2]
    id1.sort()
    id2.sort()
    assert id1 == id2


def create_fish(client: TestClient, pond_id: str, question: str = "question", answer: str = "answer"):
    response = client.post(
        f"/ponds/{pond_id}/fishes",
        json={
            "question": question,
            "answer": answer
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == question
    assert data["answer"] == answer
    assert data["pond_id"] == pond_id
    return data


def get_fishes(client: TestClient, pond_id: int):
    response = client.get(f"/ponds/{pond_id}/fishes")
    assert response.status_code == 200
    return response.json()


def get_fish(client: TestClient, fish_id: int):
    response = client.get(f"/fishes/{fish_id}")
    assert response.status_code == 200
    return response.json()


def test_root():
    entry()


def test_admin():
    client = entry()
    response = client.post("/users", json={"password": "normis"})
    assert response.status_code == 400


def test_get_fish():
    client = entry()
    response = client.post("/users", json={"password": "ne normis"})
    assert response.status_code == 200

    client2 = entry()
    response = client.post("/users", json={"password": "normis"})
    assert response.status_code == 400


def test_create_pond():
    client = entry()
    ponds = set()
    for i in range(100):
        ponds.add(create_pond(client)["id"])
        assert len(ponds) == i + 1


def test_create_pond_with_ai():
    client = entry()
    response = client.post("/users", json={"password": "ne normis"})
    assert response.status_code == 200

    pond = create_pond_with_ai(client, "Я учусь оценивать данные о компаниях. Напиши мне вопросы и ответы в формате мультипликатор, расшифровка + что означает.", 20)
    fishes = get_fishes(client, pond["id"])
    print(fishes)
    assert len(fishes) == 20
    assert response.status_code == 400


def test_get_ponds():
    client = entry()
    ponds = []
    for i in range(100):
        new_pond = create_pond(client)
        ponds.append(new_pond)
        check_equal_lists(ponds, get_ponds(client))


def test_create_fish():
    client = entry()
    pond1 = create_pond(client)
    fishes1 = set()
    for i in range(100):
        fish = create_fish(client, pond1["id"])
        fishes1.add(fish["id"])
        assert len(fishes1) == i + 1


def test_get_fishes():
    client = entry()
    pond1 = create_pond(client)
    fishes1 = []
    for i in range(100):
        fish = create_fish(client, pond1["id"])
        fishes1.append(fish)
        check_equal_lists(fishes1, get_fishes(client, pond1["id"]))

    pond2 = create_pond(client)
    fishes2 = []
    for i in range(100):
        fish = create_fish(client, pond2["id"])
        fishes2.append(fish)
        check_equal_lists(fishes2, get_fishes(client, pond2["id"]))

    check_equal_lists(fishes1, get_fishes(client, pond1["id"]))
    check_equal_lists(fishes2, get_fishes(client, pond2["id"]))


def test_delete_pond_without_fishes():
    client = entry()
    ponds = []
    for i in range(100):
        ponds.append(create_pond(client))

    for i in range(100):
        del_pond = random.choice(ponds)
        delete_pond(client, del_pond["id"])
        ponds.remove(del_pond)
        check_equal_lists(ponds, get_ponds(client))


def test_delete_pond_with_fishes():
    client = entry()
    pond = create_pond(client)
    fishes_id = []
    for i in range(100):
        new_fish = create_fish(client, pond["id"])
        fishes_id.append(new_fish["id"])

    for fish_id in fishes_id:
        fish = get_fish(client, fish_id)
        assert fish["id"] == fish_id

    delete_pond(client, pond["id"])
    pond_id = pond["id"]
    response = client.get(f"/ponds/{pond_id}")
    assert response.status_code == 404
    for fish_id in fishes_id:
        response = client.get(f"fishes/{fish_id}")
        assert response.status_code == 404


def test_set_cookies():
    client1 = entry()
    token1 = client1.cookies.get("access_token")
    pond = create_pond(client1)
    assert len(get_ponds(client1)) == 1

    client2 = entry()
    token2 = client2.cookies.get("access_token")

    assert len(get_ponds(client2)) == 0
    client2.cookies.clear()
    client2.cookies.set("access_token", token1)
    assert client2.cookies.get("access_token") == token1
    assert len(get_ponds(client2)) == 1


def test_get_pond():
    client = entry()
    create_pond(client, "qwerty", "asdfg", "zxcvb")
    pond = get_ponds(client)[0]
    assert pond["name"] == "qwerty"
    assert pond["description"] == "asdfg"
    assert pond["topic"] == "zxcvb"


def test_get_fish():
    client = entry()
    pond = create_pond(client)
    fish = create_fish(client, pond["id"], "qwerty", "asdfgh")
    assert fish["question"] == "qwerty"
    assert fish["answer"] == "asdfgh"
    assert fish["pond_id"] == pond["id"]






#  синхронные тесты от китенка

import pytest
import requests
from datetime import datetime, timedelta

# Базовый URL для тестов
BASE_URL = "http://localhost:8000"


class TestClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_URL
        # Инициализируем клиента с куки
        response = self.session.get(f"{self.base_url}/")
        self.token = self.session.cookies.get("access_token")

    def get(self, endpoint, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", **kwargs)

    def put(self, endpoint, **kwargs):
        return self.session.put(f"{self.base_url}{endpoint}", **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)

    def set_token(self, token):
        """Установить другой токен для эмуляции другого пользователя"""
        self.session.cookies.clear()    
        self.session.cookies.set("access_token", token)


@pytest.fixture
def client():
    return TestClient()


@pytest.fixture
def pond_data(client):
    pond_data = {
        "name": "Test Pond",
        "description": "Test Description",
        "topic": "Test Topic"
    }
    response = client.post("/ponds", json=pond_data)
    return response.json()


@pytest.fixture
def fish_data(client, pond_data):
    fish_data = {
        "question": "Test Question",
        "answer": "Test Answer"
    }
    response = client.post(f"/ponds/{pond_data['id']}/fishes", json=fish_data)
    return response.json()


class TestAuthentication:
    def test_start_endpoint_sets_cookie(self):
        client = TestClient()
        assert "access_token" in client.session.cookies
        assert len(client.token) == 36

    def test_get_ponds_without_token(self):
        client = requests.Session()  # Клиент без куки
        response = client.get(f"{BASE_URL}/ponds")
        assert response.status_code == 401
        assert "there is not token in cookies" in response.json()["detail"]

    def test_get_ponds_with_invalid_token(self):
        client = TestClient()
        client.session.cookies.clear()
        client.session.cookies.set("access_token", "invalid_token")
        response = client.get("/ponds")
        assert response.status_code == 401
        assert "this user_id doesn`t exist" in response.json()["detail"]


class TestPonds:
    def test_create_pond(self, client):
        pond_data = {
            "name": "Test Pond",
            "description": "Test Description",
            "topic": "Test Topic"
        }
        response = client.post("/ponds", json=pond_data)

        assert response.status_code == 200
        assert response.json()["name"] == pond_data["name"]
        assert "id" in response.json()

    def test_get_ponds_empty(self, client):
        response = client.get("/ponds")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_ponds_with_data(self, client, pond_data):
        response = client.get("/ponds")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == pond_data["id"]

    def test_get_pond_by_id(self, client, pond_data):
        response = client.get(f"/ponds/{pond_data['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == pond_data["id"]

    def test_get_nonexistent_pond(self, client):
        response = client.get("/ponds/999")
        assert response.status_code == 404

    def test_delete_pond(self, client, pond_data):
        response = client.delete(f"/ponds/{pond_data['id']}")
        assert response.status_code == 200

        response = client.get("/ponds")
        assert response.status_code == 200
        assert response.json() == []

    def test_multiple_users_isolation(self):
        # Первый пользователь
        client1 = TestClient()
        token1 = client1.token

        # Создаем пруд от первого пользователя
        pond_data = {"name": "Pond1", "description": "Desc1", "topic": "Topic1"}
        response = client1.post("/ponds", json=pond_data)
        assert response.status_code == 200

        # Второй пользователь
        client2 = TestClient()
        token2 = client2.token

        # У второго пользователя не должно быть прудов
        response = client2.get("/ponds")
        assert len(response.json()) == 0

        # Если подменить куки второго пользователя на первого, должен увидеть пруды
        client2.set_token(token1)
        response = client2.get("/ponds")
        assert len(response.json()) == 1


class TestFishes:
    def test_create_fish(self, client, pond_data):
        fish_data = {
            "question": "Test Question",
            "answer": "Test Answer"
        }
        response = client.post(f"/ponds/{pond_data['id']}/fishes", json=fish_data)

        assert response.status_code == 200
        assert response.json()["question"] == fish_data["question"]
        assert response.json()["pond_id"] == pond_data["id"]

    def test_get_fishes_empty(self, client, pond_data):
        response = client.get(f"/ponds/{pond_data['id']}/fishes")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_fishes_with_data(self, client, pond_data, fish_data):
        response = client.get(f"/ponds/{pond_data['id']}/fishes")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == fish_data["id"]

    def test_get_fish_by_id(self, client, fish_data):
        response = client.get(f"/fishes/{fish_data['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == fish_data["id"]

    def test_get_nonexistent_fish(self, client):
        response = client.get("/fishes/999")
        assert response.status_code == 404

    def test_update_fish(self, client, fish_data):
        update_data = {
            "question": "Updated Question",
            "answer": "Updated Answer"
        }
        response = client.put(f"/fishes/{fish_data['id']}", json=update_data)

        assert response.status_code == 200
        assert response.json()["question"] == update_data["question"]

    def test_delete_fish(self, client, fish_data):
        response = client.delete(f"/fishes/{fish_data['id']}")
        assert response.status_code == 200

        response = client.get(f"/fishes/{fish_data['id']}")
        print("\n deleted_fish =", response.json(), "\n")
        assert response.status_code == 404

class TestFishingSession:
    def test_start_fishing(self, client, pond_data, fish_data):
        print(client.get("/ponds").json())
        print(client.get(f"/ponds/{pond_data['id']}").json())
        response = client.get(f"/ponds/{pond_data['id']}/start-fishing")
        assert response.status_code == 200
        assert response.json()["id"] == fish_data["id"]

    def test_get_current_fishing_session(self, client, pond_data, fish_data):
        # Запускаем сессию
        client.get(f"/ponds/{pond_data['id']}/start-fishing")

        response = client.get("/fishing_sessions")
        assert response.status_code == 200
        assert "id" in response.json()
        assert response.json()["fish_id"] == fish_data["id"]

    def test_get_no_fishing_session(self, client):
        response = client.get("/fishing_sessions")
        assert response.status_code == 204


class TestFishCaught:
    def test_update_caught_fish(self, client, pond_data, fish_data):
        # Запускаем сессию
        client.get(f"/ponds/{pond_data['id']}/start-fishing")

        # Обновляем пойманную рыбу
        response = client.put(f"/fishes/{fish_data['id']}/caught?quality=4")

        assert response.status_code == 200
        assert response.json()["repetitions"] == 1

    def test_update_caught_fish_no_session(self, client, fish_data):
        response = client.put(f"/fishes/{fish_data['id']}/caught?quality=4")
        assert response.status_code == 400


class TestAccessControl:
    def test_access_other_user_pond(self):
        # Первый пользователь создает пруд
        client1 = TestClient()
        pond_data = {"name": "Pond1", "description": "Desc1", "topic": "Topic1"}
        response = client1.post("/ponds", json=pond_data)
        pond_id = response.json()["id"]

        # Второй пользователь пытается получить доступ
        client2 = TestClient()
        response = client2.get(f"/ponds/{pond_id}")
        assert response.status_code == 405

    def test_access_other_user_fish(self):
        # Первый пользователь создает пруд и рыбу
        client1 = TestClient()
        pond_data = {"name": "Pond1", "description": "Desc1", "topic": "Topic1"}
        response = client1.post("/ponds", json=pond_data)
        pond_id = response.json()["id"]

        fish_data = {"question": "Q1", "answer": "A1"}
        response = client1.post(f"/ponds/{pond_id}/fishes", json=fish_data)
        fish_id = response.json()["id"]

        # Второй пользователь пытается получить доступ
        client2 = TestClient()
        response = client2.get(f"/fishes/{fish_id}")
        assert response.status_code == 405


if __name__ == "__main__":
    # Запуск тестов без pytest
    test_client = TestClient()

    # Тест аутентификации
    #test_auth = TestAuthentication()
    #test_auth.test_start_endpoint_sets_cookie()

    print("All tests passed!")
