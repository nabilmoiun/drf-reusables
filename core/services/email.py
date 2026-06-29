import  os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


User = get_user_model()


def send_user_email(
    subject: str,
    to: list[str],
    template_name: str = None,
    context: dict = None,
    plain_message: str = None,
    attachments: list = None,
):
    """
    Send an email using Django's EmailMultiAlternatives.

    Args:
        subject (str): Subject of the email.
        to (list[str]): List of recipient emails.
        template_name (str, optional): Path to HTML template.
        context (dict, optional): Context for rendering the template.
        plain_message (str, optional): Fallback plain text message.
        attachments (list, optional): List of file paths to attach.
    """
    context = context or {}
    from_email = settings.DEFAULT_FROM_EMAIL

    # Render the HTML content (if template is provided)
    html_content = None
    if template_name:
        html_content = render_to_string(template_name, context)

    # Plain text fallback
    text_content = plain_message or "This email requires an HTML-compatible client."

    # Create the email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to,
    )

    # Attach HTML version
    if html_content:
        email.attach_alternative(html_content, "text/html")

    # Attach files
    if attachments:
        for file_path in attachments:
            if os.path.exists(file_path):
                email.attach_file(file_path)

    # Send the email
    email.send(fail_silently=False)
