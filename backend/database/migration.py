import json
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from backend.database.postgres import engine, Base, SessionLocal
from backend.database.models import Candidate, CandidateJourney

def run_migrations():
    # 1. Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # 2. Inspect candidates table to see if new columns exist, and add if not
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("candidates")]
    
    new_cols = {
        "gender": "VARCHAR",
        "total_experience_years": "FLOAT",
        "highest_education_level": "VARCHAR"
    }
    
    with engine.begin() as conn:
        for col_name, col_type in new_cols.items():
            if col_name not in columns:
                print(f"Adding column {col_name} to table candidates...")
                conn.execute(text(f"ALTER TABLE candidates ADD COLUMN {col_name} {col_type}"))
                print(f"Column {col_name} added successfully.")
                
    # 3. Populate default values for existing candidates
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        genders = ["Male", "Female", "Non-binary", "Not Specified"]
        educations = ["Bachelors", "Masters", "PhD", "High School"]
        
        for c in candidates:
            updated = False
            if not c.gender:
                c.gender = genders[c.id % len(genders)]
                updated = True
            if c.total_experience_years is None:
                exp_list = []
                if c.experience:
                    try:
                        exp_list = json.loads(c.experience)
                    except Exception:
                        pass
                if exp_list:
                    c.total_experience_years = float(len(exp_list) * 2)
                else:
                    c.total_experience_years = float((c.id % 8) + 1.5)
                updated = True
            if not c.highest_education_level:
                edu_list = []
                if c.education:
                    try:
                        edu_list = json.loads(c.education)
                    except Exception:
                        pass
                if edu_list:
                    # Pick degree
                    c.highest_education_level = edu_list[0].get("degree", "Bachelors")
                else:
                    c.highest_education_level = educations[c.id % len(educations)]
                updated = True
                
            if updated:
                db.add(c)
                
            # Create default journey events if candidate doesn't have any
            journey_count = db.query(CandidateJourney).filter(CandidateJourney.candidate_id == c.id).count()
            if journey_count == 0:
                # Add Applied event
                db.add(CandidateJourney(
                    candidate_id=c.id,
                    stage="Applied",
                    status="Completed",
                    remarks="Candidate profile created.",
                    updated_by="System"
                ))
                
                # If they have been analyzed/scored, add Resume Parsed and AI Screening
                if c.match_score is not None:
                    db.add(CandidateJourney(
                        candidate_id=c.id,
                        stage="Resume Parsed",
                        status="Completed",
                        remarks="Resume text successfully parsed.",
                        updated_by="AI Agent"
                    ))
                    db.add(CandidateJourney(
                        candidate_id=c.id,
                        stage="AI Screening",
                        status="Completed",
                        remarks=f"AI Screening and Match Scoring complete (Score: {c.match_score}%).",
                        updated_by="AI Agent"
                    ))
                
                # If status is hired or rejected, add those events
                if c.status == "Hired":
                    db.add(CandidateJourney(
                        candidate_id=c.id,
                        stage="Hired",
                        status="Completed",
                        remarks="Candidate successfully hired.",
                        updated_by="System"
                    ))
                elif c.status == "Rejected":
                    db.add(CandidateJourney(
                        candidate_id=c.id,
                        stage="Rejected",
                        status="Completed",
                        remarks="Candidate profile rejected.",
                        updated_by="System"
                    ))
                elif c.status != "New" and c.status != "Applied":
                    db.add(CandidateJourney(
                        candidate_id=c.id,
                        stage=c.status,
                        status="Completed",
                        remarks=f"Moved to {c.status} stage.",
                        updated_by="System"
                    ))
        db.commit()
    except Exception as e:
        print(f"Error during migration populating: {e}")
        db.rollback()
    finally:
        db.close()
