from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import os
from api import router as api_router
from loguru import logger
import sys
import time

logger.remove()
logger.add(sys.stdout, format="{time}::{level} --- {message}", level="TRACE")

load_dotenv()

__title__ = os.getenv('TITLE', 'API')
__contact_name__ = os.getenv('CONTACT_NAME', 'John Doe')
__contact_email__ = os.getenv('CONTACT_EMAIL', 'jd@go.com')

app = FastAPI(title=__title__,
              contact={"name": __contact_name__, "email": __contact_email__},
              version="1.0")

app.include_router(api_router, tags=["API"])

@app.middleware("http")
async def befor_after(request: Request, call_next):
    # ref: https://fastapi.tiangolo.com/tutorial/middleware/?h=before
    start_time = time.perf_counter()
    msg = f"{request.method} {request.url}"
    # logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.trace(f"{msg} : {response.status_code} : {process_time:.2f}s")
    return response

@app.get("/")
async def root(req: Request):
    docs_url = req.base_url.__str__() + "docs"
    return {"message": "", "docs_url": docs_url}


logger.trace("App Starting")
