import nltk
from nltk.chat.util import Chat, reflections

# Define a simple set of patterns and responses
pairs = [
    ['my name is (.*)', ['Hello %1, how are you today?']],
    ['(hi|hello|hey)', ['Hello!', 'Hi there!']],
    ['(.*) your name ?', ['My name is ChatBot.']],
    ['how are you (.*)', ['I am doing well, thank you!']],
    ['(.*) (location|city) ?', ['I am a virtual assistant, I live in the cloud.']],
    ['quit', ['Bye! Take care.']]
]

chat = Chat(pairs, reflections)

def chatbot_response(user_input):
    return chat.respond(user_input)
