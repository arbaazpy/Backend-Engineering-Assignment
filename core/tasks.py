from celery import shared_task
from .models import Deployment
from django.db import transaction

@shared_task(bind=True)
def schedule_deployment(self, deployment_id):
    print("'Celery is working!'")
    try:
        # Get deployment object
        deployment = Deployment.objects.get(id=deployment_id)
        cluster = deployment.cluster

        # Check if resources are available
        if (
            cluster.cpu_available >= deployment.cpu_required
            and cluster.ram_available >= deployment.ram_required
            and cluster.gpu_available >= deployment.gpu_required
        ):
            # Start the deployment by updating its status
            deployment.status = Deployment.Status.RUNNING
            cluster.cpu_available -= deployment.cpu_required
            cluster.ram_available -= deployment.ram_required
            cluster.gpu_available -= deployment.gpu_required

            # Save both the deployment and cluster
            with transaction.atomic():
                deployment.save()
                cluster.save()

            return f"Deployment {deployment.id} is now running."

        else:
            # Queue the deployment if resources are not available
            deployment.status = Deployment.Status.PENDING
            deployment.save()

            # Retry scheduling
            return f"Deployment {deployment.id} is pending due to insufficient resources."

    except Deployment.DoesNotExist:
        return f"Deployment {deployment_id} not found."
    except Exception as e:
        return f"Error scheduling deployment {deployment_id}: {str(e)}"
