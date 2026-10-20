from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import send_enrollment_confirmation
from .models import Student


@receiver(post_save, sender=Student)
def email_new_student(sender, instance, created, raw=False, **kwargs):
    """Send the email when a student is first enrolled, but only after the save is committed."""
    if created and not raw:
        transaction.on_commit(lambda: send_enrollment_confirmation(instance))