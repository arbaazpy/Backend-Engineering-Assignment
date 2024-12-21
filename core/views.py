from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, Organization, Cluster, Deployment
from .serializers import (
    OrganizationSerializer,
    ClusterSerializer,
    DeploymentSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    InviteCodeSerializer,
    ValidateRefreshTokenSerializer
)
from drf_spectacular.utils import extend_schema
from .tasks import schedule_deployment


# User Registration API
class UserRegistrationAPIView(APIView):
    """
    API endpoint for registering a new user. The user is created by providing 
    a username, email, and password. The password is hashed before being stored.

    Permission: AllowAny (accessible by anyone)

    Methods:
        post: Creates a new user with the provided registration data.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(request=UserRegistrationSerializer)
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to register a new user.

        Validates and saves the user data, then returns a success message along with 
        the user's data on successful creation.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User created successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Login API (JWT Authentication)
class UserLoginAPIView(APIView):
    """
    API endpoint for user login using JWT authentication. The user is authenticated 
    using their username and password, and if successful, JWT tokens are returned.

    Permission: AllowAny (accessible by anyone)

    Methods:
        post: Authenticates the user and returns access and refresh JWT tokens.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to login a user by validating the credentials
        and returning JWT tokens.

        Returns an access token and a refresh token on successful authentication.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = serializer.get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    """
    API endpoint for logging out the user by invalidating their refresh token.
    Ensures the token is blacklisted to prevent further use.

    Permission: IsAuthenticated (requires user to be authenticated)

    Methods:
        post: Logs out the user by invalidating their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ValidateRefreshTokenSerializer)
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to log the user out by invalidating their refresh token.

        Blacklists the refresh token and prevents further usage.
        """
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Decode and blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing organizations. This viewset allows creating, updating, 
    deleting, and retrieving organizations. It also includes an action for users to 
    join an organization using an invite code.

    Methods:
        join: Allows a user to join the organization by providing a valid invite code.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @extend_schema(request=InviteCodeSerializer)
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Allows a user to join an organization using an invite code.
        Validates the invite code and adds the user to the organization if valid.
        """
        organization = self.get_object()
        invite_code = request.data.get('invite_code')

        # Validate the invite code
        if invite_code != organization.invite_code:
            return Response({"error": "Invalid invite code."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is already part of the organization
        if request.user in organization.users.all():
            return Response({"error": "You are already part of this organization."}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the organization
        organization.users.add(request.user)

        return Response({"message": "Successfully joined the organization."}, status=status.HTTP_200_OK)


class ClusterViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing clusters. This viewset allows creating, updating, 
    deleting, and retrieving clusters associated with an organization.

    Methods:
        None
    """
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DeploymentViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing deployments. This viewset allows creating, updating, 
    deleting, and retrieving deployments in clusters. It also handles scheduling 
    deployments in the background.

    Methods:
        create: Creates a deployment and schedules it asynchronously in the background.
    """
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a deployment and schedules it for execution in 
        the background.

        This method enqueues the deployment task to be processed asynchronously 
        while immediately returning the response to the client.
        """
        try:
            # Deserialize request data
            serializer = DeploymentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            deployment = serializer.save()

            # Enqueue the deployment task to be scheduled in the background
            schedule_deployment.delay(deployment.id)

            # Return the response immediately, as the task is being processed asynchronously
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
