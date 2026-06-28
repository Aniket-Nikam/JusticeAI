import logging
import json
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from backend.config import settings
from backend.api.models.base import engine, Base, SessionLocal
from backend.api.models.schema import Case, Analysis, Citation, Challenge
from backend.engine.reasoning_pipeline import ReasoningPipeline

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="JusticeAI API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = ReasoningPipeline()

# Pydantic Schemas for API
class CaseSubmitRequest(BaseModel):
    jurisdiction: str
    crime_type: str
    defendant_profile: str
    description: str
    counts: List[dict] = []

class AnalysisResponseModel(BaseModel):
    id: str
    case_id: str
    verdict_classification: str
    confidence_score: int
    recommended_range_min_months: float
    recommended_range_max_months: float
    summary: str
    layer1_result: Any
    layer2_result: Any
    layer3_result: Any
    layer4_result: Any
    layer5_result: Any
    full_reasoning_chain: str
    citations: List[Any] = []

class ChallengeSubmitRequest(BaseModel):
    layer_challenged: int
    challenge_text: str

@app.post("/api/v1/analyze", response_model=AnalysisResponseModel)
async def analyze_case_endpoint(request: CaseSubmitRequest, db: Session = Depends(get_db)):
    logger.info("Received analysis request v2.")
    try:
        # Convert request to dict for pipeline
        case_dict = request.model_dump()
        
        # Fetch historical Agentic Memory (past challenges for this crime/jurisdiction)
        past_cases = db.query(Case).filter(
            (Case.crime_type == request.crime_type) | (Case.jurisdiction == request.jurisdiction)
        ).all()
        past_case_ids = [c.id for c in past_cases]
        
        historical_challenges = []
        if past_case_ids:
            past_analyses = db.query(Analysis).filter(Analysis.case_id.in_(past_case_ids)).all()
            past_analysis_ids = [a.id for a in past_analyses]
            if past_analysis_ids:
                challenges = db.query(Challenge).filter(Challenge.analysis_id.in_(past_analysis_ids)).all()
                for ch in challenges:
                    historical_challenges.append({
                        "layer": ch.layer_challenged,
                        "text": ch.challenge_text
                    })
        
        # Run Reasoning Pipeline
        parsed_result = await pipeline.analyze(case_dict, historical_challenges)
        
        # Save Case to DB
        db_case = Case(
            jurisdiction=request.jurisdiction,
            crime_type=request.crime_type,
            crime_description=request.description,
            defendant_mental_health=request.defendant_profile,
            status="completed"
        )
        db.add(db_case)
        db.flush()
        
        # Save Analysis to DB
        db_analysis = Analysis(
            case_id=db_case.id,
            confidence_score=parsed_result.get("confidence_score", 0),
            confidence_breakdown=parsed_result.get("confidence_breakdown", {}),
            layer1_result=parsed_result.get("layer1_result", {}),
            layer2_result=parsed_result.get("layer2_result", {}),
            layer3_result=parsed_result.get("layer3_result", {}),
            layer4_result=parsed_result.get("layer4_result", {}),
            layer5_result=parsed_result.get("layer5_result", {}),
            verdict_classification=parsed_result.get("verdict_classification", "ANOMALOUS"),
            recommended_range_min_months=parsed_result.get("recommended_range_min_months", 0),
            recommended_range_max_months=parsed_result.get("recommended_range_max_months", 0),
            full_reasoning_chain=parsed_result.get("full_reasoning_chain", ""),
            summary=parsed_result.get("summary", "")
        )
        db.add(db_analysis)
        db.flush()
        
        # Save Citations
        citations = parsed_result.get("citations", [])
        for cit in citations:
            db_citation = Citation(
                analysis_id=db_analysis.id,
                layer=cit.get("layer", 1),
                source_url=cit.get("source_url", ""),
                source_title=cit.get("source_title", ""),
                source_type=cit.get("source_type", ""),
                excerpt=cit.get("excerpt", "")
            )
            db.add(db_citation)
        
        db.commit()
        db.refresh(db_analysis)
        
        response_data = {
            "id": db_analysis.id,
            "case_id": db_case.id,
            "verdict_classification": db_analysis.verdict_classification,
            "confidence_score": db_analysis.confidence_score,
            "recommended_range_min_months": db_analysis.recommended_range_min_months,
            "recommended_range_max_months": db_analysis.recommended_range_max_months,
            "summary": db_analysis.summary,
            "layer1_result": db_analysis.layer1_result,
            "layer2_result": db_analysis.layer2_result,
            "layer3_result": db_analysis.layer3_result,
            "layer4_result": db_analysis.layer4_result,
            "layer5_result": db_analysis.layer5_result,
            "full_reasoning_chain": db_analysis.full_reasoning_chain,
            "citations": citations
        }
        return response_data
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/cases")
async def get_case_history(db: Session = Depends(get_db)):
    # Quick endpoint to fetch history
    cases = db.query(Case).order_by(Case.submitted_at.desc()).all()
    res = []
    for c in cases:
        # Get first analysis
        analysis = db.query(Analysis).filter(Analysis.case_id == c.id).first()
        res.append({
            "id": c.id,
            "crime_type": c.crime_type,
            "jurisdiction": c.jurisdiction,
            "submitted_at": c.submitted_at.isoformat(),
            "verdict": analysis.verdict_classification if analysis else "N/A",
            "confidence": analysis.confidence_score if analysis else 0
        })
    return res

@app.post("/api/v1/analyses/{analysis_id}/challenge")
async def submit_challenge(analysis_id: str, request: ChallengeSubmitRequest, db: Session = Depends(get_db)):
    logger.info(f"Received Agentic Memory Challenge for analysis {analysis_id}")
    db_challenge = Challenge(
        analysis_id=analysis_id,
        layer_challenged=request.layer_challenged,
        challenge_text=request.challenge_text,
        status="open"
    )
    db.add(db_challenge)
    db.commit()
    return {"status": "success", "message": "Challenge added to Agentic Memory"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
