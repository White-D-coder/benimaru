import pandas as pd
import os
from typing import Dict, Any, List

class DataService:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir

    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.upload_dir, filename)

    def get_schema(self, filename: str) -> Dict[str, Any]:
        """
        Extract schema and metadata from a CSV/Excel file.
        """
        file_path = self.get_file_path(filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {filename} not found.")

        # Read only a sample to get types and columns
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=5)
        else:
            df = pd.read_excel(file_path, nrows=5)

        data_profile = {
            "columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
            "row_count": self._estimate_row_count(file_path),
            "column_count": len(df.columns),
            "sample_data": df.head(3).to_dict(orient='records')
        }
        return data_profile

    def _estimate_row_count(self, file_path: str) -> int:
        # Simple estimation for CSVs
        if file_path.endswith('.csv'):
            with open(file_path, 'rb') as f:
                return sum(1 for _ in f) - 1  # Subtract header
        return -1 # For Excel, we'd need to load more or just return -1
