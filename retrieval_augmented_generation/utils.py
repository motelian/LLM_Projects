import numpy as np
import pandas as pd 
import openai
import tiktoken
from openai.embeddings_utils import get_embedding
from openai.embeddings_utils import  cosine_similarity

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

# TODO:  could be a class with embedding attributes and other functions such as similarity search etc.
def num_tokens(x, model='text-embedding-ada-002'):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(x))

def calc_embedding_cost(x, cost=0.0001/1000):
    return num_tokens(x)*cost


def retrieve_relevant_text(query, vectordb, embedding_model='text-embedding-ada-002', top_n=3, verbose=True):
    # get the cost
    cost = calc_embedding_cost(query)
    
    # get query's embedding
    query_embedding = get_embedding(query, engine=embedding_model)

    # search against the database and get the top matches
    vectordb['similarity_score'] = vectordb.embedding.apply(lambda x: cosine_similarity(x, query_embedding))
    result = vectordb.sort_values(by='similarity_score', ascending=False).head(top_n)
    
    # we sort the chunks  again according to their index in ascending order to maintain the semantic connectedness of the document
    result = result.sort_index()
    
    if verbose:
        print(f'query embedding cost:${cost}')
    
    return [(row["text"], row['similarity_score']) for i, row in result.iterrows()]

def prompt_tempelate(query, vectordb, model, embedding_model='text-embedding-ada-002', max_tokens = 1000, verbose=True):
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    related_text = retrieve_relevant_text(query, vectordb, top_n=3, verbose=verbose, embedding_model=embedding_model)
    intro = """Answer the following Question based on the Context only. Only answer from the Context. If you don't know the answer, say 'I don't know'."""
    question = f"\n\nQuestion: {query}"
    message = intro
    for i in related_text:
        next_text, _ = i
        next_text = f'\n\n{next_text}\n\n'
        if num_tokens(message + next_text + question, model=model) > max_tokens:
            print('stopped using texts from the database...')
            print(f'-- GPT prompt tokens exceeds maximum token limit ({max_tokens})')
            break
        else:
            message += next_text
    return message + question 

def ask(
    query,
    vectordb,
    model="gpt-3.5-turbo",
    embedding_model='text-embedding-ada-002',
    max_tokens=1000,
    verbose=False,
    temperature=0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
):
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = prompt_tempelate(query, vectordb=vectordb, model=model, max_tokens=max_tokens, verbose=verbose, embedding_model=embedding_model)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message},
    ]
    
    if verbose:
        print(f"{''.join(20*['-'])}\n")
        print(message)
        print(f"{''.join(20*['-'])}")
        print(f'Total GPT cost: ${np.round(num_tokens_from_messages(messages=messages, model=model)*0.003/1000)}')
        
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message