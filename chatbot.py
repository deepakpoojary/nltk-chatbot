import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from dotenv import load_dotenv
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json
import os

load_dotenv()

# TOKENS = os.getenv("TOKENS")
tokens_dict = json.loads(CreateExternalUser)

API_TOKEN = tokens_dict["token"]
REFRESH_TOKEN = tokens_dict["refreshToken"]

transport = RequestsHTTPTransport(
    url="https://shc-dev.krishitantra.com/",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    use_json=True,
)

client = Client(transport=transport, fetch_schema_from_transport=True)


# Predefined pairs of user inputs and bot responses
import pandas as pd

# Initialize the list to store pairs
pairs = []

# Define the file path
file_path = 'book4.csv'

# Define the column numbers containing the query text and answer
query_text_column = 2  # Assuming the 11th column (0-indexed) contains query text
query_answer_column = 3  # Assuming the 12th column (0-indexed) contains query answer

# Define the chunk size for reading the file
chunk_size = 100000  # Adjust as needed based on your system's memory capacity

# Iterate over chunks of the CSV file
for chunk in pd.read_csv(file_path, chunksize=chunk_size, encoding='utf-8',dtype=str):
    # Iterate over rows in the chunk and extract query text and answer
    for index, row in chunk.iterrows():
        query_text = row.iloc[query_text_column]
        query_answer = row.iloc[query_answer_column]
        pairs.append((query_text, query_answer))

# Extract user patterns and responses
user_patterns = [pattern for pattern, response in pairs]
responses = [response for pattern, response in pairs]

# Tokenizer and vectorizer
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
vectorizer = TfidfVectorizer(tokenizer=tokenizer.tokenize)

def replace_placeholders(response, match):
    """Replace placeholders in the response with matched groups."""
    for i in range(len(match.groups())):
        response = response.replace(f'%{i+1}', match.group(i+1))
    return response

def chatbot_response(user_message):
     # Example GraphQL query
    query = gql("""
    query ($message: String!) {
        respond(message: $message) {
            response
        }
    }
    """)
    params = {"message": user_message}

    try:
        response = client.execute(query, variable_values=params)
        return response["respond"]["response"]
    except Exception as e:
        return f"Sorry, I couldn't process your request at the moment. Error: {str(e)}"
# Example usage
if __name__ == "__main__":
    print(chatbot_response("my name is Deepak"))  # Expected: "Hello Deepak, how are you today?"
    print(chatbot_response("hello"))  # Expected: "Hello!"
    print(chatbot_response("hey"))  # Expected: "Hello!"
