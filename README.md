# eHealth API

A Django-based REST API for a medical platform where patients can register, book appointments with medical practitioners, and rate practitioners. The API includes role-based access control, search/filtering for practitioners, and comprehensive Swagger documentation.

## Features
- **User Authentication**: Email-based login with token authentication.
- **Role-Based Access**: Differentiates between patients, practitioners, and admins.
- **CRUD Operations**: Manage patients and practitioners.
- **Appointment Management**: Patients can book/cancel appointments; practitioners can accept/reject.
- **Ratings and Feedback**: Patients can rate and leave feedback for practitioners.
- **Search and Filtering**: Find practitioners by specialization, location, and name.
- **Swagger Documentation**: Interactive API docs at `/api/swagger/`.
- **Unit Tests**: Comprehensive tests for all endpoints.

## Tech Stack
- **Framework**: Django 5.0.10, Django REST Framework
- **Authentication**: Token-based (DRF TokenAuthentication)
- **Documentation**: Swagger (`drf-yasg`)
- **Database**: SQLite (default, configurable for PostgreSQL, etc.)
- **Python**: 3.12.3

## Prerequisites
- Python 3.12+
- Virtualenv (recommended)
- Git

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/eHealth.git
   cd eHealth

### Setup your virtual environment
python -m venv django-venv
source django-venv/bin/activate  # On Windows: django-venv\Scripts\activate

### Install django and it's dependencies
pip install django djangorestframework drf-yasg django-filter
pip freeze > requirements.txt

### Database migrations
python manage.py makemigrations
python manage.py migrate

### create admin panel
python manage.py createsuperuser


### Run local development server
python manage.py runserver

Api will be available at:
http://127.0.0.1:8000/api/

Access Swagger Documentation:
Open http://127.0.0.1:8000/api/swagger/ in your browser.

### HAPPY CODING!!!

