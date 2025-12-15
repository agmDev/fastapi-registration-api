# User Registration API

Simple user registration API built with FastAPI, MySQL, and asyncio.

Features:
- Clean layered architecture
- Explicit dependency injection
- Application factory (no side effects on import)
- Transactional service layer
- Full test suite (unit, API, integration)
- MySQL integration tests using Testcontainers


## Application Lifecycle

1. create_app(settings) is called
2. FastAPI application is created
3. Database instance is attached to app.state
4. On startup:
   - Database pool is initialized
   - Database schema/migrations are applied
5. Requests are handled
6. On shutdown:
   - Database pool is gracefully closed

## Architecture

![Architecture diagram](docs/architecture.png)

## Configuration

Configuration is handled via Pydantic BaseSettings and environment variables.

Required environment variables:
- MYSQL_HOST
- MYSQL_PORT
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_DATABASE
- ENVIRONMENT (production | test | integration)


## Running the Application

### Using Docker Compose

Prerequisites:
- Docker
- Docker Compose

Command:

```bash
docker compose up
```

This will start the API and its dependencies locally.

---

### Running Locally

Prerequisites:
- Python 3.12

Commands:

```bash
pip install -r requirements.txt
./launch_dev.sh
```

The `launch_dev.sh` script starts the FastAPI application using the application factory.

---
## How to Run Tests

Prerequisites:
- Docker
- Python 3.12

Commands:

```bash
pip install -r dev-requirements.txt
pytest
```

## Design Decisions

Why an application factory?
- Avoid side effects at import time
- Enable multiple app instances for tests
- Explicit lifecycle management

Why Testcontainers?
- Real database behavior
- No shared state
- Fully reproducible test environment

Why explicit dependency injection?
- Easier testing
- Clear ownership of resources
- No hidden globals

