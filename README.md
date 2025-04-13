# Markr - Marking as a Service

This project is a data ingestion and processing microservice for multiple-choice question (MCQ) test results, built as a prototype for Markr.

## Project Goal

The primary goal is to ingest XML documents containing student test results via an HTTP POST request, store them persistently, handle duplicates, validate the data, and provide an endpoint to retrieve aggregate statistics (mean, count, percentiles) for a given test.

## Note:
* I have used the AI-native IDE 'Cursor' as my primary IDE while building this application
* I have tried to use AI relatively sparingly during the course of completing this application, but I have used it largely for some of these tasks:
1) Flask, Docker and Pytest setup
2) Debugging & fixing errors
3) Environment variables management & configuration setup for testing
4) Creation of Sample XML Test fixtures & XML lines
5) Documentation
6) Creation of an PRD document to ensure that I don't miss out on any of the requirements detailed in the instructions.

Overall, whereas I have indeed utilised AI over the course of the building of this application, I have tried not to rely on it heavily and feel confident about my decision making & choices, and shall be happy to discuss the same.

## Key Assumptions

*   **XML Data Source:** The input XML format is based on the provided example and description. While somewhat flexible, it expects a root element `<mcq-test-results>` containing `<mcq-test-result>` elements.
*   **`<summary-marks>` Reliability:** For this prototype, the `<summary-marks>` element within each `<mcq-test-result>` is trusted as the source for `marks-obtained` and `marks-available`. The individual `<answer>` elements are ignored.
*   **Duplicate Handling:** If multiple results for the same student and test ID are ingested, the entry with the highest `marks-obtained` score is kept. The `marks-available` for that entry will also be updated to the highest seen value for that test across all submissions for that student.
*   **Error Handling:** Malformed XML or missing required fields (`first-name`, `last-name`, `student-number`, `test-id`, `summary-marks` with `available` and `obtained` attributes) within a `<mcq-test-result>` element will cause the entire *document* to be rejected with an appropriate HTTP error (400 Bad Request).
*   **Content Type:** The `/import` endpoint strictly expects a `Content-Type` header of `text/xml+markr`. Other content types will be rejected (415 Unsupported Media Type).
*   **Database:** PostgreSQL is used as the persistent data store, managed via SQLAlchemy.
*   **Environment:** The application is designed to be run using Docker and Docker Compose. Configuration is managed via environment variables (`.env` for local, `.env.docker` for Docker).
*   **Security:** HTTPS/SSL is not implemented for the `/import` endpoint as per instructions. `SECRET_KEY` is managed via environment variables and should be changed for production. XML parsing is done securely using `lxml`'s `resolve_entities=False` setting to prevent XXE attacks.

## Approach Taken

*   **Framework:** Flask is used as the web framework.
*   **Database:** PostgreSQL with SQLAlchemy ORM for database interactions. The `TestResult` model defines the schema. An index is added to the `test_id` column for faster lookups during aggregation.
*   **XML Parsing:** `lxml` library is used for robust and secure XML parsing and validation.
*   **API Endpoints:**
    *   `POST /import`: Ingests XML data (`text/xml+markr`). Handles validation and duplicate logic via the `IngestionService`.
    *   `GET /results/<test_id>/aggregate`: Returns JSON aggregate statistics calculated by the `AggregationService`. Uses NumPy for calculations after fetching relevant records.
    *   `GET /health`: Basic health check endpoint.
*   **Project Structure:** The application follows a standard structure:
    *   `markr_app/`: Main application package.
        *   `views/`: Defines API endpoints (Blueprints).
        *   `services/`: Contains business logic (XML parsing, ingestion, aggregation).
        *   `models/`: Defines database models (SQLAlchemy).
        *   `utils/`: Contains utility functions (e.g., custom error classes, error handlers).
        *   `config.py`: Manages application configuration for different environments (Development, Testing, Production).
        *   `app.py`: Application factory and entry point.
        *   `database.py`: Initializes the SQLAlchemy database object.
    *   `tests/`: Contains automated tests using `pytest`.
*   **Containerization:** `Dockerfile` defines the application image. Docker and `docker-compose.yml` are provided for easy setup and deployment.
*   **Configuration:** Uses `.env` files (`python-dotenv`) and environment variables for configuration, separating concerns for different environments.
*   **Error Handling:** Custom exception classes (`ValidationError`, `ZeroMarksError`) and Flask error handlers provide meaningful error responses.

## Key Features & Highlights

*   **XML Ingestion:** Handles `text/xml+markr` POST requests.
*   **Data Persistence:** Stores results in a PostgreSQL database.
*   **Duplicate Resolution:** Implements logic to keep the highest score per student per test.
*   **Data Validation:** Validates incoming XML structure and required fields.
*   **Aggregate Statistics:** Calculates and returns mean, count, p25, p50, p75 as percentages.
*   **Testing:** Includes unit and integration tests for core functionality (parsing, ingestion, aggregation).
*   **Dockerized:** Easy to build, run, and deploy using Docker Compose.
*   **Configuration Management:** Flexible configuration via environment variables for different deployment scenarios.

## Performance Considerations (Prototype)

*   **Aggregation:** The current implementation fetches all results for a given `test_id` into memory and uses NumPy for calculations. While suitable for the prototype stage, this approach might become slow for tests with a very large number of submissions.
*   **Indexing:** A database index has been added to the `test_id` column in the `test_results` table (`models.py`). This speeds up the initial query to find relevant records for aggregation.

## How to Build and Run

**Prerequisites:**

*   Docker
*   Docker Compose

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/jaiphookan20/Markr.git
    cd Markr # Or your project directory name
    ```

2.  **Set up Environment Variables:**
    *   **For Docker (Recommended):**
        *   Copy the example Docker environment file:
            ```bash
            cp .env.docker.example .env.docker
            ```
        *   *(Optional)* Modify `.env.docker` if you need to change database credentials or other settings. The defaults should work out-of-the-box with the provided `docker-compose.yml`.
    *   **For Local Development (without Docker for the app, potentially with Docker for DB):**
        *   Copy the example environment file:
            ```bash
            cp .env.example .env
            ```
        *   Modify `.env` to set the correct `DATABASE_URL` pointing to your local or Dockerized PostgreSQL instance (e.g., `postgresql://postgres:ABCDE@localhost:5432/markrdb`). Ensure other variables like `SECRET_KEY` are set appropriately.

3.  **Build and Run using Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    *   This command builds the Docker images (if necessary) and starts the `app` and `db` services in detached mode.
    *   The Flask application will be accessible at `http://localhost:5000`.

4.  **Accessing the Service:**
    *   **Import Data:**
        ```bash
        curl -X POST -H 'Content-Type: text/xml+markr' http://localhost:5000/import -d @sample_results.xml
        ```
        (Assuming `sample_results.xml` is in your current directory)
    *   **Get Aggregates:** Replace `1234` with the actual `test-id`.
        ```bash
        curl http://localhost:5000/results/1234/aggregate
        ```
    *   **Health Check:**
        ```bash
        curl http://localhost:5000/health
        ```

5.  **Running Tests:**
    *   Execute the tests within the running `app` container. The command uses `docker-compose exec` to run commands inside the `app` service container.
    *   It sets the `FLASK_ENV` environment variable to `testing` to ensure the application uses the test configuration.
    *   It runs the `setup-test.sh` script, which ensures the test database (`markrdb_test`) exists on the `db` service before executing the tests.
    *   Finally, it runs `pytest` targeting the `markr_app/tests` directory. Use the command below to run the tests:
        ```bash
        docker-compose exec -e FLASK_ENV=testing app sh -c "./setup-test.sh && pytest markr_app/tests"
        ```

6.  **Stopping the Services:**
    ```bash
    docker-compose down
    ```
