import os
from openai import OpenAI
from typing import Dict, Any

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key not found.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_analysis_code(self, query: str, schema: Dict[str, Any], filename: str) -> str:
        """
        Generates Python/Pandas code for a given query and schema.
        """
        system_prompt = f"""
You are a senior data analyst and Python expert.
Your task is to generate Python code using the pandas library to answer a user's data question.
The data is stored in a file named '{filename}'.
The dataframe is named 'df'.

DATASET SCHEMA:
Columns: {schema['columns']}
Data Types: {schema['dtypes']}
Sample Data: {schema['sample_data']}

RULES:
1. Only return the Python code. No explanations, no markdown code blocks, just raw code.
2. The code should assume the dataframe 'df' is already loaded.
3. If the user asks for a visualization, use matplotlib or seaborn. Save the plot to 'output_plot.png'.
4. Store the final textual answer in a variable named 'final_result'.
5. If the query results in a table or subset of data, store the DataFrame in a variable named 'data_result'.
6. Do not import any libraries other than pandas, numpy, matplotlib, or seaborn.
7. Be concise and efficient.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o", # Or any other suitable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0
        )

        code = response.choices[0].message.content.strip()
        
        # Clean up code if it contains markdown blocks
        if code.startswith("```python"):
            code = code.replace("```python", "").replace("```", "").strip()
        elif code.startswith("```"):
            code = code.replace("```", "").strip()
            
        return code
