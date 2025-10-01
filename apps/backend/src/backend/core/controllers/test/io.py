from pydantic import BaseModel

class TestInput(BaseModel):
    name: str

class TestOutput(BaseModel):
    message: str