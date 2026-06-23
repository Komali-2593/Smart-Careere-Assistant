import re
import os
import json
import logging
from typing import Dict, Any, List, Optional

# Optional Gemini integration
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

logger = logging.getLogger(__name__)

# Heuristic list of common skills for extraction fallback
COMMON_SKILLS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin",
    "html", "css", "sql", "nosql", "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch",
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "ci/cd", "jenkins", "terraform", "ansible",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
    "project management", "agile", "scrum", "product management", "system design", "rest api", "graphql", "microservices"
]

# All known section heading aliases for experience sections
EXPERIENCE_HEADINGS = [
    "experience", "employment history", "work history", "career history",
    "professional experience", "work experience", "professional background",
    "career experience", "relevant experience", "internship", "internships",
    "positions held", "job history", "employment", "projects", "project experience",
    "work background", "career summary", "employment summary",
    "professional summary", "career achievements"
]

# All known section heading aliases for education sections
EDUCATION_HEADINGS = [
    "education", "academic background", "qualification", "qualifications",
    "academic history", "educational background", "degrees", "certifications",
    "academic qualifications", "training", "courses",
]

# Generic separators that signal a new section (not experience/education)
OTHER_SECTION_HEADINGS = [
    "skills", "technical skills", "soft skills", "languages", "awards",
    "achievements", "certifications", "volunteer", "references", "publications",
    "hobbies", "interests", "summary", "objective", "profile", "contact",
    "personal information", "additional information", "extracurricular",
]


class ResumeAgent:
    def __init__(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.use_llm = True
            logger.info("ResumeAgent: Using Google Gemini LLM API")
        else:
            self.use_llm = False
            logger.info("ResumeAgent: Using heuristic/rule-based parser")

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parses raw resume text into structured JSON profile.
        Always guarantees: name, email, skills, experience, education, summary keys.
        """
        if self.use_llm:
            try:
                result = self._parse_with_llm(text)
                result = self._normalize_profile(result)
                # If LLM returned empty experience, supplement with heuristics
                if not result.get("experience"):
                    logger.warning("LLM returned empty experience — running heuristic supplement.")
                    heuristic = self._parse_with_heuristics(text)
                    result["experience"] = heuristic.get("experience", [])
                return result
            except Exception as e:
                logger.error(f"Error parsing resume with LLM: {e}. Falling back to heuristics.")
                return self._parse_with_heuristics(text)
        else:
            return self._parse_with_heuristics(text)

    def _parse_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Uses Gemini to parse the resume. The prompt explicitly lists all common
        Employment History heading variants so the model never skips the section.
        """
        prompt = f"""You are an expert Resume Parser. Your ONLY job is to extract structured data from the resume text below.

CRITICAL RULES:
1. You MUST extract ALL work experience entries. Look for sections titled ANY of these:
   "Experience", "Employment History", "Work History", "Professional Experience",
   "Work Experience", "Career History", "Internships", "Positions Held", or similar.
2. For EACH job entry, extract:
   - company: the employer/organization name
   - role: the job title or position (e.g. "Software Engineer", "Data Analyst Intern")
   - duration: date range as written (e.g. "Jan 2022 - Mar 2024", "2021-Present")
   - description: a short summary of responsibilities and achievements (combine bullet points)
3. If a section exists but formatting is unusual (tables, columns, bullet-only), still extract it.
4. NEVER return an empty "experience" array if there is any work/internship content in the resume.
5. Respond ONLY with valid JSON. No markdown fences (no ```json), no extra text.

Return this exact JSON structure:
{{
    "name": "Candidate full name or null",
    "email": "email@example.com or null",
    "skills": ["Skill1", "Skill2"],
    "experience": [
        {{
            "company": "Company Name",
            "role": "Job Title",
            "duration": "Start Date - End Date",
            "description": "Summary of responsibilities and achievements."
        }}
    ],
    "education": [
        {{
            "degree": "Degree name (e.g. B.Tech Computer Science)",
            "school": "University or Institution Name",
            "year": "Graduation year or date range"
        }}
    ],
    "summary": "Brief professional summary (1-3 sentences)"
}}

Resume Text:
{text}
"""
        response = self.model.generate_content(prompt)
        clean_text = response.text.strip()
        # Strip markdown fences if model still added them
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*\n?", "", clean_text)
            clean_text = re.sub(r"\n?```\s*$", "", clean_text)
        clean_text = clean_text.strip()
        return json.loads(clean_text)

    def _normalize_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes field name variations that an LLM might return.
        Ensures the profile always has the expected keys with correct names.
        """
        # Normalize top-level keys
        normalized = {
            "name": profile.get("name") or profile.get("full_name") or profile.get("candidate_name"),
            "email": profile.get("email") or profile.get("email_address"),
            "skills": profile.get("skills") or profile.get("technical_skills") or profile.get("key_skills") or [],
            "experience": [],
            "education": profile.get("education") or profile.get("educational_background") or [],
            "summary": profile.get("summary") or profile.get("objective") or profile.get("profile") or profile.get("about"),
        }

        # Normalize experience entries — LLMs use many field name variants
        raw_exp = (
            profile.get("experience") or
            profile.get("employment_history") or
            profile.get("work_experience") or
            profile.get("professional_experience") or
            profile.get("work_history") or
            []
        )
        for entry in raw_exp:
            if not isinstance(entry, dict):
                continue
            norm_entry = {
                "company": (
                    entry.get("company") or entry.get("employer") or
                    entry.get("organization") or entry.get("company_name") or "Unknown Company"
                ),
                "role": (
                    entry.get("role") or entry.get("title") or entry.get("job_title") or
                    entry.get("position") or entry.get("designation") or "Unknown Role"
                ),
                "duration": (
                    entry.get("duration") or entry.get("dates") or entry.get("period") or
                    entry.get("date_range") or entry.get("tenure") or "Dates unspecified"
                ),
                "description": (
                    entry.get("description") or entry.get("responsibilities") or
                    entry.get("duties") or entry.get("details") or entry.get("summary") or
                    entry.get("achievements") or ""
                ),
            }
            # If description is a list of strings, join them
            if isinstance(norm_entry["description"], list):
                norm_entry["description"] = " ".join(str(d) for d in norm_entry["description"])
            normalized["experience"].append(norm_entry)

        # Normalize education entries
        norm_edu = []
        for entry in normalized["education"]:
            if not isinstance(entry, dict):
                continue
            norm_edu.append({
                "degree": entry.get("degree") or entry.get("qualification") or entry.get("program") or "Degree",
                "school": (
                    entry.get("school") or entry.get("university") or entry.get("institution") or
                    entry.get("college") or "Institution"
                ),
                "year": entry.get("year") or entry.get("graduation_year") or entry.get("date") or "Completed",
            })
        normalized["education"] = norm_edu

        # Guarantee lists are lists
        if not isinstance(normalized["skills"], list):
            normalized["skills"] = []
        if not isinstance(normalized["experience"], list):
            normalized["experience"] = []
        if not isinstance(normalized["education"], list):
            normalized["education"] = []

        return normalized

    def _parse_with_heuristics(self, text: str) -> Dict[str, Any]:
        """
        Rule-based parser using regex and dictionary matching.
        Robust against reordered sections and varied heading names.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Extract Name (Heuristic: usually first short line without digits or @)
        name = None
        for line in lines[:4]:
            if 2 <= len(line.split()) <= 5 and not any(char.isdigit() for char in line) and "@" not in line:
                name = line
                break
        if not name:
            name = "Candidate Profile"

        # 2. Extract Email
        email_match = re.search(r'[\w\.\+\-]+@[\w\.\-]+\.\w+', text)
        email = email_match.group(0) if email_match else None

        # 3. Extract Skills via keyword matching
        skills = []
        text_lower = text.lower()
        for skill in COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.append(skill.upper() if len(skill) <= 3 else skill.title())
        skills = sorted(list(set(skills)))

        # 4. Segment the document into named sections
        sections = self._segment_sections(lines)

        # 5. Parse Experience from detected section
        experience = self._extract_experience(sections.get("experience", []))
        if not experience:
            logger.warning("No employment history extracted during heuristic parsing.")

        # 6. Parse Education from detected section
        education = self._extract_education(sections.get("education", []))

        # 7. Extract Summary
        summary = None
        for line in lines[:8]:
            if len(line) > 60 and not any(k in line.lower() for k in ["resume", "cv", "portfolio", "@"]):
                summary = line
                break
        if not summary:
            summary = "Motivated professional with a focus on leveraging technology to solve complex problems."

        return {
            "name": name,
            "email": email,
            "skills": skills if skills else ["Python", "SQL", "Git"],
            "experience": experience,
            "education": education,
            "summary": summary,
        }

    def _segment_sections(self, lines: List[str]) -> Dict[str, List[str]]:
        """
        Walks through all lines, detects section headings, and groups content
        under the correct section key. Returns a dict with keys like
        'experience', 'education', and 'other'.
        """
        sections: Dict[str, List[str]] = {"experience": [], "education": [], "other": []}
        current_section = "other"

        for line in lines:
            l_lower = line.lower().strip()
            # Remove common punctuation from heading detection
            l_clean = re.sub(r'[:\-_#*=]+', '', l_lower).strip()

            # Detect headings more flexibly: allow optional colon and surrounding whitespace, case-insensitive
            heading_clean = re.sub(r"[:\-#*_]*$", "", l_clean).strip()
            is_exp = any(re.fullmatch(r".*" + re.escape(h) + ".*", heading_clean, re.IGNORECASE) for h in EXPERIENCE_HEADINGS)
            is_edu = any(re.fullmatch(r".*" + re.escape(h) + ".*", heading_clean, re.IGNORECASE) for h in EDUCATION_HEADINGS)
            is_other = any(re.fullmatch(r".*" + re.escape(h) + ".*", heading_clean, re.IGNORECASE) for h in OTHER_SECTION_HEADINGS)
            # Only treat as a heading if the line is short (headings are rarely > 60 chars)
            is_heading_length = len(line) < 60
            if is_exp and is_heading_length and not is_edu:
                current_section = "experience"
                continue  # Skip the heading line itself
            elif is_edu and is_heading_length and not is_exp:
                current_section = "education"
                continue
            elif is_other and is_heading_length and not is_exp and not is_edu:
                current_section = "other"
                continue

            sections[current_section].append(line)

        return sections

    def _extract_experience(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parses a block of experience lines into structured job entries.
        Handles: role | company | date, role at company, multi-line bullet descriptions,
        date-only lines, and entries without separators.
        """
        experience = []
        curr_job: Optional[Dict[str, Any]] = None
        date_pattern = re.compile(
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|'
            r'June|July|August|September|October|November|December)?\s*\d{4}\b'
            r'|present|current|ongoing|till date|to date',
            re.IGNORECASE
        )
        role_keywords = [
            "developer", "engineer", "intern", "analyst", "specialist", "designer",
            "lead", "manager", "consultant", "architect", "programmer", "admin",
            "coordinator", "officer", "support", "expert", "associate", "executive",
            "researcher", "scientist", "trainee", "director", "head", "vp", "cto", "cfo",
        ]

        def looks_like_job_header(line: str) -> bool:
            """True if line looks like a job title/company header rather than a description."""
            if len(line) > 120:
                return False
            has_sep = bool(re.search(r'[\|•/]| at | @ ', line))
            has_role = any(re.search(r'\b' + re.escape(k) + r'\b', line.lower()) for k in role_keywords)
            has_date = bool(date_pattern.search(line))
            has_company_clue = bool(re.search(r'\b(?:Inc|Ltd|LLC|Pvt|Corp|Technologies|Solutions|Services|Labs|Studio|Group|Company|Co\.|Technologies)\b', line, re.IGNORECASE))
            return has_sep or has_role or has_date or has_company_clue

        def is_bullet(line: str) -> bool:
            return line.strip().startswith(("-", "*", "•", "·", "○", "–", "→", "▪"))

        def parse_job_header(line: str) -> Dict[str, Any]:
            """Split a job header line into role, company, duration."""
            # Try to extract trailing date range first
            duration = "Dates unspecified"
            date_match = re.search(
                r'(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|'
                r'June|July|August|September|October|November|December)?\s*\d{4}\s*[-–—to]+\s*'
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|'
                r'June|July|August|September|October|November|December)?\s*(?:\d{4}|present|current|ongoing|till date|to date))',
                line, re.IGNORECASE
            )
            if date_match:
                duration = date_match.group(0).strip()
                line = line[:date_match.start()].strip().rstrip("(,| \t")

            # Split on separators
            parts = re.split(r'\s*[\|/]\s*|\s+at\s+|\s+@\s+|\s*[,]\s*', line, maxsplit=2)
            parts = [p.strip() for p in parts if p.strip()]

            role_part = parts[0] if parts else "Unknown Role"
            company_part = parts[1] if len(parts) > 1 else "Unknown Company"

            # Swap if company appears to contain role keyword instead
            p0_is_role = any(re.search(r'\b' + re.escape(k) + r'\b', role_part.lower()) for k in role_keywords)
            p1_is_role = len(parts) > 1 and any(re.search(r'\b' + re.escape(k) + r'\b', company_part.lower()) for k in role_keywords)
            if not p0_is_role and p1_is_role:
                role_part, company_part = company_part, role_part

            return {"role": role_part, "company": company_part, "duration": duration, "description": ""}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if is_bullet(stripped):
                # Bullet point → add to current job description
                bullet_text = re.sub(r'^[-*•·○–→▪]\s*', '', stripped).strip()
                if curr_job is not None:
                    curr_job["description"] += bullet_text + " "
                else:
                    # Orphan bullet — might be first job's bullets before we detected header
                    if experience:
                        experience[-1]["description"] += bullet_text + " "
            elif looks_like_job_header(stripped):
                # Save previous job
                if curr_job is not None:
                    curr_job["description"] = curr_job["description"].strip()
                    experience.append(curr_job)
                curr_job = parse_job_header(stripped)
            else:
                # Plain text line inside experience — append to description
                if curr_job is not None:
                    curr_job["description"] += stripped + " "

        # Don't forget last job
        if curr_job is not None:
            curr_job["description"] = curr_job["description"].strip()
            experience.append(curr_job)

        return experience

    def _extract_education(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parses education section lines into structured degree entries.
        """
        education = []
        curr_edu: Optional[Dict[str, Any]] = None

        degree_keywords = [
            "bachelor", "master", "phd", "ph.d", "b.s", "m.s", "b.a", "m.a", "degree", "diploma",
            "b.tech", "m.tech", "btech", "mtech", "b.e", "m.e", "b.sc", "m.sc",
            "bsc", "msc", "bca", "mca", "mba", "bba", "associate", "certification", "certificate",
            "honours", "honors", "undergraduate", "postgraduate", "graduate",
        ]

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            l_lower = stripped.lower()
            has_degree = any(re.search(r'\b' + re.escape(k) + r'\b', l_lower) for k in degree_keywords)

            year_match = re.search(r'\b(19|20)\d{2}\b', stripped)
            year = year_match.group(0) if year_match else None
            line_no_year = stripped.replace(year, "").strip() if year else stripped

            if has_degree:
                if curr_edu:
                    education.append(curr_edu)
                # Split on common separators
                parts = re.split(r'\s*[\|/,]\s*|\s+at\s+|\s+from\s+', line_no_year, maxsplit=2)
                parts = [p.strip() for p in parts if p.strip()]

                degree_part = parts[0] if parts else "Degree"
                school_part = parts[1] if len(parts) > 1 else "Institution"

                # Swap if degree keyword is in second part
                p0_has_deg = any(re.search(r'\b' + re.escape(k) + r'\b', degree_part.lower()) for k in degree_keywords)
                p1_has_deg = len(parts) > 1 and any(re.search(r'\b' + re.escape(k) + r'\b', school_part.lower()) for k in degree_keywords)
                if not p0_has_deg and p1_has_deg:
                    degree_part, school_part = school_part, degree_part

                curr_edu = {
                    "degree": degree_part,
                    "school": school_part,
                    "year": year or "Completed",
                }
            elif curr_edu:
                # Continuation line — could be school name or year
                if year and not curr_edu.get("year"):
                    curr_edu["year"] = year
                if curr_edu.get("school") in ("Institution", "") and len(stripped) < 100:
                    curr_edu["school"] = stripped

        if curr_edu:
            education.append(curr_edu)

        return education
