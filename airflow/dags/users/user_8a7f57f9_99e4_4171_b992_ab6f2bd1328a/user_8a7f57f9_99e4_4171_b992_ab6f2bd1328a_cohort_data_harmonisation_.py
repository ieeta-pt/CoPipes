from airflow import DAG
from datetime import datetime
import sys
import os

# Add the DAGs folder to the Python path for subfolder imports
if '/opt/airflow/dags' not in sys.path:
    sys.path.insert(0, '/opt/airflow/dags')

from components.transformation.cohorts.migrate import migrate
from components.loading.postgres.write_to_db import write_to_db
from components.transformation.cohorts.harmonize import harmonize
from components.loading.postgres.create_connection import create_connection
from components.loading.postgres.create_table import create_table
from components.extraction.csv import csv
from components.transformation.cohorts.to_key_value import to_key_value

with DAG (
    dag_id="user_8a7f57f9_99e4_4171_b992_ab6f2bd1328a_Cohort_data_harmonisation_",
    schedule=None,
    start_date=None,
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    csv_mjd = csv(filename='20190510 EMIF Patient Data.csv', file_separation=',')
    csv_sjw = csv(filename='UsagiExportContentMapping_v6.csv', file_separation=',')
    csv_jwo = csv(filename='UsagiExportColumnMapping_v2.csv', file_separation=',')
    to_key_value_85b = to_key_value(data=csv_mjd, fixed_columns='', measurement_columns='')
    harmonize_y3c = harmonize(data=to_key_value_85b, mappings=csv_sjw, adhoc_harmonization='False')
    migrate_c70 = migrate(person_data=harmonize_y3c, observation_data=harmonize_y3c, mappings=csv_jwo, adhoc_migration='False')
    create_connection_4a8 = create_connection(conn_id='my_postgres', host='postgres', schema='airflow', login='airflow', password='airflow', port='5432')
    create_table_eay = create_table(columns='person_id,gender_concept_id,year_of_birth,month_of_birth,day_of_birth,birth_datetime,death_datetime,race_concept_id,ethnicity_concept_id,location_id,provider_id,care_site_id,person_source_value,gender_source_value,gender_source_concept_id,race_source_value,race_source_concept_id,ethnicity_source_value,ethnicity_source_concept_id', table_name='person')
    write_to_db_zf6 = write_to_db(data=migrate_c70, table_name='person', conn_id='my_postgres')

    csv_mjd >> csv_sjw
    csv_sjw >> csv_jwo
    csv_jwo >> to_key_value_85b
    to_key_value_85b >> harmonize_y3c
    harmonize_y3c >> migrate_c70
    migrate_c70 >> create_connection_4a8
    create_connection_4a8 >> create_table_eay
    create_table_eay >> write_to_db_zf6
