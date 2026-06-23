import os
import json
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from .. import models

# Optional Gemini integration
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

logger = logging.getLogger(__name__)

# Predefined role mappings for Phase 1 rule-based fallback
STANDARD_ROLES = {
    "full stack developer": [
        "React", "Node.js", "Python", "SQL", "Git", "HTML", "CSS", "TypeScript", "REST API", "Docker"
    ],
    "data scientist": [
        "Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "Deep Learning", "TensorFlow", "Statistics", "Data Visualization"
    ],
    "devops engineer": [
        "Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git", "Terraform", "Python", "Jenkins", "Ansible"
    ],
    "backend developer": [
        "Python", "FastAPI", "SQL", "PostgreSQL", "Git", "REST API", "Docker", "Redis", "Microservices", "System Design"
    ],
    "frontend developer": [
        "React", "JavaScript", "TypeScript", "HTML", "CSS", "Git", "REST API", "Tailwind CSS", "Vue", "System Design"
    ],
    "product manager": [
        "Project Management", "Agile", "Scrum", "User Research", "Analytics", "SQL", "System Design", "Product Roadmaps"
    ],
    "ai/ml engineer": [
        "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "SQL", "Git", "System Design"
    ]
}

class SkillGapAgent:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.use_llm = True
            logger.info("SkillGapAgent: Using Google Gemini LLM API")
        else:
            self.use_llm = False
            logger.info("SkillGapAgent: Using database and static mappings")

    def analyze(self, db: Session, current_skills: List[str], target_role: str) -> Dict[str, Any]:
        """
        Compares current skills against the target role requirements.
        Returns target role, current skills list, required skills list, missing skills list, fit score, and recommendations.
        """
        # Try database matching first
        db_match = self._analyze_with_db(db, current_skills, target_role)
        if db_match:
            logger.info("SkillGapAgent: Successfully matched target role against database records.")
            return db_match

        # Fallback to LLM if active
        if self.use_llm:
            try:
                return self._analyze_with_llm(current_skills, target_role)
            except Exception as e:
                logger.error(f"Error executing skill gap analysis with LLM: {e}. Falling back to rule-based.")
        
        return self._analyze_with_rules(current_skills, target_role)

    def _analyze_with_db(self, db: Session, current_skills: List[str], target_role: str) -> Optional[Dict[str, Any]]:
        try:
            # 1. Try exact match
            role = db.query(models.CareerRole).filter(models.CareerRole.name.ilike(target_role)).first()
            
            # 2. Try substring match (e.g. "frontend" matches "Frontend Developer")
            if not role:
                roles = db.query(models.CareerRole).all()
                for r in roles:
                    if r.name.lower() in target_role.lower() or target_role.lower() in r.name.lower():
                        role = r
                        break
            
            # 3. Fallback to general software engineer if no matches found at all
            if not role:
                role = db.query(models.CareerRole).filter(models.CareerRole.name.like("%Generalist%")).first()

            if not role:
                return None

            required = role.required_skills
            current_lower = [s.lower() for s in current_skills]
            matched_skills = []
            missing_skills = []

            for req in required:
                if req.lower() in current_lower:
                    matched_skills.append(req)
                else:
                    missing_skills.append(req)

            # Calculate fit score (ratio of matched skills)
            if len(required) > 0:
                fit_score = int((len(matched_skills) / len(required)) * 100)
            else:
                fit_score = 0

            # Cap fit score between 10% and 95%
            fit_score = max(10, min(fit_score, 95))

            missing_str = ", ".join(missing_skills[:4])
            recommendations = (
                f"Based on the official curriculum for {role.name}: {role.description} "
                f"To transition effectively, focus on learning {missing_str}. "
                f"We recommend completing hands-on projects and studying standard system architecture patterns."
            )

            return {
                "target_role": role.name,
                "overall_fit_score": fit_score,
                "current_skills": current_skills,
                "required_skills": required,
                "skill_gaps": missing_skills,
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Error querying database for skill gap: {e}")
            return None

    def _analyze_with_llm(self, current_skills: List[str], target_role: str) -> Dict[str, Any]:
        prompt = f"""
        You are a Career Skill Gap Analyzer Agent. Compare the candidate's current skills against the requirements for a '{target_role}'.
        Respond ONLY with a valid JSON object matching this structure (no markdown formatting, no ```json):
        {{
            "target_role": "{target_role}",
            "overall_fit_score": 75, // integer between 0 and 100
            "current_skills": ["Skill1", "Skill2", ...], // list of matches
            "required_skills": ["ReqSkill1", "ReqSkill2", ...], // complete list of standard required skills
            "skill_gaps": ["MissingSkill1", "MissingSkill2", ...], // skills from required_skills not in current_skills
            "recommendations": "Provide 2-3 sentences of tactical recommendations to bridge the gap."
        }}

        Candidate Current Skills:
        {json.dumps(current_skills)}
        """
        response = self.model.generate_content(prompt)
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            import re
            clean_text = re.sub(r"^```(?:json)?\n", "", clean_text)
            clean_text = re.sub(r"\n```$", "", clean_text)
        
        return json.loads(clean_text.strip())

    def _analyze_with_rules(self, current_skills: List[str], target_role: str) -> Dict[str, Any]:
        """
        Rule-based matching.
        """
        role_lower = target_role.lower()
        required = []

        # Find best matching standard role
        best_match = None
        for std_role, reqs in STANDARD_ROLES.items():
            if std_role in role_lower or role_lower in std_role:
                best_match = std_role
                required = reqs
                break
        
        if not required:
            # Fallback if target role is custom
            required = STANDARD_ROLES["backend developer"]  # Default base

        # Compare lists case-insensitively
        current_lower = [s.lower() for s in current_skills]
        matched_skills = []
        missing_skills = []

        for req in required:
            if req.lower() in current_lower:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        # Calculate fit score (ratio of matched skills)
        if len(required) > 0:
            fit_score = int((len(matched_skills) / len(required)) * 100)
        else:
            fit_score = 0

        # Adjust score if user has no skills at all or perfect match
        fit_score = max(10, min(fit_score, 95)) # Cap at 95 to leave room for improvement, min at 10

        # Make recommendations text
        missing_str = ", ".join(missing_skills[:4])
        recommendations = (
            f"To excel as a {target_role}, focus on mastering key skills like {missing_str}. "
            f"We recommend completing hands-on projects that integrate these tools. "
            f"Additionally, update your GitHub profile to showcase practical application of your current skills."
        )

        return {
            "target_role": target_role,
            "overall_fit_score": fit_score,
            "current_skills": current_skills,
            "required_skills": required,
            "skill_gaps": missing_skills,
            "recommendations": recommendations
        }
