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
