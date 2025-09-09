import secrets
import random

from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from models.user import User
from models.fish import Fish
from models.pond import Pond
from models.fishing_session import FishingSession

app = FastAPI(name="Knowledge Fishing API", version="0.1.0")


class PondCreate(BaseModel):
    name: str
    description: str
    topic: str


class FishCreate(BaseModel):
    question: str
    answer: str


last_user_id = 0
last_pond_id = 0
last_fish_id = 0

last_fishing_session_id = 0
token_to_user_id = dict()
user_id_to_user = dict()
pond_id_to_pond = dict()
fish_id_to_fish = dict()
fishing_session_id_to_fishing_session = dict()


def get_user_from_token(request: Request) -> User:
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='there is not token in cookies'
        )

    if token not in token_to_user_id.keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='this token isn`t exist'
        )

    return user_id_to_user[token_to_user_id[token]]


def get_pond_with_check_rights(pond_id: str, cur_user: User = Depends(get_user_from_token)) -> Pond:
    if pond_id not in pond_id_to_pond.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='there is not pond with this id'
        )

    pond = pond_id_to_pond.get(pond_id)
    if pond.user_id != cur_user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail='this pond does not belong to the current user'
        )

    return pond


def get_fish_with_check_rights(fish_id: str, cur_user: User = Depends(get_user_from_token)) -> Fish:
    if fish_id not in fish_id_to_fish.keys():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='there is not fish with this id'
        )

    fish = fish_id_to_fish.get(fish_id)
    pond_id = fish.pond_id
    try:
        pond = get_pond_with_check_rights(pond_id, cur_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error'
        )

    return fish


def update(fish: Fish):
    if fish.id not in fish_id_to_fish.keys():
        return
    if fish.next_review_date <= datetime.now():
        fish_id_to_fish[fish.id].status = 'ready'
    else:
        fish_id_to_fish[fish.id].status = 'not ready'
    return fish_id_to_fish[fish.id]


def get_fishes_by_pond_id(pond_id: str, fish_status: Optional[str] = None,
                          depth_level: Optional[int] = None) -> list[Fish]:
    fishes = []
    for fish in fish_id_to_fish.values():
        fish = update(fish)
        if ((fish.pond_id == pond_id and
                (fish_status is None or fish_status == fish.status)) and
                (depth_level is None or depth_level == fish.depth_level)):
            fishes.append(fish)

    return fishes


@app.get("/")
def start(request: Request, response: Response):
    global last_user_id

    token = request.cookies.get('access_token')
    if not token:
        token = secrets.token_hex(32)
        last_user_id += 1
        new_user = User()
        print("new_id =", new_user.id)
        user_id_to_user[new_user.id] = new_user  # db
        token_to_user_id[token] = new_user.id  # db
        response.set_cookie(
            key='access_token',
            value=token,
            httponly=True
        )

    # TODO: return EGOR`S files


@app.get("/ponds", response_model=list[Pond])
def get_ponds(cur_user: User = Depends(get_user_from_token)):
    user_ponds = []
    for pond in pond_id_to_pond.values():  # db
        if pond.user_id == cur_user.id:
            user_ponds.append(pond)

    return user_ponds


@app.post("/ponds", response_model=Pond)
def create_pond(cr_pond: PondCreate, cur_user: User = Depends(get_user_from_token)):
    global last_pond_id

    last_pond_id += 1
    new_pond = Pond(
        id=str(last_pond_id),
        user_id=str(cur_user.id),
        name=cr_pond.name,
        description=cr_pond.description,
        topic=cr_pond.topic,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    pond_id_to_pond[str(last_pond_id)] = new_pond

    return new_pond


@app.get("/ponds/{pond_id}", response_model=Pond)
def get_pond_by_pond_id(pond: Pond = Depends(get_pond_with_check_rights)):
    return pond


@app.delete("/ponds/{pond_id}")
def delete_pond(pond: Pond = Depends(get_pond_with_check_rights)):
    fishes = get_fishes_by_pond_id(pond.id)

    del pond_id_to_pond[pond.id]  # bd
    for fish in fishes:
        del fish_id_to_fish[fish.id]  # bd


@app.get("/ponds/{pond_id}/fishes", response_model=list[Fish])
def get_fishes(fish_status: Optional[str] = None, depth_level: Optional[int] = None,
               pond: Pond = Depends(get_pond_with_check_rights)):
    return get_fishes_by_pond_id(pond.id, fish_status, depth_level)


@app.post("/ponds/{pond_id}/fishes", response_model=Fish)
def create_fish(fish_data: FishCreate, pond: Pond = Depends(get_pond_with_check_rights)):
    global last_fish_id
    last_fish_id += 1
    new_fish = Fish(
        id=str(last_fish_id),
        pond_id=str(pond.id),
        question=fish_data.question,
        answer=fish_data.answer,
        next_review_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    fish_id_to_fish[str(last_fish_id)] = new_fish  # bd

    return new_fish


@app.get("/ponds/{pond_id}/start-fishing", response_model=Fish)
def get_fish_from_pond(pond: Pond = Depends(get_pond_with_check_rights)):
    fishes = get_fishes_by_pond_id(pond.id, fish_status='ready')
    if len(fishes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no one fish into this pond"
        )
    fish = random.choice(fishes)

    global last_fishing_session_id
    last_fishing_session_id += 1
    fishing_session_id_to_fishing_session[str(last_fishing_session_id)] = FishingSession(
        id=str(last_fishing_session_id),
        pond_id=str(pond.id),
        fish_id=str(fish.id)
    )
    user_id = pond.user_id
    user_id_to_user[user_id].cur_fishing_session_id = str(last_fishing_session_id)

    return fish


@app.put("/fishes/{fish_id}/caught", response_model=Fish)
def update_caught_fish(quality: int, fish: Fish = Depends(get_fish_with_check_rights)):
    pond_id = fish.pond_id
    user_id = pond_id_to_pond[pond_id].user_id
    fishing_session_id = user_id_to_user[user_id].cur_fishing_session_id

    if fishing_session_id not in fishing_session_id_to_fishing_session.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='this user hasn`t got running fishing session'
        )

    fishing_session = fishing_session_id_to_fishing_session[fishing_session_id]
    if fishing_session.fish_id != fish.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='fish in running fishing session doesn`t match with fish in request'
        )

    del fishing_session_id_to_fishing_session[fishing_session_id]

    if quality >= 3:
        if fish.repetitions == 0:
            fish.interval = 1
        elif fish.repetitions == 1:
            fish.interval = 6
        else:
            fish.interval = round(fish.interval * fish.ease_factor)
        fish.repetitions += 1
        fish.ease_factor = max(1.3, fish.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    else:
        fish.repetitions = 0
        fish.interval = 1
        fish.ease_factor = max(1.3, fish.ease_factor - 0.2)

    fish.next_review_date = datetime.now() + timedelta(days=fish.interval)
    if fish.repetitions == 0:
        fish.depth_level = 1
    elif fish.repetitions < 4:
        fish.depth_level = 2
    else:
        fish.depth_level = 3

    fish.updated_at = datetime.now()

    fish_id_to_fish[fish.id] = fish

    return update(fish)


@app.get("/fishes/{fish_id}", response_model=Fish)
def get_fish_by_id(fish: Fish = Depends(get_fish_with_check_rights)):
    return update(fish)


@app.put("/fishes/{fish_id}", response_model=Fish)
def change_fish(fish_data: FishCreate, fish: Fish = Depends(get_fish_with_check_rights)):
    fish_id_to_fish[fish.id].question = fish_data.question
    fish_id_to_fish[fish.id].answer = fish_data.answer
    return update(fish_id_to_fish[fish.id])


@app.delete("/fishes/{fish_id}")
def delete_fish(fish: Fish = Depends(get_fish_with_check_rights)):
    del fish_id_to_fish[fish.id]


@app.get("/fishing_sessions", response_model=FishingSession)
def get_cur_fishing_session(cur_user: User = Depends(get_user_from_token)):
    if cur_user.cur_fishing_session_id not in fishing_session_id_to_fishing_session.keys():
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='no fishing session is running now'
        )

    return fishing_session_id_to_fishing_session[cur_user.cur_fishing_session_id]
