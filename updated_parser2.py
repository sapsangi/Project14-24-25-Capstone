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

# Ensure SpaCy model is available
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load('en_core_web_sm')

# Utility function to write output to a numbered file
def write_to_file(content, prefix="output"):
    global output_counter
    directory = "text-files"
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"{prefix}{output_counter}.txt")

    with open(filename, 'a', encoding='utf-8') as file:
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
            text_content = soup.get_text(" ", strip=True)
            write_to_file(f"HTML Content from {url}:\n{text_content}")

            # Extract PDF links
            pdf_links = [link['href'] for link in soup.find_all('a', href=True) if link['href'].endswith('.pdf')]
            for pdf_url in pdf_links:
                if not pdf_url.startswith("http"):
                    base_url = "/".join(url.split("/")[:3])
                    pdf_url = base_url + pdf_url
                await scrape_pdf(session, pdf_url, pdf_url.split('/')[-1])

            # Process content for keywords
            #process_scraped_content(text_content, url)
    except Exception as err:
        print(f"Error processing HTML ({url}): {err}")

# Function to download and parse PDF content
async def scrape_pdf(session, url, pdf_filename):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()

            pdf_path = os.path.join("text-files", pdf_filename)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(content)

            # Extract text from PDF
            text = extract_text_from_pdf(pdf_path)
            write_to_file(f"PDF Content from {url}:\n{text}")
            os.remove(pdf_path)

            # Process content for keywords
            #process_scraped_content(text, url)
    except Exception as err:
        print(f"Error processing PDF ({url}): {err}")

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_filename):
    try:
        text = ""
        with pdfplumber.open(pdf_filename) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text
        return text
    except Exception as err:
        print(f"Error extracting text from PDF {pdf_filename}: {err}")
        return ""

# Preprocess text
def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return tokens

# Extract keywords using TF-IDF
def extract_keywords_tfidf(texts, max_features=50):
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer.get_feature_names_out()

# Extract keywords with regex
def extract_keywords_regex(text, custom_patterns=None):
    if not custom_patterns:
        custom_patterns = [r'\\bcyber\\w+', r'\\b(policy|framework|encryption|threat|breach)\\b']
    keywords = []
    for pattern in custom_patterns:
        keywords.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return set(keywords)

# Analyze keywords
def analyze_keywords(text):
    tokens = preprocess_text(text)
    tfidf_keywords = extract_keywords_tfidf([" ".join(tokens)])
    regex_keywords = extract_keywords_regex(" ".join(tokens))
    return set(tfidf_keywords).union(regex_keywords)

# Process and save scraped content keywords
def process_scraped_content(content, source_url):
    keywords = analyze_keywords(content)
    global output_counter
    keyword_filename = os.path.join("text-files", f"keywords{output_counter}.txt")
    with open(keyword_filename, 'a', encoding='utf-8') as file:
        file.write(f"Keywords from {source_url}:\n")
        file.write("\\n".join(keywords) + "\\n\\n")
    return keywords

# Main asynchronous scraping function
async def scrape_and_parse(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_html(session, url) if not url.endswith('.pdf') else scrape_pdf(session, url, url.split('/')[-1]) for url in urls]
        await asyncio.gather(*tasks)

# Example URLs to scrape
urls_to_scrape = [
    "https://www.cisa.gov/resources-tools/programs/emergency-communications-policy-and-planning".
    "https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/communications-sector",
    "https://www.fcc.gov/CSRICReports",
    "https://www.cisa.gov/resources-tools/resources/enhanced-visibility-and-hardening-guidance-communications-infrastructure"
    "https://www.ntia.gov/page/information-quality-guidelines"
    "https://www.federalregister.gov/documents/2024/09/10/2024-19028/implications-of-artificial-intelligence-technologies-on-protecting-consumers-from-unwanted-robocalls", 
    "https://www.fcc.gov/wireless-telecommunications", 
    "https://www.fcc.gov/communications-business-opportunities/cybersecurity-advisories"
    "https://www.fcc.gov/cybersecurity-and-communications-reliability-division-public-safety-and-homeland-security-bureau"
    "https://www.fcc.gov/media/customer-service-standards",
    "https://www.cisa.gov/cybersecurity-performance-goals-cpgs",
    "https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/communications-sector",
    "https://www.pwc.com/us/en/technology/alliances/microsoft/cybersecurity.html?WT.mc_id=CT3-PL300-DM1-TR1-LS2-SC_XS-BM-CN_OTHER-AlliancesSearch&gclid=Cj0KCQjwgrO4BhC2ARIsAKQ7zUkrMGYHLRyttHS2uuYhTWVOk8GpyL-QmVP-feTuFL9L2JB_L1iK5MQaAhNoEALw_wcB&gclsrc=aw.ds",
    "https://cra.exein.io/?gad_source=1&gclid=Cj0KCQjwgrO4BhC2ARIsAKQ7zUkKKo83YImjM2w1wN_2jXG1E9vS55qFS9OS6FkEArdJixN1wpFk98MaAi4SEALw_wcB",
    "https://resources.nvidia.com/en-us-ai-in-telco/telco-report-state-o",
    "https://www.nist.gov/cyberframework",
    "https://www.legalitysimplified.com/new-rules-on-telecom-cybersecurity-what-you-need-to-know/",
    "https://www.gao.gov/topics/telecommunications",
    "https://guides.loc.gov/telecommunications-industry/laws-regulations" 
 
]

# Clear previous output files
if os.path.exists("text-files"):
    for file in os.listdir("text-files"):
        if file.startswith("output") or file.startswith("keywords"):
            os.remove(os.path.join("text-files", file))
else:
    os.makedirs("text-files")

# Run the scraper
if __name__ == "__main__":
    asyncio.run(scrape_and_parse(urls_to_scrape))
    print("Scraping complete. Check the 'text-files' directory for outputs.")
