from fastapi import FastAPI
from app.Api import Campaigns

app = FastAPI()
# @app.get("/health")

# def health():
# 	return{"status": "ok"}

app.include_router(Campaigns.router, prefix="/campaigns", tags=["Campaigns"])
