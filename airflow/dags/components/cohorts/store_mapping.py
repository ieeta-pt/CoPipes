from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd

def store_mapping(table: str, **kwargs):
        ti = kwargs['ti']
        mapping_dict = ti.xcom_pull(key="mapping", task_ids="create_base_table")  
        
        if not mapping_dict:
            raise ValueError("No mapping data found in XCom!")

        mapping = pd.DataFrame.from_dict(mapping_dict)

        pg_hook = PostgresHook(postgres_conn_id="my_postgres")
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {", ".join([f'"{col}" TEXT' for col in mapping.columns])}
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()

        for _, row in mapping.iterrows():
            values = tuple(row.fillna("").astype(str))  
            placeholders = ", ".join(["%s"] * len(values))
            insert_sql = f'INSERT INTO {table} VALUES ({placeholders})'
            cursor.execute(insert_sql, values)

        conn.commit()
        cursor.close()
        conn.close()