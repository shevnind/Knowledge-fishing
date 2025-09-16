import json
import secrets
import random
import hashlib

from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, TYPE_CHECKING
from sqlmodel import Session, select

from models.user import User
from models.fish import Fish
from models.pond import Pond
from models.fishing_session import FishingSession
from database import engine
from ai import ai_chatbot


app = FastAPI(name="Knowledge Fishing API", version="0.1.0")

hash_password = "e419d9ddeb9c3c1f340d5498acad9abb1ae7a037"


class PondCreate(BaseModel):
    name: str
    description: str
    topic: str
    ai_request: Optional[str]
    ai_cnt: int = 20


class FishCreate(BaseModel):
    question: str
    answer: str


def get_user_from_token(request: Request) -> User:
    user_id = request.cookies.get('access_token')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='there is not token in cookies'
        )

    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='this user_id doesn`t exist'
            )

    return user


def get_pond_with_check_rights(pond_id: str, cur_user: User = Depends(get_user_from_token)) -> Pond:
    with Session(engine) as session:
        pond = session.get(Pond, pond_id)
        if not pond:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='there is not pond with this id'
            )
        
        if pond.user_id != cur_user.id:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail='this pond does not belong to the current user'
            )

    return pond


def get_fish_with_check_rights(fish_id: str, cur_user: User = Depends(get_user_from_token)) -> Fish:
    with Session(engine) as session:
        fish = session.get(Fish, fish_id)
        print("find fish:", fish)
        if not fish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='there is not fish with this id'
            )

        pond = fish.pond
        if pond.user_id != cur_user.id:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail='this pond does not belong to the current user'
            )

    return fish


def update(fish: Fish):
    with Session(engine) as session:
        fish = session.get(Fish, fish.id)
        if fish.next_review_date <= datetime.now():
            fish.status = 'ready'
        else:
            fish.status = 'not ready'
        session.commit()
        session.refresh(fish)
    
    return fish


def get_fishes_by_pond_id(pond_id: str, fish_status: Optional[str] = None,
                          depth_level: Optional[int] = None) -> list[Fish]:
    with Session(engine) as session:
        fish_select = select(Fish)
        fish_select = fish_select.where(Fish.pond_id == pond_id)
        if fish_status is not None:
            fish_select = fish_select.where(Fish.status == fish_status)
        if depth_level is not None:
            fish_select = fish_select.where(Fish.next_review_date <= datetime.now())
        result = session.execute(fish_select)
        fishes = result.scalars().all()

    return fishes


def correct(s: str):
    st = 0
    while st < len(s) and s[st] != '{':
        st += 1

    fin = len(s) - 1
    while fin >= 0 and s[fin] != '}':
        fin -= 1

    if st > fin:
        return ''
    else:
        return s[st:fin + 1]


@app.get("/")
def start(request: Request, response: Response):
    user_id = request.cookies.get('access_token')
    if not user_id:

        with Session(engine) as session:
            new_user = User()

            session.add(new_user)
            session.commit()

            response.set_cookie(
                key='access_token',
                value=new_user.id,
                httponly=True
            )

    # TODO: return EGOR`S files


class Password(BaseModel):
    password: str


@app.post("/users")
def start_to_be_admin(p: Password, user: User = Depends(get_user_from_token)):
    h = hashlib.sha1(p.password.encode('utf-8'))
    if hash_password == h.hexdigest():
        with Session(engine) as session:
            user = session.get(User, user.id)
            user.admin = True
            session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='incorrect password'
        )


@app.get("/ponds", response_model=list[Pond])
def get_ponds(cur_user: User = Depends(get_user_from_token)):
    with Session(engine) as session:
        cur_user = session.get(User, cur_user.id)
        session.refresh(cur_user, attribute_names=['ponds'])
    
    return cur_user.ponds


@app.post("/ponds", response_model=Pond)
def create_pond(cr_pond: PondCreate, cur_user: User = Depends(get_user_from_token)):
    new_pond = Pond(
        user_id=str(cur_user.id),
        name=cr_pond.name,
        description=cr_pond.description,
        topic=cr_pond.topic,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    with Session(engine) as session:
        session.add(new_pond)
        session.commit()
        session.refresh(new_pond)

    print(cr_pond.ai_request, cur_user.admin)

    if cr_pond.ai_request is not None and cur_user.admin:
        request = 'Верни только пары вопрос-ответ без форматирования и другого текста. ' + cr_pond.ai_request + " Верни данные в следующем формате: набор из " + f'{cr_pond.ai_cnt}' + 'пар строк в формате {"question1": "answer1", "question2": "answer2", ...}. Длина вопросов и ответов не должна превышать 1000 символов. Верни только вопросы и ответы без форматирования и другого текста'
        print("\nrequest =", request)
        response = ai_chatbot.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "user", "content": request},
            ],
        )
        resp = response.choices[0].message.content
        resp = correct(resp)
        print("first answer =", resp, "\n", type(resp))

        cnt = 0
        while len(resp) == 0 and cnt < 2:
            response = ai_chatbot.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=[
                    {"role": "user", "content": request},
                ],
            )
            resp = response.choices[0].message.content
            resp = correct(resp)
            print("answer =", resp, "\n")
            cnt += 1

        if len(resp) == 0:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='can`t get response from ai chatbot'
            )
        
        new_fishes = json.loads(resp)

        for fish in new_fishes.items():
            create_fish(FishCreate(question=fish[0], answer=fish[1]), new_pond)

    return new_pond



@app.get("/ponds/{pond_id}", response_model=Pond)
def get_pond_by_pond_id(pond: Pond = Depends(get_pond_with_check_rights)):
    return pond


@app.delete("/ponds/{pond_id}")
def delete_pond(pond: Pond = Depends(get_pond_with_check_rights)):
    with Session(engine) as session:
        pond = session.get(Pond, pond.id)
        fishes = pond.fishes
        for fish in fishes:
            session.delete(fish)
        session.delete(pond)
        session.commit()


@app.get("/ponds/{pond_id}/fishes", response_model=list[Fish])
def get_fishes(fish_status: Optional[str] = None, depth_level: Optional[int] = None,
               pond: Pond = Depends(get_pond_with_check_rights)):
    return get_fishes_by_pond_id(pond.id, fish_status, depth_level)


@app.post("/ponds/{pond_id}/fishes", response_model=Fish)
def create_fish(fish_data: FishCreate, pond: Pond = Depends(get_pond_with_check_rights)):
    new_fish = Fish(
        pond_id=str(pond.id),
        question=fish_data.question,
        answer=fish_data.answer,
        next_review_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    with Session(engine) as session:
        session.add(new_fish)
        session.commit()
        session.refresh(new_fish)

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

    new_fishing_session = FishingSession(
        pond_id=str(pond.id),
        fish_id=str(fish.id)
    )
    with Session(engine) as session:
        session.add(new_fishing_session)
        session.commit()
        session.refresh(new_fishing_session)
        
        pond = session.get(Pond, pond.id)
        user = pond.user
        user.cur_fishing_session_id = new_fishing_session.id
        session.commit()

    return fish


@app.put("/fishes/{fish_id}/caught", response_model=Fish)
def update_caught_fish(quality: int, fish: Fish = Depends(get_fish_with_check_rights)):
    with Session(engine) as session:
        fish = session.get(Fish, fish.id)
        pond = fish.pond
        user = pond.user

        if user.cur_fishing_session_id == "-1":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='this user hasn`t got running fishing session'
            )
        
        fishing_session = user.fishing_session

        if fishing_session.fish_id != fish.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='fish in running fishing session doesn`t match with fish in request'
            )

        user.cur_fishing_session_id = "-1"
        session.commit()
        session.delete(fishing_session)
        session.commit()

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

        session.commit()
        session.refresh(fish)

    return update(fish)


@app.get("/fishes/{fish_id}", response_model=Fish)
def get_fish_by_id(fish: Fish = Depends(get_fish_with_check_rights)):
    return update(fish)


@app.put("/fishes/{fish_id}", response_model=Fish)
def change_fish(fish_data: FishCreate, fish: Fish = Depends(get_fish_with_check_rights)):
    with Session(engine) as session:
        fish = session.get(Fish, fish.id)
        fish.question = fish_data.question
        fish.answer = fish_data.answer
        session.commit()
        session.refresh(fish)

    return update(fish)


@app.delete("/fishes/{fish_id}")
def delete_fish(fish: Fish = Depends(get_fish_with_check_rights)):
    with Session(engine) as session:
        session.delete(fish)
        session.commit()


@app.get("/fishing_sessions", response_model=FishingSession)
def get_cur_fishing_session(cur_user: User = Depends(get_user_from_token)):
    with Session(engine) as session:
        cur_user = session.get(User, cur_user.id)
        # print("\nuser =", cur_user, "\n")
        if cur_user.cur_fishing_session_id == "-1":
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail='no fishing session is running now'
            )
        return cur_user.fishing_session
