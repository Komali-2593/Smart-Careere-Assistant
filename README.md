# Smart Career Assistant

🚀 **Live Demo:** https://smart-career-assistant-3v82.onrender.com/

This repository contains the **Smart Career Assistant** project, a resume parsing and career recommendation tool built with:

* **FastAPI** backend for resume upload, parsing (heuristic + LLM), and data storage.
* **HTML/JS** frontend providing a simple UI for uploading resumes and viewing extracted information.
* **SQLite** databases for storing resources, internships, roles, and parsed resume data.

## Features

* Upload PDF or text resumes.
* Extract **Employment History**, **Education**, **Skills**, and other sections.
* Handles various resume formats (tables, bullet points, different headings).
* Provides REST API documentation via FastAPI `/docs`.
* Career guidance and recommendations based on resume analysis.
* Interactive dashboard for viewing extracted candidate information.

## Live Application

🌐 **Website:** https://smart-career-assistant-3v82.onrender.com/

📖 **API Documentation:** https://smart-career-assistant-3v82.onrender.com/docs

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Komali-2593/Smart-Careere-Assistant.git
cd Smart-Careere-Assistant
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run the Backend

```bash
uvicorn backend.app.main:app --reload
```

### 4. Serve the Frontend

```bash
python -m http.server 3000 --directory frontend
```

Open:

```text
http://localhost:3000
```

in your browser to use the application.

## Project Structure

```text
Smart-Careere-Assistant/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── databases/
├── frontend/
│   ├── js/
│   ├── css/
│   └── index.html
├── render.yaml
└── README.md
```

## Deployment

The application is deployed on Render:

https://smart-career-assistant-3v82.onrender.com/

## License

MIT License – see the LICENSE file for details.
