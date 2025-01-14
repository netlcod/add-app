import os
import json


def parse_array_configuration(path):
    configuration = {
        "ARRAY_PATH": None,
        "ARRAY_NAME": None,
        "SAMPLE_RATE": None,
        "MIC_ARRAY": None,
        "PHYSICAL_COUNT": None,
    }

    with open(path, "r") as file:
        data = json.load(file)
        configuration["ARRAY_PATH"] = path
        configuration["ARRAY_NAME"] = data["Name"]
        configuration["SAMPLE_RATE"] = data["Sample rate"]
        configuration["MIC_ARRAY"] = data["Array"]
        configuration["PHYSICAL_COUNT"] = sum(
            map(lambda value: value.get("type") == "physical", data["Array"].values())
        )
        configuration["VIRTUAL_COUNT"] = sum(map(lambda value: value.get("type") == "virtual", data["Array"].values()))

    return configuration


def parse_model_configuration(path):
    filename = os.path.basename(path).split(".h5")[0]
    fileparts = filename.split("-")

    configuration = {
        "MODEL_PATH": None,
        "NN_TYPE": None,
        "FEATURE_DATASET": None,
        "FEATURE_DURATION": None,
        "FEATURE_OVERLAPPING": None,
        "FEATURE_TYPE": None,
        "FEATURE_SIZE": None,
        "N_FFT": None,
        "HOP_LENGTH": None,
    }

    configuration["MODEL_PATH"] = path
    configuration["NN_TYPE"] = fileparts[0]
    configuration["FEATURE_DATASET"] = fileparts[1]
    configuration["FEATURE_DURATION"] = fileparts[2]
    configuration["FEATURE_OVERLAPPING"] = fileparts[3]
    configuration["FEATURE_TYPE"] = fileparts[4]
    configuration["FEATURE_SIZE"] = fileparts[5]
    configuration["N_FFT"] = fileparts[6]
    configuration["HOP_LENGTH"] = fileparts[7]

    return configuration
