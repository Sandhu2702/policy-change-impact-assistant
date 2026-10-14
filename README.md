
# Policy Change Impact Assistant

A full-stack application that compares different versions of policy documents, identifies changes, stores structured evidence, and answers user questions using policy changes and AI-generated responses with citations.

## Features

- Parse and clean policy documents.
- Compare two policy versions and detect added, modified, and removed content.
- Store policy versions and changes in SQLite.
- Retrieve relevant policy evidence for user questions.
- Generate answers using Google's Gemini API.
- Display supporting policy sections and citations.
- Handle missing evidence and AI service errors.
- Provide a React-based web interface.
- Include automated tests for core functionality.

## Tech Stack

**Backend**
- Python
- FastAPI
- SQLite
- SQL
- Pytest

**Frontend**
- React
- Vite
- JavaScript
- CSS

**AI Integration**
- Google Gemini API

## Project Structure

```text
policy-change-impact-assistant/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── services/
│   │   └── main.py
│   ├── data/
│   │   └── policies/
│   ├── sql/
│   ├── tests/
│   ├── requirements.txt
│   └── policy_assistant.db
├── frontend/
│   └── src/
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11 or a compatible Python version
- Node.js and npm
- A Google Gemini API key for AI-generated answers

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sandhu2702/policy-change-impact-assistant.git
cd policy-change-impact-assistant
```

### 2. Configure environment variables

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit your real API key to GitHub.

### 3. Set up the backend

From the project root, run:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

Backend URL: http://127.0.0.1:8000

Interactive API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

### 4. Set up the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check backend health |
| GET | `/policies/{policy_name}/changes` | Retrieve saved policy changes |
| POST | `/policies/{policy_name}/compare` | Compare two policy versions |
| GET | `/policies/{policy_name}/ask?question=...` | Ask a question about policy changes |

Refer to `/docs` for available parameters and request details.

## Running Tests

From the backend directory, activate the virtual environment and run:

```powershell
python -m pytest
```

The current test suite contains 33 passing tests.

## Example Use Cases

- Identify changes in annual leave entitlement.
- Review work-from-home rules.
- Compare travel reimbursement limits.
- Understand restrictions on confidential data sharing.
- Ask questions about policy changes and review the supporting evidence.

## How It Works

1. Policy documents are parsed and cleaned.
2. Different versions are compared.
3. Added, modified, and removed content is identified.
4. Structured changes are stored in SQLite.
5. Relevant changes are retrieved for a user question.
6. The Gemini API generates a response based on the retrieved evidence.
7. The application returns the answer and supporting citations.

## Limitations

- Answer quality depends on the available policy evidence and the AI service.
- Keyword-based retrieval may miss relevant evidence when a question uses different terminology.
- Gemini API availability and usage quotas may affect AI-generated answers.
- Citations identify supporting policy changes; users should review the cited text for important decisions.

## Security

- Keep API keys in environment variables.
- Do not commit `.env`, virtual environments, or local database files containing data that should remain private.
- Review `.gitignore` before pushing changes to GitHub.

## Future Improvements

- Improve semantic retrieval and evidence ranking.
- Add document upload support.
- Improve citation relevance and answer evaluation.
- Add authentication and role-based access control.

## Author

Developed as a full-stack project demonstrating policy version comparison, structured data storage, API development, automated testing, and AI-assisted question answering.
