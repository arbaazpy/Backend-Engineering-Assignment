# Hypervisor-like Service for MLOps Platform

This project is a Django-based backend service for managing clusters, deployments, and organizations. It includes user authentication using JWT, organization membership, and resource management capabilities.

## Features

- User authentication (register/login/logout)
- Organization creation and membership with invite codes
- Cluster creation and resource management (CPU, RAM, GPU)
- Deployment scheduling with priority-based queuing

---

## Project Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Virtual environment tool (e.g., `venv` or `virtualenv`)

### Steps to Set Up the Project

#### 1. Clone the Repository
```bash
$ git clone git@github.com:arbaazpy/Backend-Engineering-Assignment.git
$ cd Backend-Engineering-Assignment
```

#### 2. Create and Activate a Virtual Environment
```bash
# Create a virtual environment
$ python -m venv venv

# Activate the virtual environment
# For Linux/macOS:
$ source venv/bin/activate

# For Windows:
$ venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
$ pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the root directory and add the following environment variables:
```bash
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgresql://<username>:<password>@localhost:<port>/<database_name>
```
Replace `<username>`, `<password>`, `<port>`, and `<database_name>` with your PostgreSQL configuration.

#### 5. Create and Set Up the Database
- Start PostgreSQL and create a database for the project.

```sql
CREATE DATABASE hypervisor;
```

- Apply database migrations:
```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

#### 6. Run the Development Server
```bash
$ python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

---

## API Endpoints

### Authentication
- **Register:** `POST /api/v1/auth/register`
- **Login:** `POST /api/v1/auth/login`
- **Logout:** `POST /api/v1/auth/logout`

### Organization Management
- **Create Organization:** `POST /api/v1/organizations/`
- **Join Organization:** `POST /api/v1/organizations/<id>/join/`

### Cluster Management
- **List/Create Clusters:** `GET/POST /api/v1/clusters/`

### Deployment Management
- **List/Create Deployments:** `GET/POST /api/v1/deployments/`

---

## Running Tests
To ensure the functionality of the application:
```bash
$ python manage.py test
```

---

## API Documentation
The API documentation is available at:
- Swagger: `http://127.0.0.1:8000/swagger/`

---

## Notes
- Ensure the database is running before starting the project.
- Use `DEBUG=False` in production environments.