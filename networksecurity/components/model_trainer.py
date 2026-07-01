import sys
import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier
)
from sklearn.neighbors import KNeighborsClassifier

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact,
    ClassificationMetricArtifact
)
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.utils.main_utils.utils import (
    load_numpy_array_data,
    load_object,
    save_object,
    evaluate_models
)
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


class ModelTrainer:
    def __init__(self,
                 model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config         = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, x_train, y_train, x_test, y_test):
        """Try multiple models with GridSearchCV, pick best, return ModelTrainerArtifact"""
        try:
            # --- Define models ---
            models = {
                "Random Forest":        RandomForestClassifier(verbose=1),
                "Decision Tree":        DecisionTreeClassifier(),
                "Gradient Boosting":    GradientBoostingClassifier(verbose=1),
                "Logistic Regression":  LogisticRegression(verbose=1),
                "AdaBoost":             AdaBoostClassifier(),
            }

            # --- Define hyperparameter grids ---
            params = {
                "Decision Tree": {
                    "criterion": ["gini", "entropy"],
                    # "splitter": ["best", "random"],
                    # "max_features": ["sqrt", "log2"],
                },
                "Random Forest": {
                    "n_estimators": [8, 16, 32, 64, 128, 256],
                },
                "Gradient Boosting": {
                    "learning_rate": [0.1, 0.01, 0.05, 0.001],
                    "subsample":     [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    "n_estimators":  [8, 16, 32, 64, 128, 256],
                },
                "Logistic Regression": {},
                "AdaBoost": {
                    "learning_rate": [0.1, 0.01, 0.5, 0.001],
                    "n_estimators":  [8, 16, 32, 64, 128, 256],
                },
            }

            # --- Evaluate all models ---
            model_report: dict = evaluate_models(
                x_train=x_train, y_train=y_train,
                x_test=x_test,   y_test=y_test,
                models=models,   params=params
            )

            # --- Get best model ---
            best_model_score = max(sorted(model_report.values()))
            best_model_name  = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            # --- Train predictions ---
            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(
                y_true=y_train, y_pred=y_train_pred
            )

            # --- Test predictions ---
            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(
                y_true=y_test, y_pred=y_test_pred
            )

            # --- Check overfitting/underfitting ---
            diff = abs(classification_train_metric.f1_score - classification_test_metric.f1_score)
            if diff > self.model_trainer_config.overfitting_underfitting_threshold:
                raise Exception("Model is overfitting or underfitting. Try different parameters.")

            # --- Check minimum accuracy ---
            if classification_test_metric.f1_score < self.model_trainer_config.expected_accuracy:
                raise Exception(f"No best model found. F1 score below expected {self.model_trainer_config.expected_accuracy}")

            # --- Load preprocessor and build NetworkModel ---
            preprocessor = load_object(
                self.data_transformation_artifact.transformed_object_file_path
            )
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            network_model = NetworkModel(preprocessor=preprocessor, model=best_model)

            save_object(
                self.model_trainer_config.trained_model_file_path,
                obj=network_model
            )

            # --- Also save to saved_models/ for later use ---
            save_object("saved_models/model.pkl", obj=best_model)

            # --- Build artifact ---
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")
        try:
            # Load numpy arrays
            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )
            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            # Split features and target
            x_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            x_test,  y_test  = test_arr[:, :-1],  test_arr[:, -1]

            # Train and return artifact
            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)