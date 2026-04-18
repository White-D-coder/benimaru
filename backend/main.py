from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import pandas as pd
from dotenv import load_dotenv

from services.data_service import DataService
from services.llm_service import LLMService
from services.executor_service import ExecutorService

# Load environment variables
load_dotenv()

app = FastAPI(title="Data Analyst Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Services
data_service = DataService(UPLOAD_DIR)
llm_service = LLMService() # Assumes OPENAI_API_KEY is in environment
executor_service = ExecutorService()

@app.get("/")
async def root():
    return {"message": "Data Analyst Assistant API is running"}

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV/Excel file and return its schema.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Unsupported file format.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        data_profile = data_service.get_schema(file.filename)
        return {
            "filename": file.filename,
            "status": "uploaded",
            "data_profile": data_profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def process_query(
    filename: str = Body(...),
    query: str = Body(...)
):
    """
    Process a natural language query against a specific dataset.
    """
    file_path = data_service.get_file_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found. Please upload it first.")

    try:
        # 1. Get Schema
        schema = data_service.get_schema(filename)

        # 2. Generate Code
        code = llm_service.generate_analysis_code(query, schema, filename)

        # 3. Load Data
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # 4. Execute Code
        result = executor_service.execute_code(code, df)

        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
                "generated_code": code
            }

        return {
            "success": True,
            "explanation": result["explanation"],
            "data": result["data"],
            "chart": result["chart"],
            "generated_code": code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
