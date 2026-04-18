import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import sys
import traceback
from typing import Dict, Any

class CodeSandbox:
    @staticmethod
    async def execute_analysis(code: str, file_path: str) -> Dict[str, Any]:
        """
        Executes the generated code in a restricted environment and captures results.
        """
        # Load the data into the environment
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}

        # Prepare the restricted global environment
        # In a production environment, this should run in a Docker container.
        exec_globals = {
            "pd": pd,
            "plt": plt,
            "df": df,
            "result_data": None
        }

        # Redirect stdout to capture any print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            # Execute the code
            exec(code, exec_globals)
            
            # Reset stdout
            sys.stdout = old_stdout
            console_output = redirected_output.getvalue()

            # Process the results
            result = {
                "console_output": console_output,
                "data": None,
                "chart": None
            }

            # Capture result_data
            if exec_globals.get("result_data") is not None:
                res = exec_globals["result_data"]
                if isinstance(res, pd.DataFrame):
                    result["data"] = res.head(10).to_dict(orient="records")
                elif isinstance(res, pd.Series):
                    result["data"] = res.to_dict()
                else:
                    result["data"] = str(res)

            # Capture chart.png if it was created
            # Note: The code should use plt.savefig('chart.png')
            # For simplicity in this demo, we can check if anything was plotted
            if plt.get_fignums():
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
                result["chart"] = f"data:image/png;base64,{img_base64}"
                plt.close('all') # Clean up for the next run

            return result

        except Exception:
            sys.stdout = old_stdout
            return {"error": traceback.format_exc()}
