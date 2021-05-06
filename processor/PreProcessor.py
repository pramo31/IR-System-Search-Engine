#!/usr/bin/env python

"""PreProcessor.py: Utility file containing Processing functions"""
__author__ = "Pramodh Acharya"

import re
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import splitter


# nltk.download('stopwords')
# nltk.download('wordnet')


def is_stop_word(token):
    return token in stop_words


def is_small_jibberish(token):
    return len(token) <= 2


stop_words = set(stopwords.words('english'))


class TextProcessor():

    def __init__(self):
        self.porter_stemmer = PorterStemmer()
        self.wordnet_lemmatizer = WordNetLemmatizer()

    def remove_special_characters(self, token):
        return re.sub(r'[_\W\s]', '', token)

    def remove_numericals(self, token):
        return re.sub(r'[\d]', '', token)

    def conver_to_lower(self, token):
        return token.lower()

    def stem_word(self, token):
        return self.porter_stemmer.stem(token)

    def lemmatize_word(self, token):
        return self.wordnet_lemmatizer.lemmatize(token)

    def remove_html_tags(self, token):
        return re.sub(r'^<.*>$', '', token)

    def split_token(self, token):
        return [t for t in [self.process(w) for w in splitter.split(token)] if t != '']

    def process(self, token):
        token = self.conver_to_lower(token)
        token = self.remove_numericals(token)

        if is_stop_word(token) or is_small_jibberish(token):
            return ''
        token = self.remove_html_tags(token)
        token = self.remove_special_characters(token)
        token = token.strip()
        if is_stop_word(token) or is_small_jibberish(token):
            return ''
        return token


class StemmerTextProcessor(TextProcessor):

    def __init__(self):
        super().__init__()

    def process(self, token):
        token = super().process(token)
        token = self.stem_word(token)
        if is_stop_word(token) or is_small_jibberish(token):
            return ''
        return token


class LemmatizerTextProcessor(TextProcessor):

    def __init__(self):
        super().__init__()

    def process(self, token):
        token = super().process(token)
        token = self.lemmatize_word(token)
        if is_stop_word(token) or is_small_jibberish(token):
            return ''
        return token
