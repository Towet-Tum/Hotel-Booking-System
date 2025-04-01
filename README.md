# Hotel Booking System

Hotel Booking System is a RESTful API built using Django and Django REST Framework. It allows users to register, log in, log out, book hotel rooms, and make payments. Administrators can manage hotels, rooms, rates, and room types through dedicated endpoints. The application leverages Celery with Redis for asynchronous tasks and caching, SimpleJWT for secure token-based authentication, and PostgreSQL for persistent data storage.

## Features

- **User Authentication & Management**
  - **Register:** Create a new user account.
  - **Login:** Authenticate using JWT (SimpleJWT).
  - **Logout:** Securely log out by invalidating tokens.

- **Booking & Payments**
  - **Book Room:** Authenticated users can book available hotel rooms.
  - **Payment Processing:** Complete bookings by processing payments. (Configured to work with gateways like PayPal with a designated return URL endpoint.)

- **Administration**
  - **Hotel Management:** Admins can add, update, and delete hotels.
  - **Room Management:** Admins can add, update, and delete rooms.
  - **Rate & Room Type Management:** Admins can manage room rates and room types.

- **Background Processing & Caching**
  - **Celery:** Handle asynchronous tasks such as sending emails and payment notifications.
  - **Redis:** Used as a message broker for Celery and for caching purposes.

## Tech Stack

- **Backend Framework:** Django, Django REST Framework
- **Authentication:** SimpleJWT
- **Asynchronous Tasks:** Celery
- **Caching & Messaging:** Redis
- **Database:** PostgreSQL

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Redis
- Virtual environment tool (e.g., `venv` or `pipenv`)

### Clone the Repository

```bash
git clone https://github.com/Towet-Tum/Hotel-Booking-System
cd Hotel-Booking-System
```

### Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration

Create a .env file in the project root and configure the following variables:
```bash 
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres url
REDIS_URL=redis port
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret
```

### Database Setup

Run the migrations to create the database schema:
```bash 
python manage.py makemigrations
python manage.py migrate
```

### Create an Admin User

Create a superuser account for administrative tasks 
```bash 
python manage.py createsupueruser
```

### Running the Application
Start the Django Server
```bash 
python manage.py runserver
```
### Paypal Payments
You can use ngrok for tunneling so that you can test the payment process if you are running the project in localhost.
```
ngrok http 8000
```
### Start the Celery Worker

In a separate terminal, run:
```bash
celery -A hotel_booking worker -l info
```

## API Endpoints
### User Endpoints

    Register:
    
    POST /api/users/register/
    Create a new user account.
    

    Login:
    
    POST /api/users/login/
    Authenticate and receive a JWT access token.
    

    Logout:
    
    POST /api/users/logout/
    Invalidate the JWT token to log out.
    

### Booking & Payment Endpoints

    Book a Room:
    
    POST /api/booking/bookings/
    Create a booking for a room (authentication required).
    

    Payment Confirmation:
    
    GET /api/payments/payment/success/?paymentId=...&token=...&PayerID=...
    Endpoint to finalize the booking after payment confirmation (configured as the PayPal return URL).
    

    Payment Notification:
    
    POST /api/payments/payment/notify/
    Endpoint to receive asynchronous payment notifications.
    

### Administration Endpoints

    Note: These endpoints are secured and require admin-level authentication.

    Hotels Management:
    
        GET /api/admin/hotels/ — List all hotels.

        POST /api/admin/hotels/ — Add a new hotel.

        PUT /api/admin/hotels/<id>/ — Update hotel details.

        DELETE /api/admin/hotels/<id>/ — Delete a hotel.
        

    Rooms Management:

        GET /api/admin/rooms/ — List all rooms.

        POST /api/admin/rooms/ — Add a new room.

        PUT /api/admin/rooms/<id>/ — Update room details.

        DELETE /api/admin/rooms/<id>/ — Delete a room.

    Room Types & Rates:

        GET /api/admin/roomtypes/ — List room types.

        POST /api/admin/roomtypes/ — Add a new room type.

        PUT /api/admin/roomtypes/<id>/ — Update a room type.

        DELETE /api/admin/roomtypes/<id>/ — Delete a room type.

        GET /api/admin/rates/ — List all room rates.

        POST /api/admin/rates/ — Add a new rate.

        PUT /api/admin/rates/<id>/ — Update rate details.

        DELETE /api/admin/rates/<id>/ — Delete a rate.

### Testing

Run the test suite to verify the functionality of the API:
```bash
python manage.py test
```

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.
License

#### This project is licensed under the MIT License. See the LICENSE file for details.



