import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    def __init__(self,
                 data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact   = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """Read CSV file and return DataFrame"""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def get_data_transformer_object(cls) -> Pipeline:
        """
        Initializes the KNN Imputer with parameters from training_pipeline.py
        and returns a Pipeline object with KNNImputer as the first step.
        """
        logging.info("Entered get_data_transformer_object method of DataTransformation class")
        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"Initialized KNNImputer with params: {DATA_TRANSFORMATION_IMPUTER_PARAMS}")

            processor: Pipeline = Pipeline([("imputer", imputer)])
            return processor

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """Run full transformation: read → split target → impute → save"""
        logging.info("Entered initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation")

            # Step 1: Read valid train/test data
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df  = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # Step 2: Split into input features and target (train)
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)

            # Step 2: Split into input features and target (test)
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # Step 3: Build and fit KNN Imputer pipeline
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_df)

            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature  = preprocessor_object.transform(input_feature_test_df)

            # Step 4: Combine features + target into numpy arrays
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr  = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # Step 5: Save numpy arrays
            save_numpy_array_data(
                self.data_transformation_config.transformed_train_file_path,
                array=train_arr
            )
            save_numpy_array_data(
                self.data_transformation_config.transformed_test_file_path,
                array=test_arr
            )

            # Step 6: Save preprocessing pipeline as pickle
            save_object(
                self.data_transformation_config.transformed_object_file_path,
                preprocessor_object
            )

            # Step 7: Prepare and return artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            logging.info("Data transformation completed")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)