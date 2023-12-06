import logging
from typing import Any, List, Union
import os
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import tiktoken


logger = logging.getLogger("chat2vis")


def get_dirs(path: str) -> List[str]:
    return next(os.walk(path))[1]


def clean_column_names(df):
    # create a copy of the dataframe to avoid modifying the original data
    cleaned_df = df.copy()

    # iterate over column names in the dataframe
    for col in cleaned_df.columns:
        # check if column name contains any special characters or spaces
        if re.search('[^0-9a-zA-Z_]', col):
            # replace special characters and spaces with underscores
            new_col = re.sub('[^0-9a-zA-Z_]', '_', col)
            # rename the column in the cleaned dataframe
            cleaned_df.rename(columns={col: new_col}, inplace=True)

    # return the cleaned dataframe
    return cleaned_df


def read_dataframe(file_location):
    file_extension = file_location.split('.')[-1]
    if file_extension == 'json':
        try:
            df = pd.read_json(file_location, orient='records')
        except ValueError:
            df = pd.read_json(file_location, orient='table')
    elif file_extension == 'csv':
        df = pd.read_csv(file_location)
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(file_location)
    elif file_extension == 'parquet':
        df = pd.read_parquet(file_location)
    elif file_extension == 'feather':
        df = pd.read_feather(file_location)
    elif file_extension == "tsv":
        df = pd.read_csv(file_location, sep="\t")
    else:
        raise ValueError('Unsupported file type')

    # clean column names and check if they have changed
    cleaned_df = clean_column_names(df)
    if cleaned_df.columns.tolist() != df.columns.tolist() or len(df) > 4500:
        if len(df) > 4500:
            logger.info(f"Dataframe has more than 4500 rows. We will sample 4500 rows.")
            cleaned_df = cleaned_df.sample(4500)
        # write the cleaned DataFrame to the original file on disk
        if file_extension == 'csv':
            cleaned_df.to_csv(file_location, index=False)
        elif file_extension in ['xls', 'xlsx']:
            cleaned_df.to_excel(file_location, index=False)
        elif file_extension == 'parquet':
            cleaned_df.to_parquet(file_location, index=False)
        elif file_extension == 'feather':
            cleaned_df.to_feather(file_location, index=False)
        elif file_extension == 'json':
            with open(file_location, 'w') as f:
                f.write(cleaned_df.to_json(orient='records'))
        else:
            raise ValueError('Unsupported file type')

    return cleaned_df


def file_to_df(file_location: str):
    """ Get summary of data from file location """
    file_name = file_location.split("/")[-1]
    df = None
    if "csv" in file_name:
        df = pd.read_csv(file_location)
    elif "xlsx" in file_name:
        df = pd.read_excel(file_location)
    elif "json" in file_name:
        df = pd.read_json(file_location, orient="records")
    elif "parquet" in file_name:
        df = pd.read_parquet(file_location)
    elif "feather" in file_name:
        df = pd.read_feather(file_location)

    return df


def clean_code_snippet(code_string):
    # Extract code snippet using regex
    cleaned_snippet = re.search(r'```(?:\w+)?\s*([\s\S]*?)\s*```', code_string)

    if cleaned_snippet:
        cleaned_snippet = cleaned_snippet.group(1)
    else:
        cleaned_snippet = code_string

    # remove non-printable characters
    # cleaned_snippet = re.sub(r'[\x00-\x1F]+', ' ', cleaned_snippet)

    return cleaned_snippet


# adopted from https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
