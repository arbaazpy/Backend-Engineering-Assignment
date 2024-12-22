from celery import shared_task
from .models import Deployment
from django.db import transaction
from celery.exceptions import Retry

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def schedule_deployment(self, deployment_id):
    """
    Schedule a deployment within a cluster.

    This task ensures that the required resources (CPU, RAM, GPU) for a deployment
    are available in the associated cluster. If sufficient resources are available,
    the deployment status is updated to 'RUNNING', and the resources are allocated.

    If resources are insufficient, the deployment is marked as 'PENDING', and the task
    retries after a delay to reattempt scheduling. The task will retry up to a maximum
    of three times before failing.

    Args:
        self: Reference to the current task instance (used for retries).
        deployment_id (int): The ID of the deployment to be scheduled.

    Returns:
        str: A message indicating the result of the scheduling attempt.

    Raises:
        Deployment.DoesNotExist: If the deployment with the specified ID does not exist.
        Exception: For any other errors encountered during scheduling.
    """
    try:
        # Fetch the deployment and related cluster
        deployment = Deployment.objects.get(id=deployment_id)
        cluster = deployment.cluster

        # Check resource availability in the cluster
        if (
            cluster.cpu_available >= deployment.cpu_required
            and cluster.ram_available >= deployment.ram_required
            and cluster.gpu_available >= deployment.gpu_required
        ):
            # Allocate resources and update deployment status to 'RUNNING'
            deployment.status = Deployment.Status.RUNNING
            cluster.cpu_available -= deployment.cpu_required
            cluster.ram_available -= deployment.ram_required
            cluster.gpu_available -= deployment.gpu_required

            with transaction.atomic():
                deployment.save()
                cluster.save()

            return f"Deployment {deployment.id} is now running."
        else:
            # Update status to 'PENDING' and retry after a delay
            deployment.status = Deployment.Status.PENDING
            deployment.save()

            self.retry(exc=Retry("Insufficient resources, retrying..."))

    except Deployment.DoesNotExist:
        error_message = f"Deployment {deployment_id} not found."
        return error_message

    except Retry as e:
        # Log retry-specific messages (if required by a logging mechanism)
        return str(e)

    except Exception as e:
        # Handle unexpected errors gracefully and provide meaningful output
        error_message = f"Error scheduling deployment {deployment_id}: {str(e)}"
        return error_message
