from datetime import datetime
from airflow import DAG

from components.extract.csv import extract_csv
from components.cohorts.transform_to_kv import transform_to_kv
from components.cohorts.harmonizer import harmonize
from components.cohorts.migrator import migrate

##### UTILS FUNCTIONS #####

def get_files():
    csv_files = ["/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Diagnosis.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Sleep.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Blood and CSF.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Neuropsychology.csv", "/opt/airflow/data/input_data/0_CSVs/20190510 EMIF Patient Data.csv"]
    return csv_files

with DAG (
    'multiple_files_dag',
    schedule_interval=None,
    start_date=datetime(2025, 2, 3),
    catchup=False
) as dag:

    files = get_files()

    extract_csv_task = extract_csv.expand(filename=files)

    transform_task = transform_to_kv.expand(data=extract_csv_task)

    extract_mappings_task = extract_csv(
        filename = "/opt/airflow/data/input_data/UsagiContentMapping_v5.csv"
    )

    harmonizer_task = harmonize.partial(
            mappings=extract_mappings_task
        ).expand(
            data = transform_task,
    )

    migrator_task = migrate(data=harmonizer_task)

    extract_csv_task >> transform_task >> extract_mappings_task >> harmonizer_task >> migrator_task
