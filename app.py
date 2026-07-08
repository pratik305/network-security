import sys
import os
import pymongo
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.constant.training_pipeline import (
    DATA_INGESTION_DATABASE_NAME,
    DATA_INGESTION_COLLECTION_NAME
)

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# MongoDB client
client     = pymongo.MongoClient(MONGO_DB_URL)
database   = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

# FastAPI app
app = FastAPI()

# CORS — allows browser access
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["authentication"])
async def index():
    return {"message": "Welcome to Network Security API. Visit /docs for endpoints."}


@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful!")
    except Exception as e:
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)