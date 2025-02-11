import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

def fetch_webpage(url):
    """Fetch webpage content."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return None

def extract_text(html):
    """Extract full content from <span class='expert-title-sentence'>."""
    soup = BeautifulSoup(html, "html.parser")
    spans = [span.get_text(strip=True) for span in soup.find_all("span", class_="expert-title-sentence")]
    return "\n".join(spans)

def extract_names_and_orgs(text):
    """Extract names and organizations from text, with or without titles."""
    people = []
    lines = text.split('\n')

    for line in lines:
        match = re.match(
            r'(?:(?:Dr|Professor|Associate Professor|Mr|Ms|Distinguished Professor|Honorary Fellow|Adjunct Associate Professor|Adjunct Professor|Adjunct Assoc Prof)\s+)?'  # Title is now optional
            r'([A-Za-z-\.\s]+?)\s+is.*?(?:at|from|of)\s+([A-Za-z\s\-&]+)',  # Name + Organization
            line
        )
        if match:
            name = match.group(1).strip()
            organization = match.group(2).strip()
            people.append((name, organization))

    return people

def generate_boolean_search(people):
    """Generate a Boolean search query."""
    boolean_parts = []
    name_only_parts = []
    
    for name, org in people:
        first_name = name.split()[0]
        search_part = f'(medium:Radio AND (("{name}" OR (("{first_name}") NEAR/10 ("{org}")))))'
        boolean_parts.append(search_part)
        name_only_parts.append(f'"{name}"')
    
    boolean_query = ' OR \n'.join(boolean_parts)
    name_only_query = ' OR '.join(name_only_parts)
    
    return boolean_query, name_only_query

# Streamlit UI
st.title("Boolean Search Generator")

url = st.text_input("Enter Webpage URL")

if st.button("Generate Boolean Search"):
    html = fetch_webpage(url)
    if html:
        text = extract_text(html)
        people = extract_names_and_orgs(text)
        boolean_query, name_only_query = generate_boolean_search(people)

        st.subheader("Boolean Search Query")
        st.code(boolean_query, language="text")

        st.subheader("Name-Only Boolean Query")
        st.code(name_only_query, language="text")
    else:
        st.error("Failed to fetch webpage.")
