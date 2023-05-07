# Apache Airflow 2.6.0
Tutorial projects to learn the tool
### Quick start (should not be used for production)
- Check if there is at least 4GB of memory available (ideally 8GB)
```
docker run --rm "debian:bullseye-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'
```
- Download docker-compose file from apache airflow site https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.6.0/docker-compose.yaml'
```
- Follow the init steps https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#initializing-environment
```
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
sudo docker compose up airflow-init
```
- Up command
```
docker compose up
```
- Clean it up to restart from scratch
```
docker compose down --volumes --remove-orphans
```
- Accessing the web interface: The webserver is available at: http://localhost:8080. The default account has the login **airflow** and the password **airflow**.


### Concepts
- Dag: The workflow/pipeline
```
from airflow import DAG
dag = DAG(
    "example_dag", 
    description="DAG example", 
    schedule_interval=None,
    start_date=datetime.datetime(2023,5,7),
    catchup=False
)
```
- Operator: The class that holds a task definition
```
from airflow.operators.bash_operators import BashOperator
```
- Task: The operator instance
```
tsk_1 = BashOperator(task_id="tsk_1", bash_command="echo 'HelloWorld'", dag=dag)
tsk_2 = BashOperator(task_id="tsk_2", bash_command="echo 'HelloWorld'", dag=dag)
```
- Precedence: The sequence order for task execution
```
tsk_1 >> tsk_2
```
### Environment customization
Just paste it at the environment section of x-airflow-common service.
```
AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL: 20
AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL: 5
AIRFLOW__WEBSERVER__EXPOSE_CONFIG: true
AIRFLOW__CORE__LOAD_EXAMPLES: false
```
Docs source: https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html


