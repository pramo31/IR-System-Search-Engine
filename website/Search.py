from flask import Flask, render_template, request
from engine import RetrievalSystem
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('search.html')


@app.route("/search")
def search():
    query = request.args["query"]
    results = RetrievalSystem.retrieve_documents(vector_model, query)
    return render_template("search.html", query=query, results=results)


def get_vector_model(scrapy_settings, name, start_url, allowed_domains, root_folder='ir_system', crawl_limit=1):
    if not os.path.exists(root_folder):
        os.mkdir(root_folder)

    documents = RetrievalSystem.scrape_web(name, start_url, allowed_domains, scrapy_settings, root_folder=root_folder,
                                           crawl_limit=crawl_limit)
    # documents = RetrievalSystem.scrape_web(name, start_url, allowed_domains, settings)

    # page_rank
    page_rank = RetrievalSystem.get_page_rank(documents, root_folder=root_folder)

    # inverted index
    vector_model = RetrievalSystem.get_vector_space_model(documents, page_rank, root_folder=root_folder)

    return vector_model


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
    crawl_limit = 15000
    root_folder = '../ir_system'
    # root_folder = '../uic_ir_system'
    name = 'uic'
    start_url = ['https://www.cs.uic.edu']
    allowed_domains = ['uic.edu']
    vector_model = get_vector_model(settings, name, start_url, allowed_domains, root_folder=root_folder,
                                    crawl_limit=crawl_limit)
    app.run()
