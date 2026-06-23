import logging
from sqlalchemy.orm import Session
from . import models

logger = logging.getLogger(__name__)

RESOURCES_DATA = [
    # PYTHON
    {
        "title": "Programming with Mosh - Python for Beginners",
        "type": "youtube",
        "link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
        "skill": "Python"
    },
    {
        "title": "Official Python 3 Documentation",
        "type": "documentation",
        "link": "https://docs.python.org/3/",
        "skill": "Python"
    },
    {
        "title": "HackerRank Python Practice Path",
        "type": "practice",
        "link": "https://www.hackerrank.com/domains/python",
        "skill": "Python"
    },
    # SQL
    {
        "title": "FreeCodeCamp - SQL Tutorial for Beginners",
        "type": "youtube",
        "link": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
        "skill": "SQL"
    },
    {
        "title": "SQLZoo Interactive Exercises",
        "type": "practice",
        "link": "https://sqlzoo.net/",
        "skill": "SQL"
    },
    {
        "title": "PostgreSQL Official Documentation",
        "type": "documentation",
        "link": "https://www.postgresql.org/docs/",
        "skill": "SQL"
    },
    # REACT
    {
        "title": "React Official Documentation",
        "type": "documentation",
        "link": "https://react.dev",
        "skill": "React"
    },
    {
        "title": "Net Ninja - React Modern Crash Course",
        "type": "youtube",
        "link": "https://www.youtube.com/watch?v=j942wKiXFu8",
        "skill": "React"
    },
    {
        "title": "Frontend Mentor - React UI Challenges",
        "type": "practice",
        "link": "https://www.frontendmentor.io/",
        "skill": "React"
    },
    # JAVASCRIPT & TYPESCRIPT
    {
        "title": "MDN Web Docs - JavaScript Guide",
        "type": "documentation",
        "link": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "skill": "JavaScript"
    },
    {
        "title": "TypeScript Official HandBook",
        "type": "documentation",
        "link": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "skill": "TypeScript"
    },
    {
        "title": "Exercism JavaScript Track",
        "type": "practice",
        "link": "https://exercism.org/tracks/javascript",
        "skill": "JavaScript"
    },
    # DOCKER
    {
        "title": "Fireship - Docker in 100 Seconds",
        "type": "youtube",
        "link": "https://www.youtube.com/watch?v=gAkwW2tuIqE",
        "skill": "Docker"
    },
    {
        "title": "Docker Official Reference Manual",
        "type": "documentation",
        "link": "https://docs.docker.com/",
        "skill": "Docker"
    },
    # SYSTEM DESIGN
    {
        "title": "ByteByteGo - System Design Fundamentals",
        "type": "youtube",
        "link": "https://www.youtube.com/watch?v=i53Gi_K397I",
        "skill": "System Design"
    },
    {
        "title": "System Design Primer Repository",
        "type": "documentation",
        "link": "https://github.com/donnemartin/system-design-primer",
        "skill": "System Design"
    },
    # DATA STRUCTURES & ALGORITHMS
    {
        "title": "FreeCodeCamp - Data Structures Course",
        "type": "youtube",
        "link": "https://www.youtube.com/watch?v=RBSGKlAvoiM",
        "skill": "Data Structures"
    },
    {
        "title": "LeetCode Algorithmic Practice Platform",
        "type": "practice",
        "link": "https://leetcode.com/",
        "skill": "Algorithms"
    },
    {
        "title": "LeetCode Data Structures Practice Platform",
        "type": "practice",
        "link": "https://leetcode.com/problemset/all/",
        "skill": "Data Structures"
    },
    {
        "title": "Visualgo - Visualizing Data Structures and Algorithms",
        "type": "documentation",
        "link": "https://visualgo.net/en",
        "skill": "Algorithms"
    },
    # GIT
    {
        "title": "Git Flight Rules - Detailed Guide",
        "type": "documentation",
        "link": "https://github.com/k88hudson/git-flight-rules",
        "skill": "Git"
    },
    {
        "title": "Learn Git Branching Sandbox",
        "type": "practice",
        "link": "https://learngitbranching.js.org/",
        "skill": "Git"
    },
    # FASTAPI
    {
        "title": "FastAPI Official Documentation",
        "type": "documentation",
        "link": "https://fastapi.tiangolo.com/",
        "skill": "FastAPI"
    },
    # MACHINE LEARNING
    {
        "title": "StatQuest with Josh Starmer - Machine Learning",
        "type": "youtube",
        "link": "https://www.youtube.com/user/joshstarmer",
        "skill": "Machine Learning"
    },
    {
        "title": "Scikit-Learn Official User Guide",
        "type": "documentation",
        "link": "https://scikit-learn.org/stable/user_guide.html",
        "skill": "Machine Learning"
    },
    {
        "title": "Kaggle Machine Learning Courses",
        "type": "practice",
        "link": "https://www.kaggle.com/learn",
        "skill": "Machine Learning"
    },
    # HTML & CSS
    {
        "title": "MDN Web Docs - HTML Structure Guide",
        "type": "documentation",
        "link": "https://developer.mozilla.org/en-US/docs/Web/HTML",
        "skill": "HTML"
    },
    {
        "title": "MDN Web Docs - CSS Layouts Guide",
        "type": "documentation",
        "link": "https://developer.mozilla.org/en-US/docs/Web/CSS",
        "skill": "CSS"
    },
    {
        "title": "CSS-Tricks - Guide to Flexbox & Grid",
        "type": "documentation",
        "link": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
        "skill": "CSS"
    },
    {
        "title": "CSS Diner - Interactive Selector Practice",
        "type": "practice",
        "link": "https://flukeout.github.io/",
        "skill": "CSS"
    }
]

def seed_resources(db: Session):
    """
    Checks if resources table is empty. If so, seeds with default documentation, youtube, and practice sites.
    """
    try:
        count = db.query(models.Resource).count()
        if count > 0:
            logger.info("Resources database already seeded with %d items.", count)
            return

        logger.info("Seeding learning resources into database...")
        for item in RESOURCES_DATA:
            db_resource = models.Resource(
                title=item["title"],
                type=item["type"],
                link=item["link"],
                skill=item["skill"]
            )
            db.add(db_resource)
        
        db.commit()
        logger.info("Successfully seeded %d resources.", len(RESOURCES_DATA))
    except Exception as e:
        db.rollback()
        logger.error("Error seeding resources database: %s", str(e))
