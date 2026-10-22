# Flask REST API with SQLite

A task management REST API built using Python, Flask, and SQLite. The API supports CRUD operations, JSON request and response handling, input validation, and HTTP status codes.

## Features

- Create tasks using POST
- Retrieve all tasks using GET
- Retrieve an individual task using GET
- Update tasks using PUT
- Delete tasks using DELETE
- Validate request data
- Return appropriate HTTP status codes
- Persist task data using SQLite

## Technology Stack

- Python
- Flask
- SQLite
- REST API
- Postman
- Git and GitHub

## Project Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd flask-api-interview
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The API will run locally at `http://127.0.0.1:5000`.

## API Endpoints

| Method | Endpoint           | Description        |
| ------ | ------------------ | ------------------ |
| GET    | `/health`          | Health check       |
| POST   | `/tasks`           | Create a task      |
| GET    | `/tasks`           | Retrieve all tasks |
| GET    | `/tasks/<task_id>` | Retrieve one task  |
| PUT    | `/tasks/<task_id>` | Update a task      |
| DELETE | `/tasks/<task_id>` | Delete a task      |

## Example Request

POST `/tasks`

```json
{
  "title": "Learn AWS"
}
```

Example response:

```json
{
  "id": 1,
  "title": "Learn AWS",
  "completed": false
}
```

## Testing

The API endpoints were tested manually using Postman. Test successful requests, invalid input, and missing task IDs.

## Current Limitations

- SQLite is used for local persistence.
- Authentication and authorization are not implemented.
- Automated test coverage and production deployment are future improvements.

## Learning Outcomes

- REST API design and HTTP methods
- JSON serialization and request validation
- SQL CRUD operations
- Error handling and HTTP status codes
- API testing with Postman
- Version control with Git
