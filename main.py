from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File, Cookie
from sqlalchemy.orm import Session
from database import SessionLocal, User, Flower, Purchase
from schemas import UserCreate, FlowerCreate, PurchaseCreate  # Импортируйте модели Pydantic
from auth import create_access_token, verify_password, get_password_hash, \
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM  # Импортируйте функции
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"status": "200 OK"}


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/profile")
async def get_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = db.query(User).filter(User.username == user_data["sub"]).first()
    return {"username": user.username, "email": user.email, "full_name": user.full_name}


@app.get("/flowers")
async def get_flowers(db: Session = Depends(get_db)):
    return db.query(Flower).all()


@app.post("/flowers")
async def add_flower(flower: FlowerCreate, db: Session = Depends(get_db)):
    db_flower = Flower(name=flower.name, price=flower.price)
    db.add(db_flower)
    db.commit()
    db.refresh(db_flower)
    return {"id": db_flower.id}


@app.patch("/flowers/{flower_id}")
async def update_flower(flower_id: int, flower: FlowerCreate, db: Session = Depends(get_db)):
    db_flower = db.query(Flower).filter(Flower.id == flower_id).first()
    if not db_flower:
        raise HTTPException(status_code=404, detail="Flower not found")

    db_flower.name = flower.name
    db_flower.price = flower.price
    db.commit()
    return {"status": "200 OK"}


@app.delete("/flowers/{flower_id}")
async def delete_flower(flower_id: int, db: Session = Depends(get_db)):
    db_flower = db.query(Flower).filter(Flower.id == flower_id).first()
    if not db_flower:
        raise HTTPException(status_code=404, detail="Flower not found")

    db.delete(db_flower)
    db.commit()
    return {"status": "200 OK"}


@app.get("/cart/items")
async def get_cart_items(cart: str = Cookie(None), db: Session = Depends(get_db)):
    items = cart.split(",") if cart else []
    flowers = db.query(Flower).filter(Flower.id.in_(map(int, items))).all()
    total_price = sum(flower.price for flower in flowers)
    return {"items": flowers, "total_price": total_price}


@app.post("/purchased")
async def purchase_items(token: str = Depends(oauth2_scheme), cart: str = Cookie(None), db: Session = Depends(get_db)):
    user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = db.query(User).filter(User.username == user_data["sub"]).first()
    items = cart.split(",") if cart else []
    for flower_id in items:
        purchase = Purchase(user_id=user.id, flower_id=int(flower_id))
        db.add(purchase)
    db.commit()
    return {"status": "200 OK"}


@app.get("/purchased")
async def get_purchased_items(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = db.query(User).filter(User.username == user_data["sub"]).first()
    purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()
    return {"items": purchases}
