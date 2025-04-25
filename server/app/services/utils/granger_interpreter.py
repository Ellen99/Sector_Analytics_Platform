import os
import openai

client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

def interpret_results_with_gpt(prompt):
    """
    Use GPT to interpret results using new OpenAI API.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                # "content": "You are a statistics expert. Your task is to analyze Granger causality test results between publication count and sector performance and give insights. We try to find out whether publication count can help predict market performance for near future. Respond briefly, clearly, and only mention which lag (1 month = 1 lag) shows the strongest predictive relationship based on p-values. Do not include generic explanations — just interpret the test result and recommend the best lag, instead of mentioning lag you can mention month so its easier to understand."},
                "content": "You are a data analyst providing insights from a Granger causality test. The goal is to determine whether the number of publications can help predict sector performance in the near future. Focus on identifying the most predictive time window (in months), based on the p-values. Respond clearly and briefly. Avoid technical terms like 'lag';  just refer to time in months. Do not explain what Granger causality is — just provide the insight and recommend the month with the strongest signal."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error using GPT API: {e}")
        return "Error interpreting results."
