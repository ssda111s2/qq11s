from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re

app = Flask(__name__)

def sanitize_query(query):
    # Remove non-ASCII characters (only keep English characters)
    sanitized_query = re.sub(r'[^A-Za-z0-9\s]', '', query)
    return sanitized_query

def search_web(query):
    # Sanitize the query to ensure it only contains English characters
    sanitized_query = sanitize_query(query)
    
    # Perform a Google search and get the top result URL
    search_results = list(search(sanitized_query, num_results=1))  # Convert the generator to a list
    
    # If there are no search results, return a message
    if not search_results:
        return "Sorry, no search results found."
    
    # Get the first result's URL
    url = search_results[0]
    
    # Send the GET request to fetch the page content
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Sorry, I couldn't retrieve the content from the page."
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to find the first few paragraphs (usually in the introduction)
    paragraphs = soup.find_all('p')
    
    # Combine the first few paragraphs to form a shortened answer
    answer = ""
    for p in paragraphs[:3]:  # Get the first three paragraphs
        answer += p.get_text()
    
    # Shorten the text to a reasonable length (e.g., 500 characters)
    if len(answer) > 500:
        answer = answer[:500] + "..."
    
    # If we couldn't find any paragraphs, return a default message
    if not answer.strip():
        return "Sorry, I couldn't extract useful information from the page."
    
    return answer.strip()

@app.route('/search', methods=['GET'])
def search_route():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is missing.'}), 400
    
    answer = search_web(query)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
