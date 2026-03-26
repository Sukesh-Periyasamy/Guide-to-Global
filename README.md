# Guide to Global

AI-powered platform to aggregate, structure, and search global university admission requirements, deadlines, and eligibility. Built using web scraping, FastAPI, and MongoDB to simplify study abroad applications.

---

## Project Overview

Guide to Global is a production-ready MVP backend that:

- **Scrapes** university program pages with [Scrapling](https://github.com/D4Vinci/Scrapling)
- **Extracts** structured admission data (IELTS, TOEFL, GRE, deadlines, LOR count, etc.)
- **Stores** documents in MongoDB
- **Serves** the data through a FastAPI REST API with search, filter, and detail endpoints

---

## Folder Structure

```
project/
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── routes/
│   │     ├── search.py        # GET /search, GET /filter
│   │     └── program.py       # GET /program/{id}
│   ├── services/
│   │     └── search_service.py
│   └── db/
│         └── mongo.py         # MongoDB connection + indexes
├── scraper/
│   ├── scrapling_client.py    # Fetch HTML via Scrapling
│   ├── extractor.py           # HTML → structured JSON
│   └── runner.py              # CLI: scrape URL or seed sample data
├── models/
│   └── program_schema.py      # Pydantic data schema
├── config/
│   └── settings.py            # Env config (python-dotenv)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python 3.10+
- MongoDB running locally (`mongodb://localhost:27017`) or a connection string from MongoDB Atlas

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env to set MONGO_URI and DATABASE_NAME if needed
```

---

## Running the FastAPI Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at <http://localhost:8000>.

Interactive Swagger docs: <http://localhost:8000/docs>

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/search?q=<keyword>` | Search by university, program, or department |
| GET | `/filter?country=Germany&degree=Masters` | Filter by country and/or degree |
| GET | `/program/{id}` | Get full program details by MongoDB ID |

---

## Running the Scraper

### Seed sample data (development / first run)

```bash
python -m scraper.runner --seed
```

This inserts two example program documents (TU Munich AI MSc, UofT MEng ML) into MongoDB.

### Scrape a real URL

```bash
python -m scraper.runner --url https://www.example.edu/programs/computer-science
```

The runner fetches the page, extracts admission details, and inserts the document into MongoDB.
You can then fill in university/program metadata fields manually or extend the extractor.

---

## Data Schema

Each MongoDB document represents **one program** and contains:

```json
{
  "university": { "name": "", "country": "", "city": "" },
  "program":    { "name": "", "degree": "", "department": "", "duration": "" },
  "admission":  { "status": "open", "intake": "", "deadline": "" },
  "requirements": {
    "ielts":     { "required": true,  "min_score": 7.0 },
    "toefl":     { "required": false, "min_score": null },
    "gre":       { "required": false, "recommended": true, "min_score": null },
    "documents": { "lor": 2, "sop": true, "resume": true, "transcript": true }
  },
  "financial":  { "tuition_fee": "€0", "scholarship_available": true },
  "links":      { "admission_page": "", "program_page": "", "apply_link": "" },
  "raw_data":   { "requirements_text": "", "description_text": "" },
  "metadata":   { "last_scraped": "", "source": "" }
}
```
