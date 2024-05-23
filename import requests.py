import requests
from bs4 import BeautifulSoup

def search_pubmed(term, max_results=100):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term}&retmax={max_results}&retmode=json"
    response = requests.get(url)
    data = response.json()
    id_list = data['esearchresult']['idlist']
    return id_list

def fetch_article_details(pubmed_id):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pubmed_id}&retmode=xml"
    response = requests.get(url)
    return response.text

term = "oncology AND clinical trial"
ids = search_pubmed(term)
for pubmed_id in ids:
    article_details = fetch_article_details(pubmed_id)
    soup = BeautifulSoup(article_details, 'xml')
    print(soup.prettify())
    