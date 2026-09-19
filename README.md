# Ecomm Django + React

A full-stack e-commerce web application built with Django REST Framework on the backend and React + Vite on the frontend. The project supports product browsing, cart management, checkout, authentication, and online payment integration with Razorpay.

## Tech Stack

- Backend: Django 6.1, Django REST Framework, JWT Authentication
- Frontend: React 19, Vite, React Router DOM
- Database: PostgreSQL
- Payment: Razorpay
- Styling: CSS / custom frontend styling

## Features

- Product listing and product details
- Category-based browsing
- User signup and login
- JWT-based authentication
- Cart management with add, remove, and quantity update
- Order creation
- Cash on Delivery and online payment support
- Razorpay payment order generation and signature verification
- Media upload for product images

## Project Structure

```text
Ecomm_Django/
├── backend/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── media/
│   ├── store/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── manage.py
│   └── requirements.txt (if added later)
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── razorpay_test_api_keys_1787652538475.csv
└── README.md
```

## Prerequisites

Before running the project, make sure you have installed:

- Python 3.10+
- Node.js 18+
- npm or yarn
- PostgreSQL database
- Razorpay account and API keys

## Backend Setup

1. Open a terminal and navigate to the backend folder:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt psycopg2-binary python-dotenv pillow razorpay
```

4. Create a `.env` file inside the `backend` directory with the following values:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

5. Create the database and apply migrations:

```bash
python manage.py migrate
```

6. Run the Django server:

```bash
python manage.py runserver
```

The backend will run at:

- http://localhost:8000

## Frontend Setup

1. Open a new terminal and navigate to the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will run at:

- http://localhost:5173

## API Endpoints

The backend exposes the following routes under `/api/`:

### Authentication

- `POST /api/register/` - Register a user
- `POST /api/token/` - Get JWT access token
- `POST /api/token/refresh/` - Refresh JWT token

### Products and Categories

- `GET /api/products/` - Get all products
- `GET /api/products/<id>/` - Get a single product
- `GET /api/categories/` - Get all categories

### Cart

- `GET /api/cart/` - Get current user cart
- `POST /api/cart/add/` - Add product to cart
- `POST /api/cart/remove/` - Remove cart item
- `POST /api/cart/update/` - Update item quantity

### Orders and Payments

- `POST /api/orders/create/` - Create an order
- `POST /api/payment/` - Create Razorpay order
- `POST /api/payment/verify/` - Verify Razorpay payment signature

## Environment Notes

- The Django app is configured for local development with `DEBUG = True`.
- CORS is enabled for the frontend origin:
  - `http://localhost:5173`
- Media files are stored under the backend `media/` folder.
- Razorpay credentials must be configured in the environment for online payment to work.

## Default App Flow

1. User signs up or logs in.
2. User browses products.
3. User adds items to cart.
4. User proceeds to checkout.
5. User can choose cash on delivery or online payment.
6. Order is created and stored in the database.

## Notes

This project is currently structured as a learning/demo e-commerce application and can be extended with features like:

- admin product management
- order history
- coupon system
- shipping and tracking
- full production-ready deployment setup

## License

This project is for educational and development purposes.
