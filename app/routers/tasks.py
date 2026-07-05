from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from .. import models, schemas, database, auth
import os

router = APIRouter(prefix="/tasks", tags=['tasks'])
oauth2_schemae = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str=Depends(oauth2_schemae), db: Session=Depends(database.get_db)):
    try:
        payload = jwt.decoder(token, os.getenv("SECRET_KEY"), algorithm=[os.getenv("ALGORITHM")])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).ffilter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.post("/", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session=Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    new_task = models.Task(**task.dict(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=list[schemas.TaskOut])
def list_tasks(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Task).filter(models.Task.owner_id == currnet_user.id).all()

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_update: schemas.TaskCreate, db: Session=Depends(database.get_db), current_user: models.User=Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id==task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = task_update.title
    task.description = task_update.description
    db.commit()
    db.refresh(task)

    return task

@router.delete("'/{task_id}")
def delete_task(task_id: int, db: Session=Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == Current_user.id).filter()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

