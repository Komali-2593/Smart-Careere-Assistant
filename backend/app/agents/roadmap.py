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

# Predefined learning topics for common missing skills (fallback)
SKILL_LEARNING_CONTENT = {
    "react": {
        "topic": "Frontend Mastery with React",
        "duration": "3 Weeks",
        "description": "Understand component lifecycles, state management with Hooks (useState, useEffect), routing, and clean component architecture.",
        "skills": ["React", "JavaScript", "HTML/CSS"]
    },
    "node.js": {
        "topic": "Backend Foundations with Node.js & Express",
        "duration": "2 Weeks",
        "description": "Build event-driven RESTful APIs, manage npm packages, configure middleware, and implement JWT-based user authentication.",
        "skills": ["Node.js", "Express", "REST APIs"]
    },
    "python": {
        "topic": "Core & Advanced Python Development",
        "duration": "2 Weeks",
        "description": "Master data structures, object-oriented concepts, writing clean asynchronous code, and integrating third-party libraries.",
        "skills": ["Python", "Algorithms"]
    },
    "sql": {
        "topic": "Relational Databases & Advanced SQL",
        "duration": "2 Weeks",
        "description": "Learn schema design, advanced queries (joins, aggregations), index optimization, and database normalization principles.",
        "skills": ["SQL", "PostgreSQL", "Database Design"]
    },
    "git": {
        "topic": "Modern Version Control & Collaborative Git",
        "duration": "1 Week",
        "description": "Learn semantic branching strategies, merging/rebasing processes, resolving merge conflicts, and working with GitHub pull requests.",
        "skills": ["Git", "GitHub"]
    },
    "docker": {
        "topic": "Containerization & Microservices with Docker",
        "duration": "2 Weeks",
        "description": "Understand container virtualization, write optimal Dockerfiles, manage multi-container apps with docker-compose, and expose container ports.",
        "skills": ["Docker", "Containers", "DevOps"]
    },
    "kubernetes": {
        "topic": "Orchestration with Kubernetes",
        "duration": "3 Weeks",
        "description": "Deploy workloads using pods, deployments, services, configure ingress, and manage environment secrets and configs.",
        "skills": ["Kubernetes", "DevOps", "Scaling"]
    },
    "aws": {
        "topic": "Cloud Infrastructure on AWS",
        "duration": "3 Weeks",
        "description": "Learn AWS core services: EC2 instances, S3 storage buckets, IAM user security, RDS database servers, and Lambda serverless functions.",
        "skills": ["AWS", "Cloud Computing"]
    },
    "ci/cd": {
        "topic": "Automated Pipelines with CI/CD",
        "duration": "2 Weeks",
        "description": "Design test execution, building, and deployment workflows using GitHub Actions or Jenkins to automate application delivery.",
        "skills": ["CI/CD", "GitHub Actions", "Automation"]
    },
    "machine learning": {
        "topic": "Machine Learning Fundamentals",
        "duration": "4 Weeks",
        "description": "Learn supervised and unsupervised learning algorithms, feature engineering, and training models using Scikit-Learn.",
        "skills": ["Machine Learning", "Python", "Scikit-Learn"]
    },
    "fastapi": {
        "topic": "FastAPI Web Services",
        "duration": "2 Weeks",
        "description": "Build high-performance asynchronous API endpoints, configure Pydantic schemas, and integrate SQLAlchemy ORM.",
        "skills": ["FastAPI", "Python", "APIs"]
    },
    "typescript": {
        "topic": "Type-Safe Javascript with TypeScript",
        "duration": "2 Weeks",
        "description": "Understand static typing, interfaces, generic functions, type assertions, and compiling TypeScript configuration files.",
        "skills": ["TypeScript", "JavaScript"]
    }
}

class RoadmapAgent:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.use_llm = True
            logger.info("RoadmapAgent: Using Google Gemini LLM API")
        else:
            self.use_llm = False
            logger.info("RoadmapAgent: Using database and rules generator")

    def generate(self, db: Session, skill_gaps: List[str], target_role: str, fit_score: int = 50) -> Dict[str, Any]:
        """
        Generates a sequential timeline structure based on missing skill gaps or predefined database roadmaps.
        """
        # Try database matching first
        db_roadmap = self._generate_with_db(db, target_role, fit_score)
        if db_roadmap:
            logger.info("RoadmapAgent: Successfully loaded tiered roadmap from database.")
            return db_roadmap

        # Fallback to LLM if active
        if self.use_llm:
            try:
                return self._generate_with_llm(skill_gaps, target_role)
            except Exception as e:
                logger.error(f"Error generating roadmap with LLM: {e}. Falling back to rules.")
        
        return self._generate_with_rules(skill_gaps, target_role)

    def _generate_with_db(self, db: Session, target_role: str, fit_score: int) -> Optional[Dict[str, Any]]:
        try:
            # 1. Try exact match
            role = db.query(models.CareerRole).filter(models.CareerRole.name.ilike(target_role)).first()
            
            # 2. Try substring match
            if not role:
                roles = db.query(models.CareerRole).all()
                for r in roles:
                    if r.name.lower() in target_role.lower() or target_role.lower() in r.name.lower():
                        role = r
                        break
            
            # 3. Fallback to general Software Engineer
            if not role:
                role = db.query(models.CareerRole).filter(models.CareerRole.name.like("%Generalist%")).first()

            if not role:
                return None

            # Select roadmap tier based on fit score
            if fit_score < 40:
                steps = role.beginner_roadmap
                tier = "Beginner Syllabus"
            elif fit_score <= 75:
                steps = role.intermediate_roadmap
                tier = "Intermediate Syllabus"
            else:
                steps = role.advanced_roadmap
                tier = "Advanced Syllabus"

            # Compute sum of durations in weeks
            total_weeks = 0
            for step in steps:
                duration_str = step.get("duration", "2 Weeks")
                try:
                    weeks = int(duration_str.split()[0])
                    total_weeks += weeks
                except Exception:
                    total_weeks += 2

            return {
                "estimated_duration": f"{total_weeks} Weeks ({tier} for {role.name})",
                "steps": steps
            }
        except Exception as e:
            logger.error(f"Error querying database for roadmap: {e}")
            return None

    def _generate_with_llm(self, skill_gaps: List[str], target_role: str) -> Dict[str, Any]:
        prompt = f"""
        You are a Learning Path & Curriculum Coordinator Agent.
        Design a learning roadmap to help a candidate bridge these skill gaps to become a '{target_role}'.
        Respond ONLY with a valid JSON object matching this structure (no markdown formatting, no ```json):
        {{
            "estimated_duration": "12 Weeks", // total estimated time
            "steps": [
                {{
                    "step_number": 1,
                    "topic": "Step Title (e.g. Master React Basics)",
                    "duration": "2 Weeks", // duration for this specific step
                    "description": "Detailed explanation of what to learn and build.",
                    "skills_learned": ["SkillA", "SkillB"]
                }}
            ]
        }}

        Skill Gaps:
        {json.dumps(skill_gaps)}
        """
        response = self.model.generate_content(prompt)
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            import re
            clean_text = re.sub(r"^```(?:json)?\n", "", clean_text)
            clean_text = re.sub(r"\n```$", "", clean_text)
        
        return json.loads(clean_text.strip())

    def _generate_with_rules(self, skill_gaps: List[str], target_role: str) -> Dict[str, Any]:
        """
        Generates structured steps based on the local dictionary.
        """
        steps = []
        step_number = 1
        total_weeks = 0

        # Process matching skills from our local DB
        for skill in skill_gaps:
            skill_key = skill.lower()
            if skill_key in SKILL_LEARNING_CONTENT:
                content = SKILL_LEARNING_CONTENT[skill_key]
                duration_str = content["duration"]
                weeks = int(duration_str.split()[0])
                total_weeks += weeks

                steps.append({
                    "step_number": step_number,
                    "topic": content["topic"],
                    "duration": duration_str,
                    "description": content["description"],
                    "skills_learned": content["skills"]
                })
                step_number += 1
            else:
                # Catch-all for other skills
                steps.append({
                    "step_number": step_number,
                    "topic": f"Essentials of {skill}",
                    "duration": "2 Weeks",
                    "description": f"Deep dive into the core specifications, architecture, and practical implementations of {skill} within {target_role} pipelines.",
                    "skills_learned": [skill]
                })
                total_weeks += 2
                step_number += 1

        # If no skill gaps were identified, generate advanced career growth steps
        if not steps:
            steps = [
                {
                    "step_number": 1,
                    "topic": f"Advanced {target_role} Architectures",
                    "duration": "3 Weeks",
                    "description": "Master advanced architectural patterns, optimization, security configurations, and design patterns standard for senior positions.",
                    "skills_learned": ["System Architecture", "Performance Tuning"]
                },
                {
                    "step_number": 2,
                    "topic": "Production Deployments & Scale",
                    "duration": "2 Weeks",
                    "description": "Learn cloud orchestrations, logging configurations, real-time monitoring, and automatic failovers in modern environments.",
                    "skills_learned": ["DevOps", "Monitoring"]
                }
            ]
            total_weeks = 5

        return {
            "estimated_duration": f"{total_weeks} Weeks",
            "steps": steps
        }
