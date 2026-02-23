FROM apache/airflow:2.10.4

ENV AIRFLOW_HOME=/opt/airflow

RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt" \
    psycopg2-binary \
    apache-airflow-providers-postgres \
    apache-airflow-providers-papermill \
    scikit-learn joblib pandas numpy matplotlib seaborn \
    papermill scrapbook jupyter supabase

COPY dags/ $AIRFLOW_HOME/dags/
