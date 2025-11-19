"""
Streaming Monitoring DAG

This DAG monitors Kafka consumer lag for streaming data pipelines.
Checks consumer group lag and logs warnings if lag exceeds threshold.
"""
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import logging
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from kafka.errors import KafkaError

# Kafka Configuration
KAFKA_BROKER = "kafka:9092"  # Replace with your Kafka broker if needed
KAFKA_TOPIC = "sensor_readings"
CONSUMER_GROUP = "sensor_readings_consumer"
LAG_THRESHOLD = 10  # Adjust this threshold as per business needs

def check_kafka_consumer_lag():
    """
    Connects to Kafka, retrieves consumer group lag, and logs warnings if lag exceeds threshold.
    """
    consumer = None
    try:
        logging.info(f"Connecting to Kafka broker: {KAFKA_BROKER}")

        # Create Kafka Consumer to fetch partitions and offsets
        consumer = KafkaConsumer(
            bootstrap_servers=KAFKA_BROKER,
            group_id=CONSUMER_GROUP,
            enable_auto_commit=False,
            consumer_timeout_ms=5000
        )

        # Get partitions for the topic
        partitions = consumer.partitions_for_topic(KAFKA_TOPIC)
        
        if not partitions:
            logging.warning(f"Topic '{KAFKA_TOPIC}' not found or has no partitions")
            return

        logging.info(f"Partitions for topic '{KAFKA_TOPIC}': {partitions}")

        # Create TopicPartition objects for all partitions
        topic_partitions = [TopicPartition(KAFKA_TOPIC, p) for p in partitions]
        
        # Get committed offsets (where consumer group last left off)
        committed_offsets = consumer.committed(set(topic_partitions))
        
        # Get end offsets (latest available offset for each partition)
        end_offsets = consumer.end_offsets(set(topic_partitions))

        # Calculate lag for each partition
        for tp in topic_partitions:
            partition = tp.partition
            committed_offset = committed_offsets.get(tp)
            latest_offset = end_offsets.get(tp, 0)

            if committed_offset is not None:
                # Calculate Lag
                lag = latest_offset - committed_offset
                logging.info(
                    f"Partition {partition}: Committed Offset = {committed_offset}, "
                    f"Latest Offset = {latest_offset}, Consumer Lag = {lag}"
                )

                # Raise alert if lag exceeds threshold
                if lag > LAG_THRESHOLD:
                    logging.warning(
                        f"ALERT! Consumer lag detected on {KAFKA_TOPIC}[{partition}]. "
                        f"Lag: {lag} (threshold: {LAG_THRESHOLD})"
                    )
            else:
                logging.warning(
                    f"No committed offset found for partition {partition}. "
                    f"Consumer group '{CONSUMER_GROUP}' may not have consumed from this partition yet."
                )

        logging.info("Kafka consumer lag monitoring complete.")

    except KafkaError as e:
        logging.error(f"Kafka connection error: {str(e)}")
        raise
    except Exception as ex:
        logging.error(f"Error while monitoring Kafka consumer lag: {str(ex)}")
        raise
    finally:
        if consumer:
            consumer.close()

# Airflow DAG Configuration
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1
}

with DAG(
        dag_id='streaming_monitoring_dag',
        default_args=default_args,
        schedule_interval='@hourly',
        catchup=False
) as dag:

    monitor_kafka_task = PythonOperator(
        task_id='monitor_kafka_consumer_lag',
        python_callable=check_kafka_consumer_lag
    )

