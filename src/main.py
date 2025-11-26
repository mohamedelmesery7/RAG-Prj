from fastapi import FastAPI

from Routes import base
from Routes import data

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)