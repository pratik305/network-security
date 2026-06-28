import os
from datetime import datetime
from networksecurity.constant import training_pipeline


class TrainingPipelineConfig:
    def __init__(self, pipeline_name=training_pipeline.PIPELINE_NAME):
        self.pipeline_name = pipeline_name
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.timestamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

        # Root artifact directory: Artifacts/timestamp
        self.artifact_dir = os.path.join(
            self.artifact_name,
            self.timestamp
        )


class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):

        # Root: Artifacts/timestamp/data_ingestion
        self.data_ingestion_dir = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME
        )

        # Feature store: .../data_ingestion/feature_store/phishing.csv
        self.feature_store_file_path = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
            training_pipeline.FILE_NAME
        )

        # Train file: .../data_ingestion/ingested/train.csv
        self.training_file_path = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TRAIN_FILE_NAME
        )

        # Test file: .../data_ingestion/ingested/test.csv
        self.testing_file_path = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TEST_FILE_NAME
        )

        # Split ratio and MongoDB info
        self.train_test_split_ratio = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        self.collection_name = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name = training_pipeline.DATA_INGESTION_DATABASE_NAME

if __name__ == "__main__":
    training_pipeline_config = TrainingPipelineConfig()
    data_ingestion_config = DataIngestionConfig(training_pipeline_config)

    print(data_ingestion_config.data_ingestion_dir)
    print(data_ingestion_config.feature_store_file_path)
    print(data_ingestion_config.training_file_path)
    print(data_ingestion_config.testing_file_path)
    print(data_ingestion_config.train_test_split_ratio)
    print(data_ingestion_config.collection_name)