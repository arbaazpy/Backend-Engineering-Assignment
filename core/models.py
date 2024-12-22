from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser model. 
    Adds unique email field and includes Many-to-Many relationships for groups and user permissions.
    
    Attributes:
        email: Unique email address for each user.
        groups: Many-to-many relationship with the Group model, representing the groups the user belongs to.
        user_permissions: Many-to-many relationship with the Permission model, representing the specific permissions for the user.
    """
    groups = models.ManyToManyField(
        Group,
        related_name="user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    email = models.EmailField(unique=True)


class Organization(models.Model):
    """
    Represents an Organization in the system. An organization can have multiple users and clusters. 
    The organization is associated with a unique invite code that can be used by users to join the organization.

    Attributes:
        name: The name of the organization.
        invite_code: A unique code used for inviting users to join the organization.
        users: Many-to-many relationship with the User model, representing the users belonging to the organization.
    """
    name = models.CharField(max_length=255)
    invite_code = models.CharField(max_length=10, unique=True, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Cluster(models.Model):
    """
    Represents a Cluster within an Organization. A cluster holds resources (CPU, RAM, GPU) 
    that are available for deployments. Each cluster belongs to an organization and has 
    defined resource limits and available resources.

    Attributes:
        name: The name of the cluster.
        organization: ForeignKey relationship with the Organization model, representing the organization the cluster belongs to.
        cpu_limit: The maximum CPU capacity of the cluster.
        ram_limit: The maximum RAM capacity of the cluster.
        gpu_limit: The maximum GPU capacity of the cluster.
        cpu_available: The current available CPU resources for deployments.
        ram_available: The current available RAM resources for deployments.
        gpu_available: The current available GPU resources for deployments.
    """
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, related_name="clusters", on_delete=models.CASCADE)

    # Resource limits
    cpu_limit = models.FloatField()
    ram_limit = models.FloatField()
    gpu_limit = models.FloatField()

    # Available resources
    cpu_available = models.FloatField()
    ram_available = models.FloatField()
    gpu_available = models.FloatField()

    def __str__(self):
        return self.name


class Deployment(models.Model):
    """
    Represents a Deployment within a cluster. A deployment involves allocating resources (CPU, RAM, GPU) 
    from the cluster to run a service or application. Each deployment has a status, priority, and resource requirements.

    Attributes:
        name: The name of the deployment.
        cluster: ForeignKey relationship with the Cluster model, representing the cluster the deployment is associated with.
        docker_image: The Docker image used for the deployment.
        status: The current status of the deployment (e.g., pending, running, failed, completed).
        priority: The priority level of the deployment.
        cpu_required: The amount of CPU required for the deployment.
        ram_required: The amount of RAM required for the deployment.
        gpu_required: The number of GPUs required for the deployment.
    """
    class Status(models.TextChoices):
        """
        Choices for the status of a deployment. The deployment can be in one of the following states:
        - PENDING: The deployment is waiting for resources to be allocated.
        - RUNNING: The deployment is currently running.
        - FAILED: The deployment failed to execute.
        - COMPLETED: The deployment has finished successfully.
        """
        PENDING = "pending"
        RUNNING = "running"
        FAILED = "failed"
        COMPLETED = "completed"

    name = models.CharField(max_length=255)
    cluster = models.ForeignKey(Cluster, related_name="deployments", on_delete=models.CASCADE)
    docker_image = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    priority = models.IntegerField(default=0)

    # Resource requirements
    cpu_required = models.FloatField()
    ram_required = models.FloatField()
    gpu_required = models.FloatField()

    dependencies = models.ManyToManyField('self', blank=True)

    def are_dependencies_completed(self):
        """
        Check if all dependencies are completed.
        """
        return all(dep.status == 'COMPLETED' for dep in self.dependencies.all())

    def __str__(self):
        return self.name
