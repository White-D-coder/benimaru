import pandas as pd
import os
from typing import Dict, Any

class DataAnalyzer:
    @staticmethod
    async def analyze_file(file_path: str) -> Dict[str, Any]:
        """
        Reads a file and returns its metadata, schema, and basic statistics.
        """
        try:
            # Determine file type and read accordingly
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Extract basic info
            info = {
                "filename": os.path.basename(file_path),
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": []
            }

            # Analyze each column
            for col in df.columns:
                col_data = {
                    "name": col,
                    "type": str(df[col].dtype),
                    "null_count": int(df[col].isnull().sum()),
                    "sample_values": df[col].dropna().head(3).tolist()
                }
                
                # Add numeric stats if applicable
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_data["stats"] = {
                        "mean": float(df[col].mean()) if not df[col].empty else 0,
                        "min": float(df[col].min()) if not df[col].empty else 0,
                        "max": float(df[col].max()) if not df[col].empty else 0
                    }
                
                info["columns"].append(col_data)

            # Get top 5 rows as a preview
            info["preview"] = df.head(5).to_dict(orient="records")

            return info
        except Exception as e:
            return {"error": str(e)}
