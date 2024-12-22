from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Organization
import secrets

@receiver(pre_save, sender=Organization)
def generate_invite_code(sender, instance, **kwargs):
    """
    Signal to generate a random invite code for an organization before saving.

    Args:
        sender (Model): The model class (Organization).
        instance (Organization): The specific instance being saved.
        **kwargs: Additional keyword arguments.

    This signal ensures that an invite code is generated only if the field is blank.
    """
    if not instance.invite_code:  # Check if the invite_code field is empty
        # Generate a 10-character random invite code
        instance.invite_code = secrets.token_hex(5)
