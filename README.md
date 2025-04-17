# Board Game Analysis App

A FastAPI application that provides analysis of board game data using the BGG (BoardGameGeek) dataset.

## Prerequisites

- Python 3.11.5 or higher
- pyenv (for Python version management)
- pip (Python package manager)

## Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Set up Python environment with pyenv:
```bash
pyenv install 3.11.5
pyenv local 3.11.5
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure 
```bash
.
├── app/
│ ├── api/
│ ├── frontend/
│ ├── static/
│ │ └── css/
│ │ └── style.css
│ ├── templates/
│ │ └── index.html
│ └── main.py
├── data/
│ └── bgg_dataset.csv
├── tests/
│ ├── conftest.py
│ └── test_main.py
├── .gitignore
├── .python-version
├── pytest.ini
├── README.md
└── requirements.txt
```

## Running the Application

1. Ensure your virtual environment is activated:
```bash
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Start the FastAPI server:
```bash
python app/main.py
```

3. Open your browser and navigate to:
```bash
http://127.0.0.1:8000
```

## Running Tests

Run the test suite:
```bash
pytest
```

Generate a coverage report:
```bash
pytest --cov=app tests/
```

## Features

## Logging

The application uses Python's built-in logging module with two handlers:

1. File Handler
   - Logs are written to `logs/app.log`
   - Includes timestamp, logger name, log level, and message
   - Captures INFO level and above

2. Console Handler
   - Displays logs in the console
   - Simplified format with level and message
   - Captures INFO level and above

### Log Levels Used

- ERROR: For exceptions and critical errors
- INFO: For general application flow
- DEBUG: For detailed debugging information

### Viewing Logs

To view the application logs:

```bash
# View the last 100 lines of logs
tail -n 100 logs/app.log

# Follow the log file in real-time
tail -f logs/app.log
```
