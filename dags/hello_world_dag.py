from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.utils.helpers import cross_downstream
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator

cross_downstream


# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="demo", start_date=datetime(2022, 1, 1), schedule="0 0 * * *") as dag:
    # Tasks are represented as operators


    def hello_world_write(**kwargs):
        kwargs['ti'].xcom_push(key="message", value="hello world")


    def hello_world_read(**kwargs):
        message = kwargs['ti'].xcom_pull(key="message")
        print(f"message {message}")

    tsk_hello_world_write = PythonOperator(task_id="tsk_hello_world_write", python_callable=hello_world_write)
    tsk_hello_world_read = PythonOperator(task_id="tsk_hello_world_read", python_callable=hello_world_write)
    tsk_group_hw = TaskGroup(group_id="tsk_group_hw", dag=dag)


    @task()
    def airflow():
        print("airflow")


    # Set dependencies between tasks
    hello >> airflow()
