__author__ = 'keleigong'
import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer

import re


def preprocess(sentence):
    # wordnet_lemmatizer = WordNetLemmatizer()
    # stemmer = PorterStemmer()
    stemmer = SnowballStemmer("english")
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(sentence)
    # print(wordnet_lemmatizer.lemmatize("didn't"))
    filtered_words = [stemmer.stem(w) for w in tokens if not w in stopwords.words('english')]
    return " ".join(filtered_words)

sentence = "At eight o'clock on||]*() # Thursday morning Arthur did feel very good. French-Fries"
print(preprocess(sentence))