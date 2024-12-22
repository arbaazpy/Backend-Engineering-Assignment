from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a superuser programmatically"

    def add_arguments(self, parser):
        # Adding arguments to specify superuser details
        parser.add_argument('--username', type=str, help='Superuser username', required=True)
        parser.add_argument('--email', type=str, help='Superuser email', required=True)
        parser.add_argument('--password', type=str, help='Superuser password', required=True)

    def handle(self, *args, **options):
        User = get_user_model()

        username = options['username']
        email = options['email']
        password = options['password']

        try:
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User with username '{username}' already exists."))
                return

            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User with email '{email}' already exists."))
                return

            # Create the superuser
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error creating superuser: {str(e)}"))
