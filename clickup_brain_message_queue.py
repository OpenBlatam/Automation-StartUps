#!/usr/bin/env python3
"""
ClickUp Brain Message Queue System
=================================

Asynchronous message queue system with Redis backend, task scheduling,
dead letter queues, and distributed processing support.
"""

import asyncio
import json
import time
import uuid
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager

ROOT = Path(__file__).parent

class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

class Priority(Enum):
    """Task priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Message queue task."""
    id: str
    queue_name: str
    payload: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 300  # seconds
    error_message: Optional[str] = None
    result: Optional[Any] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class QueueConfig:
    """Queue configuration."""
    name: str
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 300
    dead_letter_queue: Optional[str] = None
    visibility_timeout: int = 30
    max_messages: int = 10000
    priority: bool = True

@dataclass
class WorkerConfig:
    """Worker configuration."""
    worker_id: str
    queue_names: List[str]
    max_concurrent_tasks: int = 5
    poll_interval: float = 1.0
    heartbeat_interval: int = 30
    shutdown_timeout: int = 30

class MessageQueue:
    """Redis-based message queue implementation."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", key_prefix: str = "mq:"):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.logger = logging.getLogger("message_queue")
        self._redis = None
        self._lock = threading.RLock()
    
    async def _get_redis(self):
        """Get Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                raise ImportError("redis package is required for message queue")
        return self._redis
    
    def _make_key(self, key: str) -> str:
        """Make full key with prefix."""
        return f"{self.key_prefix}{key}"
    
    async def enqueue(self, task: Task) -> bool:
        """Enqueue a task."""
        try:
            redis_client = await self._get_redis()
            
            # Serialize task
            task_data = {
                'id': task.id,
                'queue_name': task.queue_name,
                'payload': task.payload,
                'priority': task.priority.value,
                'status': task.status.value,
                'created_at': task.created_at.isoformat(),
                'retry_count': task.retry_count,
                'max_retries': task.max_retries,
                'retry_delay': task.retry_delay,
                'timeout': task.timeout,
                'tags': task.tags
            }
            
            # Add to queue
            queue_key = self._make_key(f"queue:{task.queue_name}")
            score = task.priority.value * 1000000 + int(time.time())
            await redis_client.zadd(queue_key, {json.dumps(task_data): score})
            
            # Store task metadata
            task_key = self._make_key(f"task:{task.id}")
            await redis_client.hset(task_key, mapping={
                'status': task.status.value,
                'created_at': task.created_at.isoformat(),
                'queue_name': task.queue_name
            })
            
            # Set expiration for task metadata
            await redis_client.expire(task_key, 86400 * 7)  # 7 days
            
            self.logger.info(f"Enqueued task {task.id} to queue {task.queue_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enqueue task: {e}")
            return False
    
    async def dequeue(self, queue_name: str, visibility_timeout: int = 30) -> Optional[Task]:
        """Dequeue a task from queue."""
        try:
            redis_client = await self._get_redis()
            queue_key = self._make_key(f"queue:{queue_name}")
            
            # Get highest priority task
            result = await redis_client.zpopmax(queue_key, count=1)
            if not result:
                return None
            
            task_json, score = result[0]
            task_data = json.loads(task_json)
            
            # Create task object
            task = Task(
                id=task_data['id'],
                queue_name=task_data['queue_name'],
                payload=task_data['payload'],
                priority=Priority(task_data['priority']),
                status=TaskStatus.PROCESSING,
                created_at=datetime.fromisoformat(task_data['created_at']),
                started_at=datetime.now(),
                retry_count=task_data['retry_count'],
                max_retries=task_data['max_retries'],
                retry_delay=task_data['retry_delay'],
                timeout=task_data['timeout'],
                tags=task_data['tags']
            )
            
            # Update task status
            task_key = self._make_key(f"task:{task.id}")
            await redis_client.hset(task_key, mapping={
                'status': task.status.value,
                'started_at': task.started_at.isoformat()
            })
            
            # Add to processing set with visibility timeout
            processing_key = self._make_key(f"processing:{queue_name}")
            await redis_client.zadd(processing_key, {task.id: time.time() + visibility_timeout})
            
            self.logger.info(f"Dequeued task {task.id} from queue {queue_name}")
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to dequeue task: {e}")
            return None
    
    async def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark task as completed."""
        try:
            redis_client = await self._get_redis()
            task_key = self._make_key(f"task:{task_id}")
            
            # Update task status
            await redis_client.hset(task_key, mapping={
                'status': TaskStatus.COMPLETED.value,
                'completed_at': datetime.now().isoformat(),
                'result': json.dumps(result) if result is not None else None
            })
            
            # Remove from processing set
            task_info = await redis_client.hgetall(task_key)
            queue_name = task_info.get('queue_name', '')
            if queue_name:
                processing_key = self._make_key(f"processing:{queue_name}")
                await redis_client.zrem(processing_key, task_id)
            
            self.logger.info(f"Completed task {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete task {task_id}: {e}")
            return False
    
    async def fail_task(self, task_id: str, error_message: str, retry: bool = True) -> bool:
        """Mark task as failed and optionally retry."""
        try:
            redis_client = await self._get_redis()
            task_key = self._make_key(f"task:{task_id}")
            
            # Get task info
            task_info = await redis_client.hgetall(task_key)
            if not task_info:
                return False
            
            retry_count = int(task_info.get('retry_count', 0))
            max_retries = int(task_info.get('max_retries', 3))
            queue_name = task_info.get('queue_name', '')
            
            if retry and retry_count < max_retries:
                # Retry task
                retry_count += 1
                retry_delay = float(task_info.get('retry_delay', 1.0))
                
                await redis_client.hset(task_key, mapping={
                    'status': TaskStatus.RETRYING.value,
                    'retry_count': retry_count,
                    'error_message': error_message,
                    'retry_at': (datetime.now() + timedelta(seconds=retry_delay)).isoformat()
                })
                
                # Re-enqueue with delay
                await asyncio.sleep(retry_delay)
                await self._reenqueue_task(task_id, queue_name)
                
                self.logger.info(f"Retrying task {task_id} (attempt {retry_count}/{max_retries})")
            else:
                # Move to dead letter queue or mark as failed
                await redis_client.hset(task_key, mapping={
                    'status': TaskStatus.DEAD_LETTER.value if retry_count >= max_retries else TaskStatus.FAILED.value,
                    'error_message': error_message,
                    'failed_at': datetime.now().isoformat()
                })
                
                self.logger.error(f"Task {task_id} failed permanently: {error_message}")
            
            # Remove from processing set
            if queue_name:
                processing_key = self._make_key(f"processing:{queue_name}")
                await redis_client.zrem(processing_key, task_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fail task {task_id}: {e}")
            return False
    
    async def _reenqueue_task(self, task_id: str, queue_name: str) -> None:
        """Re-enqueue a task for retry."""
        try:
            redis_client = await self._get_redis()
            task_key = self._make_key(f"task:{task_id}")
            
            # Get task data
            task_info = await redis_client.hgetall(task_key)
            if not task_info:
                return
            
            # Create task object
            task = Task(
                id=task_id,
                queue_name=queue_name,
                payload=json.loads(task_info.get('payload', '{}')),
                priority=Priority(int(task_info.get('priority', 2))),
                status=TaskStatus.PENDING,
                created_at=datetime.fromisoformat(task_info.get('created_at', datetime.now().isoformat())),
                retry_count=int(task_info.get('retry_count', 0)),
                max_retries=int(task_info.get('max_retries', 3)),
                retry_delay=float(task_info.get('retry_delay', 1.0)),
                timeout=int(task_info.get('timeout', 300)),
                tags=json.loads(task_info.get('tags', '[]'))
            )
            
            # Re-enqueue
            await self.enqueue(task)
            
        except Exception as e:
            self.logger.error(f"Failed to re-enqueue task {task_id}: {e}")
    
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get queue statistics."""
        try:
            redis_client = await self._get_redis()
            queue_key = self._make_key(f"queue:{queue_name}")
            processing_key = self._make_key(f"processing:{queue_name}")
            
            pending_count = await redis_client.zcard(queue_key)
            processing_count = await redis_client.zcard(processing_key)
            
            return {
                'queue_name': queue_name,
                'pending_tasks': pending_count,
                'processing_tasks': processing_count,
                'total_tasks': pending_count + processing_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
            return {'queue_name': queue_name, 'error': str(e)}

class TaskWorker:
    """Task worker for processing messages."""
    
    def __init__(self, config: WorkerConfig, message_queue: MessageQueue):
        self.config = config
        self.message_queue = message_queue
        self.logger = logging.getLogger(f"worker_{config.worker_id}")
        self.running = False
        self.tasks: Dict[str, asyncio.Task] = {}
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, queue_name: str, handler: Callable) -> None:
        """Register a handler for a queue."""
        self.handlers[queue_name] = handler
        self.logger.info(f"Registered handler for queue {queue_name}")
    
    async def start(self) -> None:
        """Start the worker."""
        self.running = True
        self.logger.info(f"Starting worker {self.config.worker_id}")
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self._heartbeat())
        
        # Start processing tasks
        processing_task = asyncio.create_task(self._process_tasks())
        
        try:
            await asyncio.gather(heartbeat_task, processing_task)
        except asyncio.CancelledError:
            self.logger.info(f"Worker {self.config.worker_id} cancelled")
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
        self.logger.info(f"Stopping worker {self.config.worker_id}")
        
        # Cancel all running tasks
        for task in self.tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.wait(self.tasks.values(), timeout=self.config.shutdown_timeout)
        
        self.tasks.clear()
    
    async def _process_tasks(self) -> None:
        """Main task processing loop."""
        while self.running:
            try:
                # Check if we can process more tasks
                if len(self.tasks) >= self.config.max_concurrent_tasks:
                    await asyncio.sleep(self.config.poll_interval)
                    continue
                
                # Try to get a task from any registered queue
                task = None
                for queue_name in self.config.queue_names:
                    if queue_name in self.handlers:
                        task = await self.message_queue.dequeue(queue_name)
                        if task:
                            break
                
                if task:
                    # Process task
                    task_handle = asyncio.create_task(self._handle_task(task))
                    self.tasks[task.id] = task_handle
                else:
                    # No tasks available, wait
                    await asyncio.sleep(self.config.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(self.config.poll_interval)
    
    async def _handle_task(self, task: Task) -> None:
        """Handle a single task."""
        try:
            self.logger.info(f"Processing task {task.id} from queue {task.queue_name}")
            
            # Get handler
            handler = self.handlers.get(task.queue_name)
            if not handler:
                await self.message_queue.fail_task(task.id, f"No handler for queue {task.queue_name}")
                return
            
            # Process task with timeout
            result = await asyncio.wait_for(
                handler(task.payload),
                timeout=task.timeout
            )
            
            # Mark as completed
            await self.message_queue.complete_task(task.id, result)
            self.logger.info(f"Completed task {task.id}")
            
        except asyncio.TimeoutError:
            await self.message_queue.fail_task(task.id, "Task timeout")
            self.logger.error(f"Task {task.id} timed out")
        except Exception as e:
            await self.message_queue.fail_task(task.id, str(e))
            self.logger.error(f"Task {task.id} failed: {e}")
        finally:
            # Remove from active tasks
            self.tasks.pop(task.id, None)
    
    async def _heartbeat(self) -> None:
        """Send heartbeat to indicate worker is alive."""
        while self.running:
            try:
                # Update worker status in Redis
                redis_client = await self.message_queue._get_redis()
                worker_key = self.message_queue._make_key(f"worker:{self.config.worker_id}")
                await redis_client.hset(worker_key, mapping={
                    'status': 'active',
                    'last_heartbeat': datetime.now().isoformat(),
                    'active_tasks': len(self.tasks),
                    'queue_names': json.dumps(self.config.queue_names)
                })
                await redis_client.expire(worker_key, self.config.heartbeat_interval * 2)
                
                await asyncio.sleep(self.config.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(self.config.heartbeat_interval)

class MessageQueueManager:
    """Main message queue management system."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.message_queue = MessageQueue(redis_url)
        self.workers: Dict[str, TaskWorker] = {}
        self.queues: Dict[str, QueueConfig] = {}
        self.logger = logging.getLogger("mq_manager")
    
    def create_queue(self, config: QueueConfig) -> None:
        """Create a new queue."""
        self.queues[config.name] = config
        self.logger.info(f"Created queue {config.name}")
    
    def create_worker(self, config: WorkerConfig) -> TaskWorker:
        """Create a new worker."""
        worker = TaskWorker(config, self.message_queue)
        self.workers[config.worker_id] = worker
        self.logger.info(f"Created worker {config.worker_id}")
        return worker
    
    async def enqueue_task(self, queue_name: str, payload: Dict[str, Any], 
                          priority: Priority = Priority.NORMAL, **kwargs) -> str:
        """Enqueue a task."""
        task_id = str(uuid.uuid4())
        
        queue_config = self.queues.get(queue_name)
        if not queue_config:
            raise ValueError(f"Queue {queue_name} not found")
        
        task = Task(
            id=task_id,
            queue_name=queue_name,
            payload=payload,
            priority=priority,
            max_retries=queue_config.max_retries,
            retry_delay=queue_config.retry_delay,
            timeout=queue_config.timeout,
            **kwargs
        )
        
        await self.message_queue.enqueue(task)
        return task_id
    
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get queue statistics."""
        return await self.message_queue.get_queue_stats(queue_name)
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues."""
        stats = {}
        for queue_name in self.queues.keys():
            stats[queue_name] = await self.get_queue_stats(queue_name)
        return stats

# Global message queue manager
mq_manager: Optional[MessageQueueManager] = None

def initialize_message_queue(redis_url: str = "redis://localhost:6379/0") -> MessageQueueManager:
    """Initialize global message queue manager."""
    global mq_manager
    mq_manager = MessageQueueManager(redis_url)
    return mq_manager

async def get_message_queue() -> MessageQueueManager:
    """Get global message queue manager."""
    global mq_manager
    if mq_manager is None:
        mq_manager = initialize_message_queue()
    return mq_manager

if __name__ == "__main__":
    # Demo message queue system
    print("ClickUp Brain Message Queue System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Initialize message queue
        mq = initialize_message_queue()
        
        # Create queues
        mq.create_queue(QueueConfig("email_queue", max_retries=3))
        mq.create_queue(QueueConfig("data_processing", max_retries=2))
        
        # Create worker
        worker_config = WorkerConfig(
            worker_id="demo_worker",
            queue_names=["email_queue", "data_processing"],
            max_concurrent_tasks=2
        )
        worker = mq.create_worker(worker_config)
        
        # Register handlers
        async def email_handler(payload):
            print(f"Sending email to {payload['to']}: {payload['subject']}")
            await asyncio.sleep(1)  # Simulate email sending
            return {"status": "sent", "message_id": "msg_123"}
        
        async def data_handler(payload):
            print(f"Processing data: {payload['data_type']}")
            await asyncio.sleep(2)  # Simulate data processing
            return {"status": "processed", "records": 100}
        
        worker.register_handler("email_queue", email_handler)
        worker.register_handler("data_processing", data_handler)
        
        # Start worker in background
        worker_task = asyncio.create_task(worker.start())
        
        # Enqueue some tasks
        await mq.enqueue_task("email_queue", {
            "to": "user@example.com",
            "subject": "Welcome!",
            "body": "Welcome to ClickUp Brain!"
        }, priority=Priority.HIGH)
        
        await mq.enqueue_task("data_processing", {
            "data_type": "user_analytics",
            "date_range": "2025-01-01 to 2025-01-07"
        }, priority=Priority.NORMAL)
        
        # Wait for tasks to process
        await asyncio.sleep(5)
        
        # Get stats
        stats = await mq.get_all_stats()
        print(f"Queue stats: {stats}")
        
        # Stop worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        
        print("\nMessage queue system demo completed!")
    
    asyncio.run(demo())







