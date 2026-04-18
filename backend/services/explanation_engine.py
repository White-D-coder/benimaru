import os
from openai import AsyncOpenAI
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ExplanationEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"

    async def explain_results(self, query: str, result_data: Any) -> str:
        """
        Takes the raw output of the analysis and converts it into a human-readable insight.
        """
        system_prompt = f"""
        You are a Data Insight Expert. 
        A user asked a question about their data, and an analysis was performed.
        Your task is to take the raw results and provide a clear, concise, and insightful explanation.
        
        RULES:
        1. Keep it professional and direct.
        2. Highlight the most important numbers or trends.
        3. If there's an error in the data, explain what might have gone wrong.
        """
        
        prompt = f"""
        USER QUESTION: {query}
        RAW ANALYSIS RESULTS: {str(result_data)}
        
        Provide a 2-3 sentence summary of the insights.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"The analysis was successful, but I couldn't generate a summary. Raw results: {str(result_data)}"
