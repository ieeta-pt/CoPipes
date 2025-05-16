FROM apache/airflow:2.10.4

ENV AIRFLOW_HOME=/opt/airflow

RUN pip install --no-cache-dir psycopg2-binary apache-airflow-providers-postgres

COPY dags/ $AIRFLOW_HOME/dags/
