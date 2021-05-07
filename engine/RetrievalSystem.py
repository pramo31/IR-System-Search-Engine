from crawler import WebScraper
from engine.VectorModel import InvertedIndexer
from evaluation.Evaluator import *
from processor.PreProcessor import LemmatizerTextProcessor
from processor.Tokenizer import Tokenizer
from utils.Utils import *
import os
import networkx as nx


# def get_n_docs(docs, n):
#     if n >= len(docs):
#         return docs.copy()
#     new_docs = {}
#     for k in docs:
#         if docs[k].id < n:
#             new_docs[k] = docs[k]
#     return new_docs
#
# def print_doc_details(documents):
#     for k, v in documents.items():
#         print(f"URL: {k}")
#         print(f"ID: {v.id}")
#         print(f"Links: ")
#         for l in v.outgoing_urls:
#             print(l)
#         print()
#
# def test(documents):
#     ids = []
#     for k, v in documents.items():
#         if (v is None):
#             print(k)
#         ids.append((v.id, k))
#
#     ids.sort(key=lambda x: x[0])
#     print(f'Number Documents: {len(ids)}')
#     # for i in ids:
#     #     print(i)
#     prev = 0
#     print(f"Last Idx {documents[ids[-1][1]].id}")
#     for i in range(1, len(ids)):
#         if ids[i][0] - prev != 1:
#             print('Error in assigning Id Here: ', prev, ids[i])
#         prev = ids[i][0]
#
#     return documents


def process_documents(documents):
    # remove unnecessary url's (like docs.google.com, login.uic.edu, login.uillinois.edu, uofi.account.box.com, non uic.edu, non http urls
    for url in list(documents.keys()):
        if not pattern_match(url, r'^https', r'.*uic.edu.*') or not pattern_not_match(url,
                                                                                      r'.*(docs\.google\.com|login\.uic\.edu|login\.uillinois\.edu|uofi\.account\.box\.com|print=).*',
                                                                                      r'^.*[.](xlsx|docx|gif|doc|xls|jpeg|mp3|png|jpg|pdf)$'):
            del documents[url]

    # re_id
    ids = []
    for k, v in documents.items():
        ids.append((v.id, k))

    ids.sort(key=lambda x: x[0])

    new_id = 0
    for old_id, url in ids:
        documents[url].id = new_id
        new_id += 1

    return documents


def scrape_web(name, start_url, allowed_domains, settings, root_folder='ir_system', crawl_limit=1):
    web_doc = f'{root_folder}/url_documents'
    if (not os.path.exists(web_doc)):
        print("Scraping the Web, Writing Them")
        documents = process_documents(WebScraper.run_spider(start_url, allowed_domains, name, crawl_limit, settings))
        write_pickle(web_doc, documents)
    else:
        print('Reading Docs from pickle')
        documents = read_pickle(web_doc)

    # For testing, remove later
    # num_docs_for_test = 10
    # documents = get_n_docs(documents, num_docs_for_test)
    # print_doc_details(documents)
    # test(documents)

    return documents


def create_graph(documents):
    graph = nx.DiGraph()

    for from_node in documents:
        out_flag = False
        for to_node in documents[from_node].outgoing_urls:
            if to_node in documents:
                out_flag = True
                graph.add_edge(from_node, to_node)
        if (not out_flag):
            graph.add_node(from_node)

    return graph


def get_page_rank(documents, damping_factor=0.9, root_folder='ir_system'):
    # Calculate Page Rank
    print('Calculating Page Rank')
    page_rank_doc = f'{root_folder}/page_rank'

    if (not os.path.exists(page_rank_doc)):
        graph = create_graph(documents)
        page_rank = nx.pagerank(graph)
        write_pickle(page_rank_doc, page_rank)
    else:
        page_rank = read_pickle(page_rank_doc)

    return page_rank


def generate_vector_space_model(url_documents, page_rank):
    inv_indexer = InvertedIndexer(page_rank)
    for doc, obj in url_documents.items():
        tk = Tokenizer(obj.text, LemmatizerTextProcessor())
        inv_indexer.add_document_to_index(doc, tk)

    inv_indexer.calculate_doc_length_vector()
    return inv_indexer


def get_vector_space_model(documents, page_rank, root_folder='ir_system'):
    print('Creating the Vector Space Model')
    vector_model_file = f'{root_folder}/vector_model'

    if not os.path.exists(vector_model_file):
        vector_model = generate_vector_space_model(documents, page_rank)
        write_pickle(vector_model_file, vector_model)
    else:
        vector_model = read_pickle(vector_model_file)

    return vector_model


def retrieve_documents(vector_model, query):
    tk = Tokenizer(query, LemmatizerTextProcessor())
    relevant_docs = vector_model.retrieve_docs(tk)
    return relevant_docs


# def convert(docs):
#     new_docs = {}
#     for k, v in docs.items():
#         new_d = Document.URLDocument(v.id, v.url, v.outgoing_urls, v.text)
#         new_docs[k] = new_d
#
#     print(len(new_docs))
#     return new_docs


if __name__ == "__main__":
    # Crawl Web
    settings = {
        "ROBOTSTXT_OBEY": True,
        "LOG_LEVEL": 'WARNING',
        "BOT_NAME": 'AssignmentBot',
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_DISK_QUEUE": 'scrapy.squeues.PickleFifoDiskQueue',
        "SCHEDULER_MEMORY_QUEUE": 'scrapy.squeues.FifoMemoryQueue'
    }
    crawl_limit = 1
    # root_folder = '../uic_ir_system'
    root_folder = '../ir_system'
    name = 'uic'
    start_url = ['https://www.cs.uic.edu']
    allowed_domains = ['uic.edu']
    documents = scrape_web(name, start_url, allowed_domains, settings, root_folder=root_folder)

    # web_doc = f'{root_folder}/url_documents'
    # write_pickle(web_doc, convert(documents))

    # graph = create_graph(documents)
    # print(graph.number_of_nodes())
    # print(graph.number_of_edges())
    # for e1, e2 in graph.edges:
    #     if('uic.edu' not in e1 or 'uic.edu' not in e2):
    #         print(e1, e2)
    #
    # for node in graph.nodes:
    #     if('uic.edu' not in node):
    #         print(node)

    # documents = process_documents((documents))
    # test
    # web_doc = f"{root_folder}/url_documents"
    # documents = test(documents)

    # page rank
    page_rank = get_page_rank(documents, root_folder=root_folder)

    # Top 10 page ranks
    # print(sorted([(v, k) for k, v in page_rank.items()], key=lambda x: x[0], reverse=True)[:10])

    # inverted index
    vector_model = get_vector_space_model(documents, page_rank, root_folder=root_folder)

    # evaluate_system(vector_model)
