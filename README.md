# AI-Powered Banking System

This project was developed as my graduation project. It is an AI-powered banking system designed to support banking operations and provide intelligent predictions based on customer data.

I was mainly responsible for the backend development and database design of the system.

## My Role

I developed the backend using Python and FastAPI and worked on connecting the application with the database and AI models.

My work included:

- Building RESTful APIs using FastAPI
- Developing client and employee management APIs
- Implementing authentication functionality
- Developing follow-up and dashboard APIs
- Designing and integrating the database
- Handling database operations from the backend
- Integrating customer churn and loan prediction models
- Collaborating with the frontend team to connect the APIs with the user interface

## Technologies Used

- Python
- FastAPI
- REST APIs
- PostgreSQL
- Database Design
- Git and GitHub

## AI Features

The backend integrates AI models that support:

- Customer churn prediction
- Loan prediction

The prediction models are connected to the backend so the system can process customer data and return prediction results through the API.

## Project Structure

The backend is organized into separate components for API routes, database operations, authentication, and system features.

This structure helped keep the project organized and made it easier to develop and maintain different parts of the system.

## Running the Project

1. Clone the repository:

    git clone YOUR_REPOSITORY_URL

2. Move to the project directory:

    cd YOUR_PROJECT_FOLDER

3. Create a virtual environment:

    python -m venv venv

4. Activate the virtual environment.

    On Windows:

    venv\Scripts\activate

5. Install the required dependencies:

    pip install -r requirements.txt

6. Run the FastAPI application:

    uvicorn main:app --reload

7. Open the API documentation:

    http://127.0.0.1:8000/docs

## API Documentation

FastAPI automatically provides interactive API documentation using Swagger UI.

After running the application, the API endpoints can be tested through the `/docs` page.

## What I Learned

Working on this project gave me practical experience in backend development, API design, database integration, and working within a team.

It also helped me understand how backend services can integrate with AI models and frontend applications in a complete system.