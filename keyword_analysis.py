from flask import Flask, request, jsonify, render_template
from flask_basicauth import BasicAuth
import requests
import os
from keyword_selector import select_keywords

# Initialize Flask app
app = Flask(__name__)

# Basic Authentication Configuration
app.config['BASIC_AUTH_USERNAME'] = 'ionyxdigital'
app.config['BASIC_AUTH_PASSWORD'] = '2349!dhjudHD'
basic_auth = BasicAuth(app)

# SEMrush API details
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")  # No fallback, should be set in Heroku Config Vars

def get_seo_keywords(keyword):
    """
    Fetches related keyword suggestions from SEMrush for a given keyword.
    """
    if not SEMRUSH_API_KEY:
        raise ValueError("SEMRUSH_API_KEY is not set. Please configure it in Heroku Config Vars.")

    params = {
        'type': 'phrase_related',
        'key': SEMRUSH_API_KEY,
        'phrase': keyword,
        'database': 'us',  # Change 'us' to your desired database, e.g., 'au' for Australia
        'export_columns': 'Ph,Nq,Cp,Co,Nr'  # Columns: Phrase, Search Volume, CPC, Competition, Number of Results
    }

    response = requests.get('https://api.semrush.com/', params=params)
    if response.status_code == 200:
        try:
            data = response.text.splitlines()
            headers = data[0].split(';')  # Extract headers from the first line
            keywords = [
                {
                    "Keyword": row.split(';')[0],
                    "Search Volume": row.split(';')[1],
                    "CPC": row.split(';')[2],
                    "Competition": row.split(';')[3],
                    "Number of Results": row.split(';')[4],
                }
                for row in data[1:]
            ]
            return keywords
        except Exception as e:
            print(f"Error parsing SEMrush response: {e}")
            return []
    else:
        print(f"SEMrush API error: {response.status_code}")
        return []

@app.after_request
def add_header(response):
    """
    Disable caching for all responses.
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
@basic_auth.required  # Protect this route with Basic Auth
def home():
    """
    Render the HTML form for keyword analysis.
    """
    return render_template('keyword-analysis.html')

@app.route('/analyze', methods=['POST'])
@basic_auth.required  # Protect this route with Basic Auth
def analyze_keywords():
    """
    Handle keyword analysis requests, fetch SEMrush data, and process with OpenAI.
    """
    try:
        # Retrieve JSON data from the request
        data = request.json
        company_name = data.get('companyName', '').strip()
        industry = data.get('industry', '').strip()
        keywords = data.get('keywords', '').strip().splitlines()

        if not company_name or not industry or not keywords:
            return jsonify({"error": "All fields are required (company name, industry, and keywords)."}), 400

        # Prepare the output
        all_processed_keywords = {}

        for keyword in keywords:
            keyword = keyword.strip()
            if not keyword:
                continue

            suggestions = get_seo_keywords(keyword)

            if suggestions:
                # Pass the industry to the select_keywords function
                processed_keywords = select_keywords(suggestions, industry=industry)
                if processed_keywords:
                    # Ensure processed_keywords retains structured format
                    all_processed_keywords[keyword] = {
                        "primary_keyword": processed_keywords.get('primary_keyword'),
                        "secondary_keywords": processed_keywords.get('secondary_keywords', []),
                        "long_tail_keywords": processed_keywords.get('long_tail_keywords', [])
                    }
                else:
                    all_processed_keywords[keyword] = {"error": "Unable to process keyword suggestions"}
            else:
                all_processed_keywords[keyword] = {"error": "No suggestions found for this keyword"}

        # Prepare the response
        response = {
            "company_name": company_name,
            "industry": industry,
            "processed_keywords": all_processed_keywords
        }

        return jsonify(response)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
