from fastapi import APIRouter, Depends
from database import DBSession
import users.schemas as schemas
import users.crud as crud
from dependecies import get_db_session
import users.exceptions as exceptions

router = APIRouter()


@router.post("/user/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: DBSession = Depends(get_db_session)):
    if crud.get_user_by_login(db, user.login):
        raise exceptions.LoginTaken()

    db_user = crud.create_user(db, user)
    response = schemas.UserResponse(success=True, accessToken=db_user.accessToken)
    return response

@router.post("/user/login", response_model=schemas.UserResponse)
async def login_user(user: schemas.UserLogin, db: DBSession = Depends(get_db_session)):
    db_user = crud.checkPassword(db, user.login, user.password)

    if not(db_user):
        raise exceptions.IncorrectPassword()
    if not(crud.get_user_by_Deleted(db, user.login)):
        raise exceptions.UserBanned()

    response = schemas.UserResponse(success=True, accessToken=db_user.accessToken)
    return response

@router.post("/dogs/register", response_model=schemas.DogsUser)
async def create_dogsuser(user: schemas.DogsUserBase, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        raise exceptions.AdminNotTaken()
    db_user = crud.create_dogsuser(db, user)

    response = schemas.DogsUser(success=True, dogid=db_user.dogid, accessDogToken=db_user.accessToken)

    return response

@router.post("/dogs/task/create", response_model=schemas.CreateTaskResponse)
async def create_task(task: schemas.CreateTask, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, task.accessToken)):
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_DogId(db, task.dog_id)):
        raise exceptions.DogNotTaken()
    db_user = crud.create_task(db, task)

    response = schemas.CreateTaskResponse(success=True, task_id=db_user.id)
    return response

@router.post("/dogs/task/list", response_model=schemas.GetTasksResponse)
async def get_all_task(task: schemas.GetTasks, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, task.accessToken)):
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_DogId(db, task.dog_id)):
        raise exceptions.DogNotTaken()

    db_user = crud.get_tasks(db, task.dog_id)

    response = schemas.GetTasksResponse(success=True, tasks=db_user)
    return response

@router.post("/dogs/task/take", response_model=schemas.TakeTaskResponse)
async def take_task(task: schemas.TakeTask, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        raise exceptions.TaskNotTaken()
    if crud.get_taken_task(db, user.id, task.task_id):
        raise exceptions.TaskAlreadyTaken()

    db_user = crud.take_task(db, task)

    response = schemas.TakeTaskResponse(success=True)
    return response

@router.post("/dogs/task/response/give", response_model=schemas.TakeTaskResponse)
async def give_response_task(task: schemas.giveResponse, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        raise exceptions.TaskNotTaken()
    if not(crud.get_taken_task(db, user.id, task.task_id)):
        raise exceptions.UserNotTakenTask()

    crud.give_response(db, user.id, task)

    response = schemas.TakeTaskResponse(success=True)
    return response

@router.post("/dogs/task/response/list", response_model=schemas.GetResponsesResponse)
async def get_responses(task: schemas.TakeTask, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        raise exceptions.TaskNotTaken()
    if not(crud.is_creator_task(db, user.id, task.task_id)):
        raise exceptions.CreatorNotTaken()

    response = schemas.GetResponsesResponse(success=True, responses=crud.get_responses(db, task))
    return response

@router.post("/dogs/task/confirm", response_model=schemas.TakeTaskResponse)
async def confirm_task(task: schemas.ConfirmTask, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        raise exceptions.TaskNotTaken()
    if not(crud.is_creator_task(db, user.id, task.task_id)):
        raise exceptions.CreatorNotTaken()

    crud.confirm_task(db, task.task_id)

    response = schemas.TakeTaskResponse(success=True)
    return response

@router.post("/dogs/coordinates",response_model=schemas.CoordinatesResponse)
async def Сoordinates(user: schemas.Coordinates, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        raise exceptions.TokenNotTaken()
    db_user = schemas.CoordinatesResponse(dogs=crud.get_dogsuser_place(db, user.place))

    return db_user

@router.post("/dogs/characteristic",response_model=schemas.CharacteristicResponse)
async def Characteristic(user: schemas.Characteristic, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_DogId(db, user.dogid)):
        raise exceptions.DogNotTaken()
    db_user = schemas.CharacteristicResponse(success=True, charterictic=crud.get_dogsuser_Characteristic(db, user.dogid))

    return db_user

@router.post("/dogs/update", response_model=schemas.DogsUpdateResponse)
async def Update(user: schemas.DogsUpdate, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_DogToken(db, user.accessDogToken)):
        raise exceptions.DogTokenNotTaken()
    if not(crud.get_user_by_DogId(db, user.dogid)):
        raise exceptions.DogNotTaken()
    crud.get_dogsuser_update(db, user.dogid, user.coordinates)
    db_user = schemas.DogsUpdateResponse(success=True)

    return db_user

@router.post("/dogs/changestatus", response_model = schemas.DogChangeStatusResponse)
async def dog_change_status(user: schemas.DogChangeStatus, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        raise exceptions.DogTokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        raise exceptions.AdminNotTaken()
    if not(crud.get_user_by_DogId(db, user.dogid)):
        raise exceptions.DogNotTaken()
    crud.dog_status_update(db, user.dogid, user.delete)
    db_user = schemas.DogChangeStatusResponse(success=True)

    return db_user

@router.post("/user/changestatus", response_model = schemas.UserChangeStatusResponse)
async def user_change_status(user: schemas.UserChangeStatus, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        raise exceptions.DogTokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        raise exceptions.AdminNotTaken()
    check_user = crud.get_user_by_login(db, user.changed_user_login)
    if not(crud.get_user_by_login(db, user.changed_user_login)):
        raise exceptions.LoginTaken()

    crud.user_status_update(db, check_user, user.delete)
    db_user = schemas.UserChangeStatusResponse(success=True)

    return db_user


@router.post("/dogs/info", response_model = schemas.DogInfoResponse)
async def dog_info(user: schemas.DogInfo, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        raise exceptions.DogTokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        raise exceptions.AdminNotTaken()
    if not (crud.get_user_by_DogId(db, user.dog_id)):
        raise exceptions.DogNotTaken()

    db_user = crud.dog_info(db, user.dog_id)
    db_user = schemas.DogInfoResponse(success=True, lastsend=db_user.last_send, coordinates=db_user.coordinates)

    return db_user