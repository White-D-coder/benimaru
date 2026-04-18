import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os
from typing import Dict, Any, Tuple

class ExecutorService:
    def __init__(self):
        pass

    def execute_code(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes the generated code in a safe environment.
        """
        # Prepare the local environment for execution
        local_vars = {
            'df': df,
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'final_result': None
        }

        # Clear any existing plots
        plt.clf()
        plt.close('all')

        try:
            # Execute the code
            exec(code, {}, local_vars)
            
            final_result = local_vars.get('final_result', "No result variable set in code.")
            
            # Check for generated plot
            plot_base64 = None
            if os.path.exists('output_plot.png'):
                with open('output_plot.png', 'rb') as f:
                    plot_base64 = base64.b64encode(f.read()).decode('utf-8')
                os.remove('output_plot.png')

            return {
                "success": True,
                "result": final_result,
                "plot_base64": plot_base64
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code_attempted": code
            }
