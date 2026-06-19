# OSINT Agent

A Dockerized OSINT agent built with Streamlit and Gemini 2.0 Flash.

## Setup Instructions

1. **Clone & Environment:**
   Clone the repository and copy the environment template:
   ```bash
   cp .env.example .env
   ```
   Add your API keys to the `.env` file (Get a free Gemini API key at aistudio.google.com).

2. **Build and Run:**
   Run the application using Docker Compose (Note: the compose file is located in the `docker` directory):
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

3. **Access the Application:**
   Open your browser and navigate to `http://localhost:8501`. 
   
   **Login Credentials:**
   - Username: `admin`
   - Password: `osint`

## Stopping and Managing the Container

* **Stop the Agent:**
  To stop the running container, run:
  ```bash
  docker-compose -f docker/docker-compose.yml down
  ```

* **Clean up Volumes:**
  If you want to stop the container and delete mounted volumes or caches, run:
  ```bash
  docker-compose -f docker/docker-compose.yml down -v
  ```

