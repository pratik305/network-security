import sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig
from networksecurity.components.data_ingestion import DataIngestion

if __name__ == "__main__":
    try:
        logging.info("Initiating data ingestion")

        # Initialize configs
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config    = DataIngestionConfig(training_pipeline_config)

        # Run data ingestion
        data_ingestion           = DataIngestion(data_ingestion_config)
        data_ingestion_artifact  = data_ingestion.initiate_data_ingestion()

        print(data_ingestion_artifact)
        logging.info("Data ingestion completed")

    except Exception as e:
        raise NetworkSecurityException(e, sys)