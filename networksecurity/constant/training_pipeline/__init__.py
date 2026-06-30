import os
import sys
import pandas as pd
import numpy as np

# common constants
TARGET_COLUMN = "Result"
PIPELINE_NAME = "NetworkSecurity"
ARTIFACT_DIR = "Artifacts"
FILE_NAME = "phishing.csv"
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME ="test.csv"

# Data Ingestion constants
DATA_INGESTION_COLLECTION_NAME = "network_data"
DATA_INGESTION_DATABASE_NAME = "phishing"
DATA_INGESTION_DIR_NAME = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_INGESTED_DIR = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO  = 0.2

# Data Validation constants
DATA_VALIDATION_DIR_NAME = "data_validation"
DATA_VALIDATION_VALID_DIR = "validated"
DATA_VALIDATION_INVALID_DIR = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME = "report.yaml"

# Schema file path
SCHEMA_FILE_PATH = os.path.join("data_schema", "schema.yaml")

# Data Transformation constants
DATA_TRANSFORMATION_DIR_NAME = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR = "transformed_object"
DATA_TRANSFORMATION_TRAIN_FILE_PATH = "train.npy"
DATA_TRANSFORMATION_TEST_FILE_PATH = "test.npy"

PREPROCESSING_OBJECT_FILE_NAME = "preprocessing.pkl"

# KNN Imputer parameters — used to handle missing values
DATA_TRANSFORMATION_IMPUTER_PARAMS = {
    "missing_values": np.nan,
    "n_neighbors": 3,
    "weights": "uniform",
}

