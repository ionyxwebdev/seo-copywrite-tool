import openai
import os
import json

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
You are a SEO Keyword master. You have to choose 2 secondary and 4 long-tail keywords with the following guide.
Keyword Selection Guidelines for {Industry}
Secondary Keywords (2)
Moderate search volume: Not too high (to avoid extreme competition) but still substantial enough to attract traffic.
Lower CPC & competition: Compared to high-volume keywords, ensuring a balance between visibility and cost-efficiency.
Commercial intent: Indicates users are actively looking to purchase a service or product.
Industry relevance: Must logically align with the company's services/products and customer search behavior.
Excludes brand/company names: No keywords tied to specific businesses or competitors.
Not education-related: Avoids keywords about courses, certifications, or training.
Avoids inappropriate themes: Must be suitable for all audiences and free from misleading, controversial, or sensitive topics.
Long-Tail Keywords (4)
Lower search volume: But highly specific to the niche, capturing targeted intent.
Low competition: Easier to rank for while still maintaining commercial value.
Commercial intent: Indicates the user is closer to making a purchase or booking a service.
Industry-specific: Must be directly relevant to the business and its offerings.
Excludes "near me": To maintain broader, location-agnostic reach.
No brand names or competitors: Keeps focus on generic but high-intent search queries.

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
