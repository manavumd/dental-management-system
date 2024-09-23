### README for Dental Management Platform

---

## Project Overview

This Dental Management System aims to manage patient and provider data efficiently across multiple clinics. This Django-based platform allows administrative users to manage three main entities: **Clinics**, **Doctors**, and **Patients**, including scheduling appointments and tracking visits.

The platform includes:

- User authentication and session management
- CRUD operations for Clinics, Doctors, and Patients
- Appointment scheduling and Visit management
- REST API for integration with external systems

---

## Key Features

### User Management
- **Login**: Users can log in using their email and password.
- **Logout**: Users can securely log out after finishing their session.

### Clinics Management
- **Clinics List**: Displays all clinics with their name, phone number, city, state, and the number of affiliated doctors and patients.
- **Clinic Detail**: Allows users to view and edit clinic details such as office address, doctors' affiliations, and their schedules.
- **Add/Edit Doctor Affiliation**: Assign doctors to clinics and set their working hours.

### Doctors Management
- **Doctors List**: Displays doctors' NPI, name, specialties, affiliated clinics, and patients.
- **Doctor Detail**: Allows viewing and editing of doctor details, affiliations, and patient lists.

### Patients Management
- **Patients List**: Displays patients’ information, last visit, and next appointment details.
- **Patient Detail**: View patient details, visit history, and upcoming appointments.
- **Add Visits**: Admins can add new visits for a patient.
- **Schedule Appointments**: Allows booking appointments with a doctor for a specific procedure.

### REST API Endpoints
- **Add Patient**: Create new patient records.
- **Add Doctor**: Create new doctor profiles.
- **Add Clinic**: Register new clinics.
- **Get Clinic Info**: Retrieve clinic details without affiliated doctors and patients.

---

## Technology Stack

- **Backend**: Django (includes admin functionalities)
- **Frontend**: HTML, Bootstrap, JavaScript
- **Database**: PostgreSQL (SQLite used for testing)
- **Testing**: Unit tests are provided for key functionalities
- **REST Framework**: Django Rest Framework for API development

---

## Setup Instructions

### 1. Prerequisites
- **Python 3.x**
- **PostgreSQL** (for local environment)
- **SQLite** (for unit testing)

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/dental-management-system.git
cd dental-management-system
```

### 3. Set up Virtual Environment
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 4. Install Requirements
```bash
pip install -r requirements.txt
cd bright_smile
```

### 5. Configure Database
- In your **settings.py** file, configure the PostgreSQL database:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yourdbname',
        'USER': 'yourdbuser',
        'PASSWORD': 'yourdbpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Make and Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
- Remember the superuser credentials for accessing the admin portal.
```bash
python manage.py createsuperuser
```


### 8. Run the Development Server
```bash
python manage.py runserver
```

### 9. Create a user for app in admin portal
1. Go to : **http://127.0.0.1:8000/admin**<br>
2. Login using superuser credentials<br>
3. Create a user (remember its username viz. email and password)

### 10. Go to clinics listing
1. Go to : **http://127.0.0.1:8000/administration/clinics**
2. Login using created user credentials in step 10


---

## Running Tests

The project uses **SQLite** for testing. To run the test suite:

```bash
python manage.py test
```

---

## REST API Usage

### Base URL:
```
http://127.0.0.1:8000/administration/api/
```

### Available Endpoints:
1. **Add Patient**: 
   - `POST /patients/`
   - JSON Body: 
     ```json
     {
       "name": "John Doe",
       "date_of_birth": "1990-01-01",
       "last_4_ssn": "1234",
       "phone_number": "1234567890",
       "gender": "Male",
       "address": "123 Main St"
     }
     ```
2. **Add Doctor**: 
   - `POST /doctors/`
   - JSON Body:
     ```json
     {
       "NPI": "1234567890",
       "name": "Dr. Smith",
       "email": "drsmith@example.com",
       "phone_number": "9876543210",
       "specialties": ["Root Canal", "Filling"]
     }
     ```

3. **Add Clinic**: 
   - `POST /clinics/`
   - JSON Body:
     ```json
     {
       "name": "Downtown Clinic",
       "phone_number": "1112223333",
       "city": "New York",
       "state": "NY",
       "email": "clinic@example.com"
     }
     ```

4. **Get All Clinic Information**: 
   - `GET /clinics/`
   - Response:
     ```json
     [{
       "id": 1,
       "name": "Downtown Clinic",
       "phone_number": "1112223333",
       "city": "New York",
       "state": "NY",
       "email": "clinic@example.com"
     },
     {
       "id": 2,
       "name": "Uptown Clinic",
       "phone_number": "111222443",
       "city": "Jersey City",
       "state": "New Jersey",
       "email": "clinic2@example.com"
     }]
     ```
     
5. **Get Clinic Information**: 
   - `GET /clinics/{id}/`
   - Response:
     ```json
     {
       "id": 1,
       "name": "Downtown Clinic",
       "phone_number": "1112223333",
       "city": "New York",
       "state": "NY",
       "email": "clinic@example.com"
     }
     ```

---

## Assumptions

- Each doctor can have multiple specialties, but these are shared across clinics.
- Doctors can have different working hours in different clinics.
- No buffer time is required between appointments.
- Patients can have multiple visits and appointments.
- **Appointment Duration**: Each appointment has a fixed duration of **15 minutes**. The system checks if there are any 15-minute slots available between the start and end time of the doctor's schedule, while considering other scheduled appointments.
- Tests are run using **SQLite**, and the production environment uses **PostgreSQL**.

---
