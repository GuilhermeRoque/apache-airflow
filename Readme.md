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
#### DAG: The workflow/pipeline
```
from airflow import DAG
dag = DAG(
    dag_id="example_dag", 
    description="DAG example", 
    schedule_interval=None,
    start_date=datetime.datetime(2023,5,7),
    catchup=False
)
```
#### Operator: The class that holds a task definition. There are core and third-part operators, links:
- Core: https://airflow.apache.org/docs/apache-airflow/stable/operators-and-hooks-ref.html
- Providers: https://airflow.apache.org/docs/apache-airflow-providers/operators-and-hooks-ref/index.html
```
from airflow.operators.bash_operators import BashOperator
```
#### Task: The operator instance
```
tsk_1 = BashOperator(task_id="tsk_1", bash_command="echo 'HelloWorld'", dag=dag)
tsk_2 = BashOperator(task_id="tsk_2", bash_command="echo 'HelloWorld'", dag=dag)
```
#### Precedence: The sequence order for task execution
```
tsk_1 >> # sequential syntax
[tsk_1, tsk_2] # parallel syntax 
```
It's not possible, due to syntax issues, to define consecutive parallels executions.
To fix this we can use the _cross_downstream_ relationship helper.
```
# Raises an error

[tsk_1, tsk_2] >> [tsk_3, tsk_4]
```
```
# Using cross_downstream

from airflow.utils.helpers import cross_downstream

cross_downstream([tsk_1, tsk_2], [tsk_3, tsk_4])

```
#### Trigger Rule: Task execution condition. 
Ex _all_success_ (default), _all_failed_. It can be defined in DAG or Task, if defined in DAG it will be the default rule for all DAG's tasks.
```
tsk_3 = BashOperator(task_id="tsk_3", bash_command="echo 'Failed'", dag=dag, trigger_rule='all_failed')
```
Docs source: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules

#### TaskGroup: Organize tasks for view and precedence 
A TaskGroup can be used to organize tasks into hierarchical groups in Graph view and to define a common precedence rule 
(the group will be executed in parallel).
```
from airflow.utils.task_group import TaskGroup
tsk_group_hw = TaskGroup(group_id="tsk_group_hw", dag=dag)
tsk_1 = BashOperator(task_id="tsk_1", bash_command="echo 'HelloWorld'", dag=dag, task_group=tsk_group_hw)
tsk_2 = BashOperator(task_id="tsk_2", bash_command="echo 'HelloWorld'", dag=dag, task_group=tsk_group_hw)
tsk_group_hw >> tsk_3
```
#### TriggerDagRunOperator: Run DAGs as tasks
```
from airflow.operators.dagrun_operator import TriggerDagRunOperator
task_dag = TriggerDagRunOperator(task_id="task_dag", trigger_dag_id="other_dag_id", dag=dag)
```
#### XCOM: Task communication
```
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(dag_id="demo", start_date=datetime(2022, 1, 1), schedule="0 0 * * *") as dag:
    # Tasks are represented as operators
    def hello_world_write(**kwargs):
        kwargs['ti'].xcom_push(key="message", value="hello world")
    
    
    def hello_world_read(**kwargs):
        message = kwargs['ti'].xcom_pull(key="message")
        print(f"message {message}")
    
    tsk_hello_world_write = PythonOperator(task_id="tsk_hello_world_write", python_callable=hello_world_write)
    tsk_hello_world_read = PythonOperator(task_id="tsk_hello_world_read", python_callable=hello_world_write)

    tsk_hello_world_write >> tsk_hello_world_read
```
#### Branch: Conditional task execution in pipeline
The BranchPythonOperator is much like the PythonOperator except that it expects a python_callable that returns a task_id.
```
from airflow.operators.python_operator import PythonOperator
def branch_func(**kwargs):
    ti = kwargs['ti']
    xcom_value = int(ti.xcom_pull(task_ids='start_task'))
    if xcom_value >= 5:
        return 'continue_task'
    else:
        return 'stop_task'

start_op = BashOperator(
    task_id='start_task',
    bash_command="echo 5",
    xcom_push=True,
    dag=dag)

branch_op = BranchPythonOperator(
    task_id='branch_task',
    provide_context=True,
    python_callable=branch_func,
    dag=dag)

continue_op = DummyOperator(task_id='continue_task', dag=dag)
stop_op = DummyOperator(task_id='stop_task', dag=dag)

start_op >> branch_op >> [continue_op, stop_op]
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

### Variables
Share information between DAGs and can be created in UI or CLI. Examples:
- API Credentials
- URLs
- Auth keys
```
from airflow.models import Variable

Variable.get("my_var")
```
### How to use GMAIL to email notifications
Note: Other SMTP server can be used
- Access your gmail account
  - On the top right icon on the Google page
  - Click on "Manage Google Account"
- Go to security section
- Active 2-step verification
- Go to App Passwords section
- Create a new password
- Set the SMTP environment variables:
```
AIRFLOW__SMTP__SMTP_HOST: smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT: 587
AIRFLOW__SMTP__SMTP_USER: <your_email>
AIRFLOW__SMTP__SMTP_PASSWORD: <created_password>
AIRFLOW__SMTP__SMTP_MAIL_FROM: Airflow
```

### Writing DAGs  
- Install apache airflow python module
```
pip install apache-airflow==2.6.0
```
- Write then in files in the **./dags** dir

### Pools
Manage concurrency and resource allocation between tasks. 
A pool can be configured in the UI or CLI and in the pool configuration we are able to specify the workers amount (concurrency level).
```
tsk_1 = BashOperator(
  task_id="tsk_1", 
  bash_command="echo 'HelloWorld'", 
  dag=dag, 
  pool="my-pool", # pool previously created in the UI
  priority_weight=10 # higher weight means prior execution
)
```
