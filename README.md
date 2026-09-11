# Doctor Appointment System

A Django project for an online doctor appointment system.

## Project Structure

The project is divided into several Django apps, with each app responsible for a specific part of the system.

    DoctorAppointmentSystem/
    ├── appointment/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations/
    │   ├── models.py
    │   ├── services.py
    │   ├── templates/
    │   │   └── appointment/
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    │
    ├── core/
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── doctor/
    │   ├── admin.py
    │   ├── AppointmentAppCodes.py
    │   ├── apps.py
    │   ├── migrations/
    │   ├── models.py
    │   ├── tests.py
    │   └── views.py
    │
    ├── feedback/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── migrations/
    │   ├── models.py
    │   ├── services.py
    │   ├── templates/
    │   │   ├── doctor_feedback_list.html
    │   │   └── feedback_form.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    │
    ├── user/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── migrations/
    │   ├── models.py
    │   ├── templates/
    │   │   └── user/
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    │
    ├── document/
    │   ├── ERD/
    │   ├── project_description/
    │   └── other_documents/
    │
    ├── .dockerignore
    ├── .env
    ├── .gitignore
    ├── Dockerfile
    ├── docker-compose.yml
    ├── manage.py
    ├── README.md
    └── requirements.txt

### Apps

- `user` — users, patients, OTP, wallets, and transactions
- `doctor` — doctors, specialties, and working shifts
- `appointment` — appointment booking and management
- `feedback` — ratings and feedback
- `core` — main Django project settings and URLs
- `document` — project documentation and related files

## About the Project

This project is a group project for an online doctor appointment system.

The system allows patients to find doctors, view available appointment times, book appointments, manage their wallet, and submit feedback after visiting a doctor.

## Main Features

- User registration with phone number and OTP verification
- Patient profile management
- Doctor and specialty management
- Doctor working shifts
- Viewing available appointment times
- Booking and managing appointments
- Patient feedback and rating for doctors
- Patient wallet
- Wallet transactions
- Login and logout
- Email notifications
- Google authentication
- Dockerized development environment
- Production deployment

## User App

The `user` app handles users, patients, OTP verification, wallets, and transactions.

### User

Custom user model based on Django `AbstractUser`.

It stores information such as:

- Username
- First name
- Last name
- Email
- Phone
- Gender
- National code
- Birth date

### OTP

Stores:

- Phone number
- OTP code
- Creation time
- Expiration time

### Patient

Each patient has a one-to-one relationship with a user.

It stores:

- Insurance number
- Address

### Wallet

Each patient has one wallet.

The wallet stores the patient's balance.

### Transaction

Transactions belong to a wallet and can be related to an appointment.

Transaction types:

- `deposit`
- `payment`
- `refund`

## Doctor App

The `doctor` app handles doctors, specialties, and working shifts.

### Specialty

Stores:

- Specialty title
- Slug

### Doctor

Each doctor has a one-to-one relationship with a user.

It stores:

- Specialty
- Medical license number
- Address
- Visit fee
- Visit duration
- Bio

### WorkingShift

Stores the doctor's working hours for each day of the week.

It also checks:

- The end time is after the start time
- Working shifts do not overlap
- The shift is long enough for the doctor's visit duration

## Appointment App

The `appointment` app handles patient appointments.

Each appointment contains:

- Patient
- Doctor
- Start time
- End time
- Booking status
- Visit status
- Creation date
- Update date

### Booking Status

- `confirmed`
- `cancelled`

### Visit Status

- `visited`
- `absent`

The system also prevents two appointments from being created for the same doctor at the same start time.

## Feedback App

The `feedback` app handles patient ratings and feedback for doctors.

Each feedback contains:

- Patient
- Doctor
- Appointment
- Rating
- Comment
- Confirmation status
- Creation date
- Update date

Ratings are from 1 to 5.

A patient can submit only one feedback for an appointment.

## Registration Flow

1. User enters their phone number.
2. An OTP code is generated.
3. User verifies the OTP.
4. New users complete the registration form.
5. The user account is created.
6. The user is logged in.

## Patient Profile

The patient profile contains information such as:

- First name
- Last name
- Email
- Gender
- National code
- Birth date
- Insurance number
- Address

Each patient has one wallet.

## Wallet and Transactions

Each patient has one wallet.

The wallet stores the current balance and transaction history.

Transaction types are:

- `deposit`
- `payment`
- `refund`

An appointment can be related to a payment transaction.

## Authentication

The project uses Django's authentication system with a custom `User` model.

The custom user model is configured using:

    AUTH_USER_MODEL = "user.User"

The project also includes OTP-based verification for registration and authentication.

## Email Notifications

The system is designed to send email notifications for important appointment events, such as appointment confirmation.

Email configuration will be handled through environment variables.

## Database

During development, the project can use a local database.

For production, the project will be configured to use a production-ready database.

Create migrations:

    python manage.py makemigrations

Apply migrations:

    python manage.py migrate

## Environment Variables

Sensitive configuration values are stored in environment variables instead of being written directly in the source code.

The `.env` file is used for local development.

Examples of configuration values include:

- Secret key
- Debug mode
- Database configuration
- Email configuration
- Google OAuth credentials
- Other environment-specific settings

The `.env` file should not be committed to Git.

## Docker

The project will use Docker to provide a consistent development and deployment environment.

Main Docker files:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

Docker will be used to run the Django application and its required services.

Build and run the containers with:

    docker compose up --build

Stop the containers with:

    docker compose down

## Testing

Tests are written using Django's built-in testing framework.

Run the tests with:

    python manage.py test

Tests cover different parts of the project, including:

- User
- Doctor
- Appointment
- Feedback

## Production

The project will be prepared for production deployment after the main development work is completed.

Production configuration will include:

- Environment variables
- Production settings
- Database configuration
- Static files
- Media files
- Security settings
- Docker deployment
- Web server configuration

## Git

The project is developed using Git and GitHub.

Some basic Git commands:

    git status

    git add .

    git commit -m "your message"

    git push

Before starting new work, update the branch when needed:

    git pull

## Documentation

Project-related documents are stored in the `document` folder.

This folder can contain:

- ER diagrams
- Project description
- Project requirements
- Other project documents

## Technologies

- Python
- Django
- HTML
- Git
- GitHub
- Docker
- Database
- Email services

## Project Status

The project is currently under development.

Some features and deployment-related parts, such as Docker configuration and production deployment, will be completed during the later stages of the project.