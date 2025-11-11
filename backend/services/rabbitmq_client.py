"""
RabbitMQ client for message queue operations.
"""
import pika
import json
import os
from typing import Dict, Any, Optional, Callable
from uuid import UUID
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """
    RabbitMQ client for publishing and consuming messages.
    """

    def __init__(self, rabbitmq_url: Optional[str] = None):
        """
        Initialize RabbitMQ client.

        Args:
            rabbitmq_url: RabbitMQ connection URL
        """
        self.rabbitmq_url = rabbitmq_url or os.getenv(
            "RABBITMQ_URL",
            "amqp://guest:guest@localhost:5672/"
        )
        self.connection = None
        self.channel = None

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((pika.exceptions.AMQPConnectionError, ConnectionError)),
        reraise=True
    )
    def connect(self):
        """Establish connection to RabbitMQ with retry logic."""
        if self.connection is None or self.connection.is_closed:
            logger.info(f"Attempting to connect to RabbitMQ at {self.rabbitmq_url}")
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ")

    def close(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")

    def declare_queue(self, queue_name: str, durable: bool = True):
        """
        Declare a queue.

        Args:
            queue_name: Name of the queue
            durable: Whether the queue should survive broker restart
        """
        self.connect()
        self.channel.queue_declare(queue=queue_name, durable=durable)

    def declare_exchange(
        self,
        exchange_name: str,
        exchange_type: str = "fanout",
        durable: bool = True
    ):
        """
        Declare an exchange.

        Args:
            exchange_name: Name of the exchange
            exchange_type: Type of exchange (fanout, direct, topic, headers)
            durable: Whether the exchange should survive broker restart
        """
        self.connect()
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable
        )

    def publish_segment_task(
        self,
        segment_id: UUID,
        render_job_id: UUID,
        prompt: str,
        model_params: Dict[str, Any],
        queue_name: str = "segment_generation"
    ):
        """
        Publish a segment generation task to the queue.

        Args:
            segment_id: UUID of the segment
            render_job_id: UUID of the render job
            prompt: Video generation prompt
            model_params: Model parameters
            queue_name: Name of the queue
        """
        self.connect()
        self.declare_queue(queue_name)

        message = {
            "version": 2,
            "segment_id": str(segment_id),
            "render_job_id": str(render_job_id),
            "prompt": prompt,
            "model_params": model_params
        }

        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type="application/json"
            )
        )

        logger.info(f"Published segment task: segment_id={segment_id}, render_job_id={render_job_id}")

    def publish_composition_task(
        self,
        render_job_id: UUID,
        project_id: UUID,
        segment_ids: list[UUID],
        queue_name: str = "video_composition"
    ):
        """
        Publish a video composition task to the queue.

        Args:
            render_job_id: UUID of the render job
            project_id: UUID of the project
            segment_ids: List of segment UUIDs in order
            queue_name: Name of the queue
        """
        self.connect()
        self.declare_queue(queue_name)

        message = {
            "version": 2,
            "render_job_id": str(render_job_id),
            "project_id": str(project_id),
            "segment_ids": [str(sid) for sid in segment_ids],
            "event": "compose_video"
        }

        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )

        logger.info(f"Published composition task: render_job_id={render_job_id}")

    def publish_segment_completed_event(
        self,
        segment_id: UUID,
        render_job_id: UUID,
        exchange_name: str = "segment_completed"
    ):
        """
        Publish a segment completion event to an exchange.

        Args:
            segment_id: UUID of the completed segment
            render_job_id: UUID of the render job
            exchange_name: Name of the exchange
        """
        self.connect()
        self.declare_exchange(exchange_name, exchange_type="fanout")

        message = {
            "segment_id": str(segment_id),
            "render_job_id": str(render_job_id),
            "event": "segment_completed"
        }

        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key="",  # Fanout ignores routing key
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )

        logger.info(f"Published segment completed event: segment_id={segment_id}")

    def consume_messages(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any]], None],
        auto_ack: bool = False
    ):
        """
        Consume messages from a queue.

        Args:
            queue_name: Name of the queue
            callback: Function to process messages
            auto_ack: Whether to automatically acknowledge messages
        """
        self.connect()
        self.declare_queue(queue_name)

        def message_callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_callback,
            auto_ack=auto_ack
        )

        logger.info(f"Starting to consume messages from {queue_name}")
        self.channel.start_consuming()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
