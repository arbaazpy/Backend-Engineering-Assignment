from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Organization, Cluster, Deployment


# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. It validates and creates a new user, 
    hashes the password before saving, and returns the user object.
    
    Fields:
        username: The username of the user.
        email: The email address of the user.
        password: The password of the user (write-only).
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        """
        Create and return a new user instance, setting the password hash.
        """
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


# Login Serializer for JWT Authentication
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. It validates the provided credentials and 
    returns JWT tokens if authentication is successful.
    
    Fields:
        username: The username of the user.
        password: The password of the user.
    
    Methods:
        validate: Validates the credentials by authenticating the user.
        get_tokens_for_user: Generates JWT tokens (access and refresh).
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Authenticate the user based on provided credentials.
        """
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user

    def get_tokens_for_user(self, user):
        """
        Generate access and refresh tokens for the authenticated user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing user data, used for reading user details.
    
    Fields:
        id: The unique ID of the user.
        username: The username of the user.
        email: The email address of the user.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email',]


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing organization data, including its users.
    
    Fields:
        id: The unique ID of the organization.
        name: The name of the organization.
        invite_code: The invite code for the organization.
        users: List of users associated with the organization.
    """
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'invite_code', 'users']


class ClusterSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing cluster data, including its resource limits 
    and available resources.
    
    Fields:
        id: The unique ID of the cluster.
        name: The name of the cluster.
        organization: The organization the cluster belongs to.
        cpu_limit: The maximum CPU resources of the cluster.
        ram_limit: The maximum RAM resources of the cluster.
        gpu_limit: The maximum GPU resources of the cluster.
        cpu_available: The available CPU resources in the cluster.
        ram_available: The available RAM resources in the cluster.
        gpu_available: The available GPU resources in the cluster.
    """
    class Meta:
        model = Cluster
        fields = ['id', 'name', 'organization', 'cpu_limit', 'ram_limit', 'gpu_limit', 'cpu_available', 'ram_available', 'gpu_available']


class DeploymentSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing deployment data, including the resources 
    required for the deployment and the current status.
    
    Fields:
        id: The unique ID of the deployment.
        name: The name of the deployment.
        cluster: The cluster the deployment belongs to.
        docker_image: The Docker image used for the deployment.
        status: The current status of the deployment.
        priority: The priority of the deployment.
        cpu_required: The amount of CPU resources required by the deployment.
        ram_required: The amount of RAM resources required by the deployment.
        gpu_required: The number of GPU resources required by the deployment.
    """
    class Meta:
        model = Deployment
        fields = ['id', 'name', 'cluster', 'docker_image', 'status', 'priority', 'cpu_required', 'ram_required', 'gpu_required']


class InviteCodeSerializer(serializers.Serializer):
    """
    Serializer for validating the invite code during organization invitation.
    
    Fields:
        invite_code: The invite code used to join an organization.
    """
    invite_code = serializers.CharField()


class ValidateRefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for validating the access token for logout view.
    
    Fields:
        access: access token obtained after logging in.
    """
    refresh = serializers.CharField()
