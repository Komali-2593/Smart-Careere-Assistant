# Smart Career Assistant

This repository contains the **Smart Career Assistant** project, a resume parsing and career recommendation tool built with:

- **FastAPI** backend for resume upload, parsing (heuristic + LLM), and data storage.
- **HTML/JS** frontend providing a simple UI for uploading resumes and viewing extracted information.
- **SQLite** databases for storing resources, internships, roles, and parsed resume data.

## Features

- Upload PDF or text resumes.
- Extract **Employment History**, **Education**, **Skills**, and other sections.
- Handles various resume formats (tables, bullet points, different headings).
- Provides REST API documentation via FastAPI `/docs`.

## Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/Komali-2593/Smart-Careere-Assistant.git
   cd Smart-Careere-Assistant
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the backend:
   ```bash
   uvicorn backend/app/main:app --reload
   ```
4. Serve the frontend:
   ```bash
   python -m http.server 3000 --directory frontend
   ```

Open `http://localhost:3000` in your browser to use the app.

## License

MIT License – see the `LICENSE` file for details.
