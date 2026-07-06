# AP Exception Resolution Agent Backend

This is a Python FastAPI backend for the **AP Exception Resolution Agent**, a multi-agent system designed to process invoices and resolve mismatches against purchase orders.

## Project Structure

```text
backend/
  main.py
  requirements.txt
  .env.example
  agents/
    __init__.py
    base.py
  models/
    __init__.py
    schemas.py
  services/
    __init__.py
    gemini_client.py
    firestore_client.py
  policy/
    __init__.py
    rules.py
  data/
    __init__.py
    generate_synthetic.py
  tests/
    __init__.py
```

## Setup and Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

## Running the Server

Start the development server using `uvicorn`:
```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`. You can check the health status by visiting `http://127.0.0.1:8000/health`.

## Running Tests

Run the automated test suite using `pytest`:
```bash
# From the backend directory:
.\venv\Scripts\pytest -v
```

