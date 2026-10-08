from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_verification_email(user, code):
    subject = "Verify Your Vendor Account"
    to      = [user.email]
    from_   = settings.DEFAULT_FROM_EMAIL

    text_body = render_to_string("emails/verify_email.txt", {"user": user, "code": code})
    html_body = render_to_string("emails/verify_email.html", {"user": user, "code": code})

    msg = EmailMultiAlternatives(subject, text_body, from_, to)
    msg.attach_alternative(html_body, "text/html")
    msg.send()
