#!/usr/bin/env python

"""Tokenizer.py: Set of classes and sub-classes to Tokenize and Process the text"""
__author__ = "Pramodh Acharya"

from processor import PreProcessor


class Tokenizer():

    def __init__(self, str, processor):
        self.__tokens = []
        for s in str.split(' '):
            token = processor.process(s)
            if (token != '' and len(token) <= 20):
                self.__tokens.append(token)
        self.__idx = 0

    def hasMoreElements(self):
        return self.__idx < len(self.__tokens)

    def nextElement(self):
        idx = self.__idx
        self.__idx += 1
        return self.__tokens[idx]


class StringTokenizer(Tokenizer):

    def __init__(self, str_list):
        super().__init__(str_list, PreProcessor.TextProcessor())


class StemmedStringTokenizer(Tokenizer):

    def __init__(self, str_list):
        super().__init__(str_list, PreProcessor.StemmerTextProcessor())


class LemmatizedStringTokenizer(Tokenizer):

    def __init__(self, str_list):
        super().__init__(str_list, PreProcessor.LemmatizerTextProcessor())
