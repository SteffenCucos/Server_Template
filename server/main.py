import uvicorn
from api.v1.api import api_router

from fastapi import FastAPI

from config import config

app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    host = config.network.host
    port = config.network.port

    uvicorn.run(app, port=port, host=host)