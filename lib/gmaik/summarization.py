import openai

# OpenAI API credentials
OPENAI_API_KEY  = ""
def summarize_text(subject, text):
    openai.api_key = OPENAI_API_KEY
    prompt = f"Subject: {subject}\nSnippet: {text}\n\nSummarize:"
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=100,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()
