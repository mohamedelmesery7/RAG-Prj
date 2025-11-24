from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from Routes import base


app = FastAPI()

app.include_router(base.base_router)