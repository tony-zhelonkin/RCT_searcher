import requests
import xml.etree.ElementTree as ET
import re
import csv

# Define the E-utilities base URL
base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Define your email address
email = "shadartist@gmail.com"
max_results = 1000  # Set max results outside the function

# Function to search PubMed for human clinical trials with pagination
def search_pubmed(term, max_results):
    id_list = []
    retmax = 100  # Number of results per request
    for retstart in range(0, max_results, retmax):
        search_url = f"{base_url}esearch.fcgi?db=pubmed&term={term}&retstart={retstart}&retmax={retmax}&retmode=json&email={email}"
        response = requests.get(search_url)
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from PubMed. Status code: {response.status_code}")
            continue
        data = response.json()
        print(f"Retrieved {len(data['esearchresult']['idlist'])} IDs")
        id_list.extend(data['esearchresult']['idlist'])
        if len(data['esearchresult']['idlist']) < retmax:
            break  # Exit loop if fewer results returned than requested
    return id_list

# Function to fetch and parse details of articles using EFetch with chunking
def fetch_and_parse_article_details(id_list, chunk_size=200):
    nct_codes = []
    for i in range(0, len(id_list), chunk_size):
        chunk = id_list[i:i+chunk_size]
        ids = ",".join(chunk)
        fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={ids}&retmode=xml&email={email}"
        response = requests.get(fetch_url)
        if response.status_code != 200:
            print(f"Error: Unable to fetch article details. Status code: {response.status_code}")
            continue
        xml_data = response.text
        nct_codes.extend(extract_nct_codes(xml_data))
    return nct_codes

# Function to extract NCT codes from a single chunk of XML data
def extract_nct_codes(xml_data):
    root = ET.fromstring(xml_data)
    nct_codes = []

    for article in root.findall('.//PubmedArticle'):
        article_text = ''
        
        # Extract title, abstract, and other fields where NCT codes might appear
        title = article.find('.//ArticleTitle')
        if title is not None and title.text is not None:
            article_text += title.text + ' '
        
        abstract = article.find('.//Abstract/AbstractText')
        if abstract is not None and abstract.text is not None:
            article_text += abstract.text + ' '

        # Check all sections of the abstract if available
        for abstract_section in article.findall('.//Abstract/AbstractText'):
            if abstract_section.text is not None:
                article_text += abstract_section.text + ' '
        
        # Use regex to find NCT codes in the combined text
        codes = re.findall(r'NCT\d{8}', article_text)
        if codes:
            print("NCT codes found:", codes)  # Debugging print
        nct_codes.extend(codes)

    return nct_codes

# Function to save NCT codes to a CSV file
def save_nct_codes_to_csv(nct_codes, filename="nct_codes.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["NCT Code"])  # Write header
        for code in nct_codes:
            writer.writerow([code])

# Define the complex search term
search_term = "(oncology) AND ((clinical trial) OR (trial) OR (phase 1) OR (phase 2) OR (phase 3) OR (final results))"

# Step 1: Search PubMed
article_ids = search_pubmed(search_term, max_results)
print(f"Found {len(article_ids)} articles")  # Debugging print

# Step 2: Fetch and parse article details
if article_ids:
    nct_codes = fetch_and_parse_article_details(article_ids)
    print("Fetched and parsed article details")  # Debugging print

    # Step 3: Save NCT codes to CSV
    print(f"Extracted {len(nct_codes)} NCT codes")  # Debugging print
    save_nct_codes_to_csv(nct_codes)
    print(f"Saved NCT codes to nct_codes.csv")
else:
    print("No articles found.")
