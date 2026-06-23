import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine, Base, SessionLocal
from app.roles_database import seed_roles
from app import models
from app.agents import CoordinatorAgent

def test_database_and_agents():
    print("=== Testing Database & Agents (Phase 2 Verification) ===")
    
    # 1. Recreate tables
    print("Recreating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed database
    print("Seeding database...")
    db = SessionLocal()
    try:
        seed_roles(db)
        
        # 3. Check role count
        role_count = db.query(models.CareerRole).count()
        print(f"Total seeded roles: {role_count}")
        assert role_count >= 30, f"Expected at least 30 roles, got {role_count}"
        
        # 4. Fetch standard role
        frontend_role = db.query(models.CareerRole).filter(models.CareerRole.name == "Frontend Developer").first()
        print(f"Sample Role Found: {frontend_role.name}")
        print(f"Description: {frontend_role.description}")
        print(f"Required Skills: {frontend_role.required_skills}")
        print(f"Beginner steps: {len(frontend_role.beginner_roadmap)}")
        print(f"Intermediate steps: {len(frontend_role.intermediate_roadmap)}")
        print(f"Advanced steps: {len(frontend_role.advanced_roadmap)}")
        
        # 5. Test Coordinator Flow
        coordinator = CoordinatorAgent()
        
        mock_resume_text = """
        John Doe
        john.doe@example.com
        Skills: Python, Git, HTML, CSS, JavaScript, React.
        
        Experience:
        Junior Frontend Developer | Tech Labs | 2024 - Present
        Developed responsive web layouts.
        
        Education:
        B.S. in Computer Science | State College
        """
        
        print("\nProcessing mock resume...")
        db_resume = coordinator.process_new_resume(db, mock_resume_text, "test_resume.txt")
        print(f"Saved Resume ID: {db_resume.id}")
        print(f"Parsed profile: {db_resume.parsed_profile}")
        
        print("\nPerforming career analysis for Frontend Developer...")
        analysis = coordinator.perform_career_analysis(db, db_resume.id, "Frontend Developer")
        print(f"Overall Fit Score: {analysis.overall_fit_score}%")
        print(f"Matched Skills: {analysis.current_skills}")
        print(f"Required Skills: {analysis.required_skills}")
        print(f"Missing Gaps: {analysis.skill_gaps}")
        print(f"Recommendations: {analysis.recommendations}")
        
        # 6. Check roadmap generated
        roadmap = db.query(models.LearningRoadmap).filter(models.LearningRoadmap.analysis_id == analysis.id).first()
        print(f"\nGenerated Roadmap Steps count: {len(roadmap.steps)}")
        print(f"Roadmap Duration: {roadmap.estimated_duration}")
        for step in roadmap.steps:
            print(f" - Step {step['step_number']}: {step['topic']} ({step['duration']})")
        
        print("\nAll tests passed successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_database_and_agents()
