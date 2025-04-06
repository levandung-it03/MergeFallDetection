from sqlalchemy.orm import Session

from app.app_sql.models import Account, User


def save(db: Session, account: Account):
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def findById(db: Session, accountId: int):
    return db.query(Account).filter(Account.id == accountId).first()

def findByUserUserId(db: Session, userId: int):
    return db.query(Account).join(User).filter(User.id == userId).first()

def findByEmail(db: Session, email: str):
    return db.query(Account).filter(Account.email == email).first()

def deleteById(db: Session, accountId: int):
    db.delete(findById(db, accountId))
    db.commit()

def updateById(db: Session, account: Account):
    raw = db.query(Account).filter(Account.id == account.id).first()
    if raw is None:
        return None
    raw.email = account.email
    raw.password = account.password
    db.commit()
    db.refresh(raw)
    return account

def findAll(db: Session):
    return db.query(Account).all()

def findAllByAccountId(db: Session, accountId: int):
    return db.query(Account).filter(Account.id == accountId).all()

def saveAll(db: Session, accounts: list[Account]):
    for account in accounts:
        db.add(account)
    db.commit()
    for account in accounts:
        db.refresh(account)
    return accounts

def countAll(db: Session):
    return db.query(Account).count()