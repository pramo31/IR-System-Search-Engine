#!/usr/bin/env python

"""VectorModel.py: Classes to maintain different types of indexing methods required for document retrieval along with retrieval methods"""
__author__ = "Pramodh Acharya"

import math


class InvertedIndexer:

    def __init__(self, page_rank, similarity_factor=0.85, page_rank_factor=0.15):
        self.__inverted_idx = {}
        self.__document_length_vector = {}
        self.__num_documents = 0
        self.similarity_factor = similarity_factor
        self.page_rank_factor = page_rank_factor
        self.page_rank = page_rank

    def get_inverted_index(self):
        return self.__inverted_idx

    def add_document_to_index(self, doc_id, tokenizer):
        self.__num_documents += 1
        document_index = {}
        max_freq = 0
        while (tokenizer.hasMoreElements()):
            token = tokenizer.nextElement()
            document_index[token] = document_index.get(token, 0) + 1
            max_freq = max(max_freq, document_index[token])

        for token, freq in document_index.items():
            self.__inverted_idx.setdefault(token, []).append([doc_id, freq / max_freq])

    def calculate_doc_length_vector(self):
        for term, docs in self.__inverted_idx.items():
            idf = math.log((self.__num_documents / len(docs)), 2)

            for doc_id, tf in docs:
                t_weight = tf * idf
                self.__document_length_vector[doc_id] = self.__document_length_vector.get(doc_id, 0) + math.pow(
                    t_weight, 2)

        for doc, vec in self.__document_length_vector.items():
            self.__document_length_vector[doc] = math.sqrt(vec)

    def retrieve_docs(self, query_tokenizer):
        query_terms = {}
        max_query_freq = 0
        while (query_tokenizer.hasMoreElements()):
            token = query_tokenizer.nextElement()
            query_terms[token] = query_terms.get(token, 0) + 1
            max_query_freq = max(max_query_freq, query_terms[token])

        for token, freq in query_terms.items():
            query_terms[token] = freq / max_query_freq

        relevant_docs = {}

        for term, q_tf in query_terms.items():
            if term in self.__inverted_idx:
                docs = self.__inverted_idx[term]
                idf = math.log((self.__num_documents / len(docs)), 2)
                for doc_id, tf in docs:
                    term_doc_weight = tf * idf
                    term_query_weight = q_tf * idf
                    relevant_docs[doc_id] = relevant_docs.get(doc_id, 0) + (term_doc_weight * term_query_weight)

        for doc_id, similarity in relevant_docs.items():
            page_rank_score = self.page_rank[doc_id]
            relevant_docs[doc_id] = (self.similarity_factor * relevant_docs[doc_id] / self.__document_length_vector[
                doc_id]) + (self.page_rank_factor * page_rank_score)

        return [doc_id for doc_id, sim in
                sorted([(doc_id, sim) for doc_id, sim in relevant_docs.items()], key=lambda x: (-x[1], x[0]))]

    def get_word_freq(self):
        result = []
        for k, v in self.__inverted_idx.items():
            result.append([k, 0])
            for doc, freq in v:
                result[-1][1] += freq

        return [term for term, freq in sorted([(t, f) for t, f in result], key=lambda x: x[1], reverse=True)]
