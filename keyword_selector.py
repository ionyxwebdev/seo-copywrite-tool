import openai
import os
import json

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
You are an SEO assistant for the {industry} industry. Select one primary keyword, two secondary keywords, 
and four long-tail keywords from the given data based on these criteria:
- Secondary: Moderate search volume with slightly lower CPC and competition.
- Long-Tail: Lower search volume but specific to the niche and with low competition.
- Not brand related or company name
- Commercial Intent, where user is looking to purchase a service or product
- Not a course or related to education
- Be sensitive to potentially inappropriate themes
- Must logically be related to the company and the service it provides. This is important.

Data:
{keywords}

Output the result in JSON format with this structure:
{{
  "primary_keyword": "<primary_keyword>",
  "secondary_keywords": ["<secondary_keyword1>", "<secondary_keyword2>"],
  "long_tail_keywords": ["<long_tail_keyword1>", "<long_tail_keyword2>", "<long_tail_keyword3>", "<long_tail_keyword4>"]
}}
"""

def select_keywords(keywords, industry="general"):
    # Format the keywords data into JSON for the prompt
    formatted_data = json.dumps(keywords, indent=2)
    prompt = PROMPT_TEMPLATE.format(industry=industry, keywords=formatted_data)

    try:
        # Call OpenAI's chat completion endpoint
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful SEO assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Extract and parse the JSON response
        result = response.choices[0].message["content"].strip()
        return json.loads(result)  # Convert the output string to JSON
    except Exception as e:
        print(f"Error: {e}")
        return None
