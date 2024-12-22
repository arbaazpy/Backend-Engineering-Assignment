from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Organization, Cluster, Deployment
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationAPIViewTest(APITestCase):
    def test_user_registration(self):
        """Test user registration endpoint."""
        url = '/api/v1/auth/register/'
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['message'], 'User created successfully')


class UserLoginAPIViewTest(APITestCase):
    def setUp(self):
        """Set up a test user for login tests."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

    def test_user_login(self):
        """Test user login with valid credentials."""
        url = '/api/v1/auth/login/'
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_user_login(self):
        """Test login with invalid credentials."""
        url = '/api/v1/auth/login/'
        data = {
            'username': 'invaliduser',
            'password': 'invalidpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid credentials')


class UserLogoutAPIViewTest(APITestCase):
    def setUp(self):
        """Set up a test user and generate tokens for authentication."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.logout_url = '/api/v1/auth/logout/'

    def test_user_logout_success(self):
        """Test successful user logout and refresh token blacklisting."""
        response = self.client.post(self.logout_url, {"refresh": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['detail'], 'Successfully logged out.')

        # Ensure the token is blacklisted
        response = self.client.post('/api/token/refresh/', {"refresh": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Token is blacklisted", response.data.get('detail', ''))

    def test_logout_without_refresh_token(self):
        """Test logout attempt without providing a refresh token."""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Refresh token is required.')

    def test_logout_with_invalid_refresh_token(self):
        """Test logout attempt with an invalid refresh token."""
        invalid_refresh = "invalid_token"
        response = self.client.post(self.logout_url, {"refresh": invalid_refresh})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token is invalid or expired", response.data['detail'])


class OrganizationViewSetTest(APITestCase):
    def setUp(self):
        """Set up a test user and organization for testing."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            invite_code='ABC123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_organization(self):
        """Test creation of an organization."""
        url = '/api/v1/organizations/'
        data = {
            "name": "New Organization",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_join_organization(self):
        """Test joining an organization with a valid invite code."""
        url = f'/api/v1/organizations/{self.organization.id}/join/'
        data = {
            "invite_code": "ABC123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Successfully joined the organization.")

    def test_invalid_invite_code(self):
        """Test joining with an invalid invite code."""
        url = f'/api/v1/organizations/{self.organization.id}/join/'
        data = {
            "invite_code": "INVALIDCODE"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid invite code.")


class ClusterViewSetTest(APITestCase):
    def setUp(self):
        """Set up a test user and cluster for testing."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            invite_code='ABC123'
        )
        self.cluster = Cluster.objects.create(
            name='Test Cluster',
            organization=self.organization,
            cpu_limit=10.0,
            ram_limit=32.0,
            gpu_limit=2.0,
            cpu_available=10.0,
            ram_available=32.0,
            gpu_available=2.0
        )
        self.client.force_authenticate(user=self.user)

    def test_create_cluster(self):
        """Test creating a new cluster."""
        url = '/api/v1/clusters/'
        data = {
            "name": "New Cluster",
            "organization": self.organization.id,
            "cpu_limit": 20.0,
            "ram_limit": 64.0,
            "gpu_limit": 4.0,
            "cpu_available": 20.0,
            "ram_available": 64.0,
            "gpu_available": 4.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class DeploymentViewSetTest(APITestCase):
    def setUp(self):
        """Set up a test user, cluster, and deployment for testing."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.organization = Organization.objects.create(
            name='Test Organization',
            invite_code='ABC123'
        )
        self.cluster = Cluster.objects.create(
            name='Test Cluster',
            organization=self.organization,
            cpu_limit=10.0,
            ram_limit=32.0,
            gpu_limit=2.0,
            cpu_available=10.0,
            ram_available=32.0,
            gpu_available=2.0
        )
        self.client.force_authenticate(user=self.user)

    def test_create_deployment(self):
        """Test creating a deployment."""
        url = '/api/v1/deployments/'
        data = {
            "name": "Test Deployment",
            "cluster": self.cluster.id,
            "docker_image": "testimage:v1",
            "status": "pending",
            "priority": 1,
            "cpu_required": 2.0,
            "ram_required": 4.0,
            "gpu_required": 1.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_deployment_invalid(self):
        """Test creating a deployment with invalid data."""
        url = '/api/v1/deployments/'
        data = {
            "name": "Test Deployment",
            "cluster": self.cluster.id,
            "docker_image": "testimage:v1",
            "status": "invalid_status",  # Invalid status
            "priority": 1,
            "cpu_required": 2.0,
            "ram_required": 4.0,
            "gpu_required": 1.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
