from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI(title="Data Analyst Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory for uploaded datasets
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Data Analyst Assistant API is running"}

from services.data_analyzer import DataAnalyzer

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload and analyze a CSV/Excel file.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Unsupported file format.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze the data immediately
    analysis_results = await DataAnalyzer.analyze_file(file_path)
    
    if "error" in analysis_results:
        raise HTTPException(status_code=500, detail=analysis_results["error"])
        
    return {
        "status": "success",
        "data_profile": analysis_results
    }

from pydantic import BaseModel
from services.query_engine import QueryEngine
from services.sandbox import CodeSandbox
from services.explanation_engine import ExplanationEngine

# Initialize services
query_engine = QueryEngine()
sandbox = CodeSandbox()
explanation_engine = ExplanationEngine()

class QueryRequest(BaseModel):
    filename: str
    query: str

@app.post("/query")
async def process_query(request: QueryRequest):
    """
    The main analysis loop: Interpret -> Execute -> Explain.
    """
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # 1. Profile the data (needed for prompt context)
    profile = await DataAnalyzer.analyze_file(file_path)
    
    # 2. Generate code
    code = await query_engine.generate_code(request.query, profile)
    
    # 3. Execute in Sandbox
    execution_result = await sandbox.execute_analysis(code, file_path)
    
    if "error" in execution_result:
        return {
            "status": "error",
            "error": execution_result["error"],
            "generated_code": code
        }

    # 4. Generate human-readable explanation
    explanation = await explanation_engine.explain_results(request.query, execution_result["data"])
    
    return {
        "status": "success",
        "query": request.query,
        "explanation": explanation,
        "data": execution_result["data"],
        "chart": execution_result["chart"],
        "generated_code": code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
