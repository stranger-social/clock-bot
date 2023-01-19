from passlib.context import CryptContext
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def check_admin(db):
    admin = db.query(models.User).filter(models.User.is_admin == True).first()
    if admin:
        return True
    else:
        return False

def create_admin(db, user):
    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict(), is_admin=True)
    db.add(new_user)
    db.commit()
    return new_user