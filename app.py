import html
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np  
import nltk
import re
from dotenv import load_dotenv
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json
import os
load_dotenv()

# Get the JSON token from environment variables
tokens = os.getenv("GRAPHQL_TOKEN")

# Extract the token and refresh token



transport = RequestsHTTPTransport(
    url="https://shc-dev.krishitantra.com/",
    headers={"Authorization": f"Bearer {tokens}"},#with token we are going there
    use_json=True,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

import pandas as pd

# Initialize the list to store pairs
pairs = []
pairs.append(('', 'Stick to agriculture-related questions'))
pairs.append(('my name is (.*)', 'Hello %1, how are you today?'))
# Add greeting response
pairs.append(('(hi|hello|hey)', 'Hello!'))

# Add name response
pairs.append(('(.*) your name ?', 'My name is ChatBot.'))

# Add default response for 'how are you' question
pairs.append(('how are you (.*)', 'I am doing well, thank you!'))

# Add default response for 'location' question
pairs.append(('(.*) (location|city) ?', 'I am a virtual assistant, I live in the cloud.'))

# Add exit response
pairs.append(('quit', 'Bye! Take care.'))
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

def another_response(user_input):
    # Compute the TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(user_patterns + [user_input])
    # Compute the cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    # Find the index of the best match
    best_match_index = np.argmax(cosine_similarities)

    # Get the best matching pattern and response
    best_pattern = user_patterns[best_match_index]
    response = responses[best_match_index]

    # Match the user input against the best pattern to find groups
    match = re.match(best_pattern, user_input, re.IGNORECASE)

    if match:
        # Replace placeholders in the response
        response = replace_placeholders(response, match)
    
    return response

def chatbot_response(user_message):
    
     # Example GraphQL query
    query = gql("""
    query GetTestForPortal($phone: String, $locale: String) {
  getTestForPortal(phone: $phone) {
    html(locale: $locale)
  }
}
    """)
    params = {"phone": user_message}

    try:
        response = client.execute(query, variable_values=params)
        # print(response)
        # rep=html.unescape(response['getTestForPortal'][0]['html'])
        
        return response
        
    except Exception as e:
        return f"Sorry, I couldn't process your request at the moment. Error: {str(e)}"



app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    print(user_message)
    if user_message == "report":
        response = "Please enter your numbers."
    elif re.fullmatch(r'\d{10}', user_message):  # Check if the message is a 10-digit number
        response = chatbot_response(user_message)
    else:
        response = another_response(user_message)

    return jsonify({"response": response})
    
    
    

if __name__ == "__main__":
    app.run(debug=True)
