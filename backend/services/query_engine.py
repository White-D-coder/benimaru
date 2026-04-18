import os
from openai import AsyncOpenAI
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class QueryEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # High reasoning capability for code generation

    async def generate_code(self, query: str, data_profile: Dict[str, Any]) -> str:
        """
        Generates Python/Pandas code based on a natural language query and data schema.
        """
        schema_context = self._format_schema(data_profile)
        
        system_prompt = f"""
        You are a world-class Data Analyst Assistant. 
        Your task is to write Python code using the pandas library to answer the user's question based on their data.
        
        DATA CONTEXT:
        The user has uploaded a file named '{data_profile['filename']}'.
        SCHEMA:
        {schema_context}
        
        RULES:
        1. Only use the 'pandas', 'matplotlib.pyplot', and 'seaborn' libraries.
        2. Assume the data is loaded into a variable named 'df'.
        3. Do NOT use any external file paths except 'data.csv' (which will be provided in the sandbox).
        4. Your code must perform the analysis and save the primary result into a variable named 'result_data'.
        5. If a visualization is requested, save the plot to 'chart.png' using plt.savefig('chart.png').
        6. Return ONLY the Python code. No preamble, no explanation, no markdown backticks.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1  # Low temperature for deterministic code
            )
            
            code = response.choices[0].message.content.strip()
            # Clean up potential markdown backticks if the model ignores instructions
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()
                
            return code
        except Exception as e:
            return f"# Error generating code: {str(e)}"

    def _format_schema(self, data_profile: Dict[str, Any]) -> str:
        """
        Formats the data profile into a readable string for the LLM prompt.
        """
        lines = []
        for col in data_profile["columns"]:
            line = f"- {col['name']} ({col['type']}): Sample values: {col['sample_values']}"
            if "stats" in col:
                line += f" | Mean: {col['stats']['mean']:.2f}"
            lines.append(line)
        return "\n".join(lines)
