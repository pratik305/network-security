import yaml
import os
import sys
import numpy as np
import pickle
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score


def read_yaml_file(file_path: str) -> dict:
    """Read a YAML file and return contents as dictionary"""
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """Write content to a YAML file"""
    try:
        if replace and os.path.exists(file_path):
            os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def save_numpy_array_data(file_path: str, array: np.array):
    """Save numpy array to file"""
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def save_object(file_path: str, obj: object) -> None:
    """Save any Python object (e.g. preprocessor) as a pickle file"""
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def load_object(file_path: str) -> object:
    """Load a pickle file and return the object"""
    try:
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} does not exist")
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def load_numpy_array_data(file_path: str) -> np.array:
    """Load numpy array from file"""
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)



def evaluate_models(x_train, y_train, x_test, y_test, models: dict, params: dict) -> dict:
    """Train multiple models with GridSearchCV and return test scores"""
    try:
        report = {}

        for model_name in models.keys():
            model = models[model_name]
            model_params = params[model_name]

            # Hyperparameter tuning with cross-validation
            gs = GridSearchCV(model, model_params, cv=3)
            gs.fit(x_train, y_train)

            # Set best params and retrain
            model.set_params(**gs.best_params_)
            model.fit(x_train, y_train)

            # Predictions
            y_train_pred = model.predict(x_train)
            y_test_pred  = model.predict(x_test)

            # Scores
            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score  = r2_score(y_test, y_test_pred)

            report[model_name] = test_model_score

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
