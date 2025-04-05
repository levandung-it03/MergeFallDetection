from sqlalchemy.orm import Session

from app.app_sql.models import User, Account


def save(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def findById(db: Session, userId: int):
    return db.query(User).filter(User.id == userId).first()

def findByAccountId(db: Session, accountId: int):
    return db.query(User).filter(User.account_id == accountId).first()

def findByAccountEmail(db: Session, email: str):
    return db.query(User).join(Account).filter(Account.email == email).first()

def deleteById(db: Session, userId: int):
    db.delete(findById(db, userId))
    db.commit()

def updateById(db: Session, user: User):
    raw = db.query(User).filter(User.id == user.id).first()
    if raw is None:
        return None
    raw.account_id = user.account_id
    raw.full_name = user.full_name
    raw.esp32_url = user.esp32_url
    db.commit()
    db.refresh(raw)
    return user

def findAll(db: Session):
    return db.query(User).all()

def findAllByUserId(db: Session, userId: int):
    return db.query(User).filter(User.id == userId).all()

def saveAll(db: Session, users: list[User]):
    for user in users:
        db.add(user)
    db.commit()
    for user in users:
        db.refresh(user)
    return users

def countAll(db: Session):
    return db.query(User).count()

