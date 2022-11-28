import nltk
from data import *
from transformers import pipeline

context = data()
question_answerer = pipeline('question-answering')

nltk.download('nps_chat')
posts = nltk.corpus.nps_chat.xml_posts()[:10000]

def dialogue_act_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features['contains({})'.format(word.lower())] = True
    return features

question_types = ["whQuestion","ynQuestion"]
featuresets = [(dialogue_act_features(post.text), post.get('class')) for post in posts]

size = int(len(featuresets)*0.05)

train_set, test_set = featuresets[size:], featuresets[:size]

classifier = nltk.NaiveBayesClassifier.train(train_set)

def get_accuracy(classifier, test_set):
    return(nltk.classify.accuracy(classifier, test_set))


def is_question(ques):
    question_type = classifier.classify(dialogue_act_features(ques)) 
    return question_type in question_types

def answer_question(question):
    result = question_answerer(question=question, context=context)
    return result['answer']

async def execute_operations2(client, message):
    msg = message.content
    valid = ["meeting", "ai", "club", "aiclub"]
    if any(word in msg for word in valid):
        result = answer_question(msg)
        await message.reply(result)


