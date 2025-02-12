# Import libraries
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pdfplumber
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import re

# Counter to track file numbering
output_counter = 1

# Utility function to write output to a numbered file
def write_to_file(content, prefix="output"):
    global output_counter
    filename = f"{prefix}{output_counter}.txt"
    with open(filename, 'a') as file:
        file.write(content + "\n")
    output_counter += 1

# Function to download and parse HTML content
async def scrape_html(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.text()
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text(strip=True)
            write_to_file(f"HTML Content from {url}:\n{text_content}")
            
            # Extract PDF links
            pdf_links = [link['href'] for link in soup.find_all('a', href=True) if link['href'].endswith('.pdf')]
            for pdf_url in pdf_links:
                await scrape_pdf(session, pdf_url, pdf_url.split('/')[-1])  # Handle PDFs

            # Process content for keywords
            process_scraped_content(text_content, url)
    except Exception as err:
        print(f"Error processing HTML ({url}): {err}")

# Function to download and parse PDF content
async def scrape_pdf(session, url, pdf_filename):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()

            with open(pdf_filename, 'wb') as pdf_file:
                pdf_file.write(content)

            # Extract text from PDF
            text = extract_text_from_pdf(pdf_filename)
            write_to_file(f"PDF Content from {url}:\n{text}")
            os.remove(pdf_filename)

            # Process content for keywords
            process_scraped_content(text, url)
    except Exception as err:
        print(f"Error processing PDF ({url}): {err}")

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_filename):
    try:
        with pdfplumber.open(pdf_filename) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as err:
        print(f"Error extracting text from PDF: {err}")
        return ""

# Preprocess text (clean, remove stop words, and tokenize)
def preprocess_text(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return tokens

# Extract keywords using TF-IDF
def extract_keywords_tfidf(texts, max_features=50):
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer.get_feature_names_out()

# Extract keywords with a heuristic or regex
def extract_keywords_regex(text, custom_patterns=None):
    if not custom_patterns:
        custom_patterns = [r'\bcyber\w+', r'\b(policy|framework|encryption|threat|breach)\b']
    keywords = []
    for pattern in custom_patterns:
        keywords.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return set(keywords)

# Analyze keywords from text
def analyze_keywords(text):
    tokens = preprocess_text(text)
    tfidf_keywords = extract_keywords_tfidf([" ".join(tokens)])
    regex_keywords = extract_keywords_regex(" ".join(tokens))
    return set(tfidf_keywords).union(regex_keywords)

# Process and save scraped content keywords
def process_scraped_content(content, source_url):
    keywords = analyze_keywords(content)
    global output_counter
    keyword_filename = f"keywords{output_counter}.txt"
    with open(keyword_filename, 'a') as file:
        file.write(f"Keywords from {source_url}:\n")
        file.write("\n".join(keywords) + "\n")
        file.write("\n")  # Add a newline for readability
    return keywords

# Main asynchronous scraping function
async def scrape_and_parse(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_html(session, url) if not url.endswith('.pdf') else scrape_pdf(session, url, url.split('/')[-1]) for url in urls]
        await asyncio.gather(*tasks)

# Example URLs to scrape
urls_to_scrape = [
    "https://www.fcc.gov/cybersecurity-and-communications-reliability-division-public-safety-and-homeland-security-bureau",
    "https://www.cisa.gov/sites/default/files/2023-03/CISA_CPG_REPORT_v1.0.1_FINAL.pdf"
]

# Clear previous output files
for file in os.listdir("."):
    if file.startswith("output") or file.startswith("keywords"):
        os.remove(file)

# Run the scraper
asyncio.run(scrape_and_parse(urls_to_scrape))
