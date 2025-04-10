from pydantic import BaseModel


class NewAccount(BaseModel):
    email: str
    password: str
    full_name: str
    esp32_url: str

class UpdateAccount(BaseModel):
    account_id: int
    full_name: str
    esp32_url: str

class AuthAccount(BaseModel):
    email: str
    password: str