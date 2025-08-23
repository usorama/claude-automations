# Data Pipeline Templates

## 1. Apache Airflow DAG Template

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import logging

# DAG Configuration
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_pipeline_template',
    default_args=default_args,
    description='Template for data processing pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['data', 'etl'],
)

def extract_data(**context):
    """Extract data from source systems"""
    try:
        # Implementation here
        logging.info("Data extraction completed successfully")
        return {'status': 'success', 'records': 1000}
    except Exception as e:
        logging.error(f"Data extraction failed: {e}")
        raise

def transform_data(**context):
    """Transform and validate data"""
    try:
        # Get data from previous task
        extract_result = context['task_instance'].xcom_pull(task_ids='extract')
        
        # Transform data
        # Implementation here
        
        logging.info("Data transformation completed successfully")
        return {'status': 'success', 'processed_records': 950}
    except Exception as e:
        logging.error(f"Data transformation failed: {e}")
        raise

def load_data(**context):
    """Load data to target systems"""
    try:
        transform_result = context['task_instance'].xcom_pull(task_ids='transform')
        
        # Load data
        # Implementation here
        
        logging.info("Data loading completed successfully")
        return {'status': 'success'}
    except Exception as e:
        logging.error(f"Data loading failed: {e}")
        raise

# Define tasks
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load_data,
    dag=dag,
)

# Define dependencies
extract_task >> transform_task >> load_task
```

## 2. Data Validation Template

```python
import pandas as pd
from typing import Dict, List, Any
import logging

class DataValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.errors = []
    
    def validate_schema(self, df: pd.DataFrame, expected_schema: Dict[str, str]) -> bool:
        """Validate dataframe schema against expected schema"""
        for column, expected_type in expected_schema.items():
            if column not in df.columns:
                self.errors.append(f"Missing column: {column}")
                return False
            
            if str(df[column].dtype) != expected_type:
                self.errors.append(f"Column {column} type mismatch: expected {expected_type}, got {df[column].dtype}")
                return False
        
        return True
    
    def validate_data_quality(self, df: pd.DataFrame, rules: Dict[str, Any]) -> bool:
        """Validate data quality based on rules"""
        is_valid = True
        
        # Null value checks
        if 'null_tolerance' in rules:
            for column, max_null_pct in rules['null_tolerance'].items():
                null_pct = (df[column].isnull().sum() / len(df)) * 100
                if null_pct > max_null_pct:
                    self.errors.append(f"Column {column} has {null_pct:.2f}% null values, exceeds limit of {max_null_pct}%")
                    is_valid = False
        
        # Range checks
        if 'range_checks' in rules:
            for column, (min_val, max_val) in rules['range_checks'].items():
                if df[column].min() < min_val or df[column].max() > max_val:
                    self.errors.append(f"Column {column} values outside expected range [{min_val}, {max_val}]")
                    is_valid = False
        
        # Uniqueness checks
        if 'unique_columns' in rules:
            for column in rules['unique_columns']:
                if df[column].duplicated().any():
                    self.errors.append(f"Column {column} contains duplicate values")
                    is_valid = False
        
        return is_valid
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'error_count': len(self.errors)
        }

# Usage example
validator = DataValidator({})
validation_rules = {
    'null_tolerance': {'user_id': 0, 'email': 0, 'created_date': 5},
    'range_checks': {'age': (0, 120), 'score': (0, 100)},
    'unique_columns': ['user_id', 'email']
}

expected_schema = {
    'user_id': 'int64',
    'email': 'object',
    'age': 'int64',
    'score': 'float64',
    'created_date': 'datetime64[ns]'
}

# Validate data
df = pd.read_csv('input_data.csv')
schema_valid = validator.validate_schema(df, expected_schema)
quality_valid = validator.validate_data_quality(df, validation_rules)

report = validator.get_validation_report()
logging.info(f"Validation report: {report}")
```

## 3. Spark Data Processing Template

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

class SparkDataProcessor:
    def __init__(self, app_name: str):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
    
    def read_data(self, source_config: dict):
        """Read data from various sources"""
        source_type = source_config.get('type')
        
        if source_type == 'parquet':
            return self.spark.read.parquet(source_config['path'])
        elif source_type == 'csv':
            return self.spark.read.option("header", "true").csv(source_config['path'])
        elif source_type == 'jdbc':
            return self.spark.read.format("jdbc") \
                .option("url", source_config['url']) \
                .option("dbtable", source_config['table']) \
                .option("user", source_config['user']) \
                .option("password", source_config['password']) \
                .load()
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def process_data(self, df, transformations: list):
        """Apply transformations to dataframe"""
        processed_df = df
        
        for transform in transformations:
            transform_type = transform.get('type')
            
            if transform_type == 'filter':
                processed_df = processed_df.filter(transform['condition'])
            elif transform_type == 'select':
                processed_df = processed_df.select(*transform['columns'])
            elif transform_type == 'aggregate':
                processed_df = processed_df.groupBy(*transform['group_by']) \
                    .agg(*[eval(agg) for agg in transform['aggregations']])
            elif transform_type == 'join':
                other_df = transform['other_df']
                processed_df = processed_df.join(other_df, transform['on'], transform.get('how', 'inner'))
            elif transform_type == 'custom':
                processed_df = transform['function'](processed_df)
        
        return processed_df
    
    def write_data(self, df, target_config: dict):
        """Write data to target systems"""
        target_type = target_config.get('type')
        mode = target_config.get('mode', 'overwrite')
        
        writer = df.write.mode(mode)
        
        if target_type == 'parquet':
            if 'partition_by' in target_config:
                writer = writer.partitionBy(*target_config['partition_by'])
            writer.parquet(target_config['path'])
        elif target_type == 'csv':
            writer.option("header", "true").csv(target_config['path'])
        elif target_type == 'jdbc':
            writer.format("jdbc") \
                .option("url", target_config['url']) \
                .option("dbtable", target_config['table']) \
                .option("user", target_config['user']) \
                .option("password", target_config['password']) \
                .save()
    
    def cleanup(self):
        """Clean up Spark session"""
        self.spark.stop()

# Usage example
processor = SparkDataProcessor("data_processing_pipeline")

# Configuration
source_config = {
    'type': 'parquet',
    'path': 's3a://data-lake/raw/user_events/'
}

transformations = [
    {'type': 'filter', 'condition': 'event_type = "purchase"'},
    {'type': 'select', 'columns': ['user_id', 'event_time', 'amount', 'product_id']},
    {'type': 'aggregate', 'group_by': ['user_id'], 'aggregations': ['sum(amount).alias("total_spent")', 'count().alias("purchase_count")']}
]

target_config = {
    'type': 'parquet',
    'path': 's3a://data-lake/processed/user_purchases/',
    'mode': 'overwrite',
    'partition_by': ['date']
}

try:
    # Process data
    raw_df = processor.read_data(source_config)
    processed_df = processor.process_data(raw_df, transformations)
    processor.write_data(processed_df, target_config)
    
    logging.info("Data processing completed successfully")
finally:
    processor.cleanup()
```

## 4. Configuration Template

```yaml
# pipeline-config.yaml
pipeline:
  name: "user_analytics_pipeline"
  version: "1.0.0"
  schedule: "0 2 * * *"  # Daily at 2 AM
  
  sources:
    - name: "user_events"
      type: "kafka"
      config:
        bootstrap_servers: "kafka-cluster:9092"
        topic: "user.events"
        consumer_group: "analytics_pipeline"
        
    - name: "user_profiles"
      type: "postgresql"
      config:
        host: "db.example.com"
        database: "users"
        table: "user_profiles"
        connection_pool_size: 5

  transformations:
    - name: "event_enrichment"
      type: "join"
      join_key: "user_id"
      
    - name: "aggregation"
      type: "window"
      window_size: "1 hour"
      functions:
        - "count(*) as event_count"
        - "avg(session_duration) as avg_session"

  targets:
    - name: "analytics_warehouse"
      type: "snowflake"
      config:
        account: "xy12345"
        warehouse: "ANALYTICS_WH"
        database: "ANALYTICS"
        schema: "USER_METRICS"
        table: "hourly_user_stats"

  quality_checks:
    - name: "completeness_check"
      type: "null_check"
      columns: ["user_id", "event_time"]
      threshold: 0.01
      
    - name: "freshness_check"
      type: "time_check"
      column: "event_time"
      max_delay_hours: 2

  monitoring:
    alerts:
      - type: "slack"
        webhook: "${SLACK_WEBHOOK_URL}"
        conditions:
          - "pipeline_failure"
          - "data_quality_failure"
          
    metrics:
      - "pipeline_duration"
      - "records_processed"
      - "error_rate"
      - "data_quality_score"

  retry_policy:
    max_retries: 3
    retry_delay: "5m"
    backoff_multiplier: 2
```

## 5. Docker Compose for Pipeline Infrastructure

```yaml
# docker-compose.yml
version: '3.8'

services:
  airflow-webserver:
    image: apache/airflow:2.7.1
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis

  airflow-scheduler:
    image: apache/airflow:2.7.1
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  spark-master:
    image: bitnami/spark:3.4
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
    ports:
      - "8081:8080"
      - "7077:7077"

  spark-worker:
    image: bitnami/spark:3.4
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=2G
      - SPARK_WORKER_CORES=2
    depends_on:
      - spark-master

volumes:
  postgres_data:
```