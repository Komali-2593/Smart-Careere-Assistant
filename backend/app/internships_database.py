import logging
from sqlalchemy.orm import Session
from . import models

logger = logging.getLogger(__name__)

INTERNSHIPS_DATA = [
    {
        "title": "Software Engineering Intern",
        "company": "Google",
        "location": "Mountain View, CA (Hybrid)",
        "link": "https://careers.google.com/jobs/results/?q=intern",
        "description": "Collaborate on scalability and performance optimization of core search infrastructure and cloud services.",
        "role_category": "Software Engineer (Generalist)"
    },
    {
        "title": "Frontend Developer Intern",
        "company": "Meta",
        "location": "Menlo Park, CA (Onsite)",
        "link": "https://www.metacareers.com/jobs",
        "description": "Build high-fidelity UI features using React and TypeScript for Instagram and Facebook web applications.",
        "role_category": "Frontend Developer"
    },
    {
        "title": "Backend Engineering Intern",
        "company": "Stripe",
        "location": "San Francisco, CA (Hybrid)",
        "link": "https://stripe.com/jobs/search",
        "description": "Scale financial API pipelines, improve logging throughput, and integrate multi-region database redundancy.",
        "role_category": "Backend Developer"
    },
    {
        "title": "Full Stack Engineering Intern",
        "company": "Vercel",
        "location": "Remote",
        "link": "https://vercel.com/careers",
        "description": "Work on the Next.js framework, enhance developer dashboard integrations, and create seamless deployment workflows.",
        "role_category": "Full Stack Developer"
    },
    {
        "title": "Data Science Intern",
        "company": "Netflix",
        "location": "Los Gatos, CA (Hybrid)",
        "link": "https://jobs.netflix.com/search",
        "description": "Apply statistical and machine learning models to optimize recommendation engines and user retention metrics.",
        "role_category": "Data Scientist"
    },
    {
        "title": "Machine Learning Intern",
        "company": "Antigravity AI",
        "location": "Bengaluru, India (Onsite)",
        "link": "https://careers.google.com",
        "description": "Train and fine-tune large language models and computer vision pipelines for coding assistants and agents.",
        "role_category": "Machine Learning Engineer"
    },
    {
        "title": "DevOps / Infrastructure Intern",
        "company": "Amazon Web Services (AWS)",
        "location": "Seattle, WA (Onsite)",
        "link": "https://www.amazon.jobs",
        "description": "Automate infrastructure provisioning using Terraform and configure containerized orchestration in Kubernetes.",
        "role_category": "DevOps Engineer"
    },
    {
        "title": "UI/UX Design Intern",
        "company": "Figma",
        "location": "San Francisco, CA (Hybrid)",
        "link": "https://www.figma.com/careers/",
        "description": "Conduct user research, draft high-fidelity wireframes, and design components for cloud collaboration design tools.",
        "role_category": "UI/UX Designer"
    },
    {
        "title": "Graduate Software Engineer Intern",
        "company": "Microsoft",
        "location": "Redmond, WA (Hybrid)",
        "link": "https://careers.microsoft.com",
        "description": "Develop features for Azure Cloud Management tools using C#, .NET, and Python.",
        "role_category": "Software Engineer (Generalist)"
    },
    {
        "title": "Junior Frontend Developer (Intern)",
        "company": "Shopify",
        "location": "Remote (Canada/US)",
        "link": "https://www.shopify.com/careers",
        "description": "Maintain merchant admin dashboards, optimize page load speeds, and style components with custom Tailwind frameworks.",
        "role_category": "Frontend Developer"
    },
    {
        "title": "Backend API Intern",
        "company": "FastAPI Labs",
        "location": "Remote",
        "link": "https://github.com/fastapi/fastapi",
        "description": "Contribute to building and testing next-generation asynchronous API routing frameworks and OpenAPI schemas.",
        "role_category": "Backend Developer"
    },
    {
        "title": "Associate Data Analyst (Intern)",
        "company": "Uber",
        "location": "New York, NY (Hybrid)",
        "link": "https://www.uber.com/careers",
        "description": "Write SQL queries to analyze ride-sharing logistics, compile interactive dashboards, and report metric trends.",
        "role_category": "Data Analyst"
    }
]

def seed_internships(db: Session):
    """
    Checks if internships table is empty. If so, seeds with default opportunities.
    """
    try:
        count = db.query(models.Internship).count()
        if count > 0:
            logger.info("Internships database already seeded with %d opportunities.", count)
            return

        logger.info("Seeding internships data into database...")
        for item in INTERNSHIPS_DATA:
            db_internship = models.Internship(
                title=item["title"],
                company=item["company"],
                location=item["location"],
                link=item["link"],
                description=item["description"],
                role_category=item["role_category"]
            )
            db.add(db_internship)
        
        db.commit()
        logger.info("Successfully seeded %d internships.", len(INTERNSHIPS_DATA))
    except Exception as e:
        db.rollback()
        logger.error("Error seeding internships database: %s", str(e))
