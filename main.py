import sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig
)
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)
from networksecurity.components.model_trainer import ModelTrainer


if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()

        # --- Data Ingestion ---
        logging.info("Initiating data ingestion")
        data_ingestion_config   = DataIngestionConfig(training_pipeline_config)
        data_ingestion          = DataIngestion(data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed")
        print(data_ingestion_artifact)

        # --- Data Validation ---
        logging.info("Initiating data validation")
        data_validation_config   = DataValidationConfig(training_pipeline_config)
        data_validation          = DataValidation(data_ingestion_artifact, data_validation_config)
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed")
        print(data_validation_artifact)

        # --- Data Transformation ---
        logging.info("Data transformation started")
        data_transformation_config   = DataTransformationConfig(training_pipeline_config)
        data_transformation          = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("Data transformation completed")
        print(data_transformation_artifact)

        # --- Model Trainer ---
        logging.info("Model training started")
        model_trainer_config   = ModelTrainerConfig(training_pipeline_config)
        model_trainer          = ModelTrainer(model_trainer_config, data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed")
        print(model_trainer_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)