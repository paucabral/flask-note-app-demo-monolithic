# Note Taking App
A demo of a Flask App using an ORM.

**Features**
- Full CRUD Note taking app
- Written in Python (Flask)
- Utilizes SQLAlchemy as the ORM

**Prerequisites**
- Python 3
- Virtual Environment Package (Installed through PIP)

**Run development server**
1. Create a virtual environment.
    ```bash
    $ python -m venv venv
    ```
2. Activate the virtual environment.
    ```bash
    $ source /venv/bin/activate
    ```
3. Install the dependencies.
    ```bash
    (venv)$ pip install -r requirements.txt
    ```

4. Create a `.env` file using `.env.sample` and fill in the values.
    
    *Example below:*
    ```
    FLASK_ENV=development
    DEBUG=True
    PORT=5000

    DEV_SECRET_KEY=E53E57F32CD769B3873D15E31AE45
    TEST_SECRET_KEY=45E74B23547B8B9EF44815F9762EF
    STG_SECRET_KEY=DFC3C8336D477D36B56A8B9DBDEFE
    PROD_SECRET_KEY=38FB5B55C454FC25C6F6A6AE35278

    DEV_SQLALCHEMY_DATABASE_URI=sqlite:///dev.db
    TEST_SQLALCHEMY_DATABASE_URI=sqlite:///:memory:
    STG_SQLALCHEMY_DATABASE_URI=sqlite:///stg.db
    PROD_SQLALCHEMY_DATABASE_URI=sqlite:///prod.db

    TEST_USER=testuser
    TEST_PASSWORD=testpassword
    ```

5. Run the code.
    ```bash
    (venv)$ python app.py
    ```

6. To run tests.
    ```bash
    (venv)$ FLASK_ENV=test pytest
    ```
