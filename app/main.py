from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware # 1. Bunu import et

# ARTIK BU SATIRA İHTİYACIMIZ YOK, ALEMBIC KULLANACAĞIZ!
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Tüm HTTP metotlarına (GET, POST, PUT, DELETE) izin ver
    allow_headers=["*"], # Tüm header bilgilerine izin ver
)

# Router'ları uygulamaya dahil et
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router) # auth router eklendi
app.include_router(vote.router) # vote router eklendi
app.include_router(post.router)


@app.get("/")
def root():
    return {"message": "API Hazır!"}