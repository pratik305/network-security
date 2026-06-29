import os
import sys
import pymongo
import certifi
import pandas as pd
import numpy as np
from typing import List
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

# Load environment variables
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """Step 1: Export MongoDB collection as a DataFrame"""
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=certifi.where())
            collection =  self.mongo_client[database_name][collection_name]

            # Convert MongoDB collection to DataFrame
            df = pd.DataFrame(list(collection.find()))

            # Drop MongoDB's default '_id' column if it exists
            if '_id' in df.columns.tolist():
                df = df.drop(columns=['_id'], axis=1)

            # Replace "na" strings with NaN
            df.replace({"na": np.nan}, inplace=True)

            return df
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Step 2: Export DataFrame to feature store as CSV"""
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)

            # Create directory if it doesn't exist
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # Save DataFrame to CSV
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info(f"Data Saved to feature store: {feature_store_file_path}")


        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def split_data_as_train_test(self, dataframe:pd.DataFrame):
        """Step 3: Split data to train/test and save to ingested folder"""

        try:
            logging.info("Performing train/test split on dataframe")
            
            train_set, test_set = train_test_split(
                dataframe,
                test_size= self.data_ingestion_config.train_test_split_ratio
            )

            logging.info("Train/Test split completed")

            # Create ingested directory
            dir_path = os.path.dirname(self.data_ingestion_config.testing_file_path)
            os.makedirs(dir_path,exist_ok=True)

            # save train and test csv files
            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path,index=False,header=True)

            logging.info("Exported train and test files to ingested folder")

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        """Main method - runs all 3 steps and return artifacts"""

        try:
            # Step 1: Read from MongoDB
            dataframe = self.export_collection_as_dataframe()

            # Step 2: Save raw data to feature store
            self.export_data_into_feature_store(dataframe)

            # Step 3: Train/Test split and save
            self.split_data_as_train_test(dataframe)

            # Return artifact with output paths
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path = self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            return data_ingestion_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        

