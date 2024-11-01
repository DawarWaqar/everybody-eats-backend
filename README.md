# Backend for everybody eats

## Technologies

- **Django REST Framework**: For building the REST APIs.
- **PostgreSQL**: The database used.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/DawarWaqar/everybody-eats-backend.git
    ```

2. **Navigate to the project directory**:
    ```bash
    cd everybodyEats
    ```

3. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Setup PostgreSQL Database**:
    - Make sure PostgreSQL is installed and running.
    - Create a database for the project.
    - Update `.env` to include your PostgreSQL database settings:
        ```
        DB_NAME=your_database_name
        DB_USER=your_database_user
        DB_PASSWORD=your_password
        DB_HOST=localhost
        DB_PORT=5432
        ```


6. **Run Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7. **Create a Superuser** (Optional but recommended):
    ```bash
    python manage.py createsuperuser
    ```

8. **Start the development server**:
    ```bash
    python manage.py runserver
    ```
