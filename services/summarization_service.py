import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def summarize_text(transcript, department):
    prompt = f"Geef een samenvatting voor de afdeling {department} op basis van de volgende tekst: {transcript}"
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
