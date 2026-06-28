import os
import sys
import json
import certifi
import pandas as pd
import numpy as np
import pymongo
from dotenv import load_dotenv
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Load environment variables
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# SSL certificate for secure MongoDB connection
ca = certifi.where()


class NetworkDataExtract:
    """ETL Pipeline: CSV → JSON → MongoDB"""

    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_converter(self, file_path):
        """Read CSV file and convert each row to a JSON record"""
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)

            # Convert DataFrame to list of JSON records (key-value pairs per row)
            records = json.loads(data.to_json(orient="records"))
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        """Insert JSON records into MongoDB Atlas"""
        try:
            self.database = database
            self.collection = collection
            self.records = records

            # Connect to MongoDB
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)

            # Select database and collection
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]

            # Insert all records
            self.collection.insert_many(self.records)

            return len(self.records)

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# Run ETL pipeline
if __name__ == "__main__":
    # Config
    FILE_PATH = "network_data/phisingData.csv"   # path to your dataset
    DATABASE  = "phishing"           # MongoDB database name
    COLLECTION = "network_data"                # MongoDB collection name

    # Initialize ETL class
    network_obj = NetworkDataExtract()

    # Step 1: Extract + Transform (CSV → JSON)
    records = network_obj.csv_to_json_converter(file_path=FILE_PATH)
    print(f"Records converted: {len(records)}")

    # Step 2: Load (JSON → MongoDB)
    no_of_records = network_obj.insert_data_mongodb(records, DATABASE, COLLECTION)
    print(f"Records inserted into MongoDB: {no_of_records}")