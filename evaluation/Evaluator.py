from processor.PreProcessor import LemmatizerTextProcessor
from processor.Tokenizer import Tokenizer
from utils.DocumentUtils import DocumentReader
from utils.Utils import generate_relevance_dict


def evaluate_retrieval_systems(retrieved_documents, relevant_documents, precision, recall, thresholds):
    print(retrieved_documents[:5])
    for threshold in thresholds:
        retrieved = set(retrieved_documents[0:threshold])
        retrieved_relevant = retrieved.intersection(relevant_documents)
        recall[threshold] = recall.get(threshold, 0) + (len(retrieved_relevant) / len(relevant_documents))
        precision[threshold] = precision.get(threshold, 0) + (len(retrieved_relevant) / len(retrieved))


def evaluate_system(vector_model):
    dr = DocumentReader()
    query_file = '../evaluation/queries.txt'
    queries = dr.read_file(query_file)

    relevance_file = '../evaluation/relevance.txt'
    relevance_dict = generate_relevance_dict(relevance_file)

    query_num = 0
    threshold = [10]
    precision = {}
    recall = {}
    for q in queries:
        query_num += 1
        retrieved_docs = vector_model.retrieve_docs(Tokenizer(q, LemmatizerTextProcessor()))
        print(f"Retrieved {len(retrieved_docs)} documents")
        evaluate_retrieval_systems(retrieved_docs, relevance_dict[q.lower().strip()], precision, recall, threshold)

    print('Retrieval System Evaluation')
    print()
    for t in threshold:
        print(f'Threshold : Top {t} Documents')
        print(f'Precision : {round(precision[t] / query_num, 3)}')
        print(f'Recall : {round(recall[t] / query_num, 3)}')
        print()


def evaluate(vector_model, query, threshold):
    relevance_file = '../evaluation/relevance.txt'
    relevance_dict = generate_relevance_dict(relevance_file)
    if query.lower().strip() not in relevance_dict:
        return 0, 0

    relevant_documents = relevance_dict[query.lower().strip()]
    retrieved_docs = vector_model.retrieve_docs(Tokenizer(query, LemmatizerTextProcessor()))

    print(retrieved_docs[:5])

    retrieved = set(retrieved_docs[0:threshold])
    retrieved_relevant = retrieved.intersection(relevant_documents)
    recall = len(retrieved_relevant) / len(relevant_documents)
    precision = len(retrieved_relevant) / len(retrieved)

    print(f"Num Relevant Retrieved Documents : {retrieved_relevant}")
    print(f"Recall : {recall}")
    print(f"Precision : {precision}")
    return precision, recall
