import openai
import os
import json

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
SEO Keyword Selection Guide for {Industry}

Choose 2 secondary and 4 long-tail keywords based on these rules:

Secondary Keywords (2)
Moderate search volume (not overly competitive).
Lower CPC & competition for cost-effectiveness.
Strong commercial intent (purchase-driven).
Industry-relevant (aligned with services/products).
No brand names, competitors, or educational terms.
Must be appropriate and suitable for all audiences.
Long-Tail Keywords (4)
Lower search volume but highly niche-specific.
Low competition with strong commercial intent.
Directly related to the business’s offerings.
No “near me,” brand names, or competitors.
Ensure all keywords match the business’s industry and service intent.

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
