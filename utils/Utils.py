import pickle
import re
import urllib.parse as up
from utils.DocumentUtils import DocumentReader


def fetch_base_url(url):
    return re.findall('https?://[^/]+', url)[0]


def canonicalize_url(url):
    url = re.sub(r'/$', '', url)
    url = re.sub(r'^https://www.', 'https://', url)
    return url


def defrag_url(url):
    return up.urldefrag(url).url


def is_valid_crawlable(url, *patterns):
    for pattern in patterns:
        if not re.match(pattern, url):
            return False
    return True


def http_secure_url(url):
    return re.sub(r'^http://', 'https://', url)


def write_pickle(filename, data):
    outfile = open(filename, 'wb')
    pickle.dump(data, outfile)
    outfile.close()


def read_pickle(filename):
    infile = open(filename, 'rb')
    obj = pickle.load(infile)
    infile.close()
    return obj


def evaluate_retrieval_systems(retrieved_documents, relevant_documents, precision, recall, thresholds):
    for threshold in thresholds:
        retrieved = set(retrieved_documents[0:threshold])
        retrieved_relevant = retrieved.intersection(relevant_documents)
        recall[threshold] = recall.get(threshold, 0) + (len(retrieved_relevant) / len(relevant_documents))
        precision[threshold] = precision.get(threshold, 0) + (len(retrieved_relevant) / len(retrieved))


def generate_relevance_dict(relevance_file):
    dr = DocumentReader()
    relevance_query_map = {}
    relevance = dr.read_file(relevance_file)
    for r in relevance:
        q, doc = r.split()
        relevance_query_map.setdefault(int(q), set()).add(int(doc))
    return relevance_query_map


def pattern_match(url, *patterns):
    for pattern in patterns:
        if not re.match(pattern, url):
            return False
    return True


def pattern_not_match(url, *patterns):
    for pattern in patterns:
        if re.match(pattern, url):
            return False
    return True
