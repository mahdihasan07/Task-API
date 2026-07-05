from fastapi import FastAPI
from .routers import tasks, auth

app = FastAPI(title="Task Manager API")
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"status": "ok"}


