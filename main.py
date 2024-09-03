from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import os
from api import router as api_router

load_dotenv()

__title__ = os.getenv('TITLE', 'API')
__contact_name__ = os.getenv('CONTACT_NAME', 'John Doe')
__contact_email__ = os.getenv('CONTACT_EMAIL', 'jd@go.com')

app = FastAPI(title=__title__,
              contact={"name": __contact_name__, "email": __contact_email__},
              version="1.0")

app.include_router(api_router, tags=["API"])

@app.get("/")
async def root(req: Request):
    docs_url = req.base_url.__str__() + "docs"
    return {"message": "", "docs_url": docs_url}


