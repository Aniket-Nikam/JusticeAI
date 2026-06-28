import logging
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List

# Import Config, DB, and AI Service
from config import settings
from database import engine, Base, get_db
from models.case_model import CaseAnalysis
from services.ai_service import analyze_case

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JusticeAI API")

# Hardened CORS using environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Validation: Max 10000 chars to prevent DoS
class CaseRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=10000, description="The factual description of the case")

class AnalysisResponse(BaseModel):
    report: str

class CaseHistoryResponse(BaseModel):
    id: int
    description: str
    report: str
    timestamp: str

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_case_endpoint(request: CaseRequest, db: Session = Depends(get_db)):
    logger.info("Received analysis request.")
    try:
        # Retrieve past learnings for consistency (fetch last 3 cases)
        past_cases = db.query(CaseAnalysis).order_by(CaseAnalysis.id.desc()).limit(3).all()
        previous_learnings = ""
        if past_cases:
            previous_learnings = "Here are summaries of the last 3 cases processed for consistency:\n"
            for c in past_cases:
                previous_learnings += f"- Case {c.id}: {c.description[:200]}... -> Report Extract: {c.report[:300]}...\n"
        else:
            previous_learnings = "No prior cases in the database yet. Establish a baseline."

        # Run the 2-step AI pipeline
        report = analyze_case(request.description, previous_learnings)
        
        # Save to database
        db_case = CaseAnalysis(description=request.description, report=report)
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        
        logger.info(f"Successfully processed and saved Case ID {db_case.id}")
        return AnalysisResponse(report=report)
        
    except Exception as e:
        # ai_service.py already sanitizes the error, so we can pass it to the frontend
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Pagination implemented via limit and offset
@app.get("/api/v1/cases", response_model=List[CaseHistoryResponse])
async def get_case_history(
    limit: int = Query(20, ge=1, le=100), 
    offset: int = Query(0, ge=0), 
    db: Session = Depends(get_db)
):
    cases = db.query(CaseAnalysis).order_by(CaseAnalysis.id.desc()).offset(offset).limit(limit).all()
    return [{"id": c.id, "description": c.description, "report": c.report, "timestamp": c.timestamp.isoformat()} for c in cases]

@app.delete("/api/v1/cases/{case_id}")
async def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(CaseAnalysis).filter(CaseAnalysis.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"message": "Case deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
