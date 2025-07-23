# CoPipes

CoPipes is a collaborative platform for ETL (Extract, Transform, Load) processes and data analysis. It enables teams to design, execute, and monitor data workflows with ease. **[Work in progress]**

## Features
- Visual workflow editor for ETL pipelines
- Integration with Apache Airflow for orchestration
- FastAPI backend for workflow management and API access
- Next.js frontend for a modern, collaborative UI
- PostgreSQL for data storage
- Dockerized, easy local development and deployment

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/)

### Environment Variables
You need a `.env` file at the project root with all required variables for the services. **If you don't have one, create it based on the variables referenced in `docker-compose.yaml` and your service configs.**

> **Tip:** For best practice, add a `.env.example` file to your repo listing all required variables and example values.

### Setup & Run
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ieeta-pt/CoPipes.git
   cd CoPipes
   ```
2. **Create your `.env` file:**
   - Add all necessary environment variables (see above).
3. **Build and start the environment:**
   ```bash
   docker compose up --build
   ```

## Project Structure
- `frontend/` — Next.js app (UI)
- `backend/api/` — FastAPI app (API, workflow logic)
- `airflow/` — Airflow DAGs, configs, and Docker setup
- `docker-compose.yaml` — Multi-service orchestration

## Development
- **Frontend:** See `frontend/README.md` for local dev instructions (e.g., `npm run dev`).
- **Backend:** Install dependencies from `backend/api/requirements.txt` and run with Uvicorn for local dev.
- **Airflow:** DAGs live in `airflow/dags/`.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)

---

For questions or support, please open an issue on GitHub.