import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_enrollment_confirmation(student):
    """Send the enrollment email. Returns True or False and never raises, so a mail
    problem cannot break the request or undo a saved enrollment."""
    context = {"student": student, "course": student.course, "company_name": settings.SENDER_NAME}
    message = EmailMultiAlternatives(
        subject=f"Enrollment confirmed: {student.course.name}",
        body=render_to_string("emails/enrollment_confirmation.txt", context),
        to=[student.email],
    )
    message.attach_alternative(render_to_string("emails/enrollment_confirmation.html", context), "text/html")
    try:
        message.send()
    except Exception:  # SMTP, network and DNS errors are all possible here
        logger.exception("Enrollment email failed for student id=%s", student.pk)
        return False
    logger.info("Enrollment email sent for student id=%s", student.pk)
    return True