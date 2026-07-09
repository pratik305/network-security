import sys
import os
import pymongo
import uvicorn
import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constant.training_pipeline import (
    DATA_INGESTION_DATABASE_NAME,
    DATA_INGESTION_COLLECTION_NAME
)

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

client     = pymongo.MongoClient(MONGO_DB_URL)
database   = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

# FastAPI app
app = FastAPI()

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 templates
templates = Jinja2Templates(directory="./templates")


@app.get("/", tags=["authentication"])
async def index():
    return {"message": "Welcome to Network Security API. Visit /docs for Swagger UI."}


@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful!")
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        # Step 1: Read uploaded CSV
        df = pd.read_csv(file.file)

        # Step 2: Load preprocessing pipeline
        preprocessor = load_object("final_model/preprocessing.pkl")

        # Step 3: Load trained model
        final_model  = load_object("final_model/model.pkl")

        # Step 4: Wrap in NetworkModel and predict
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        y_pred        = network_model.predict(df)

        # Step 5: Add predictions to dataframe
        df["predicted_column"] = y_pred
        print(df["predicted_column"])

        # Step 6: Save output CSV
        os.makedirs("prediction_output", exist_ok=True)
        df.to_csv("prediction_output/output.csv", index=False)

        # Step 7: Display as HTML table
        table_html = df.to_html(classes="table table-striped")
        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={"table": table_html}
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)