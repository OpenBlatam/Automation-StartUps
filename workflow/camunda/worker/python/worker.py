import os
import time
from camunda_external_task_client_python3.external_task import ExternalTask, TaskResult
from camunda_external_task_client_python3.external_task_client import ExternalTaskClient


def handle_task(task: ExternalTask) -> TaskResult:
	order_id = task.get_variable("orderId")
	print(f"processing order {order_id}")
	return task.complete({"processed": True})

if __name__ == "__main__":
	base_url = os.getenv("CAMUNDA_REST_URL", "http://operate.workflows.svc.cluster.local:8080")
	client = ExternalTaskClient(base_url=base_url)
	client.subscribe("process-order", handle_task)
	while True:
		time.sleep(1)


