from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_email(data):
    send_mail(subject=data.get("subject"),
            html_message=data.get("body"),
            from_email=data.get("from_email"),
            recipient_list=data.get("to_email"),
            fail_silently=True,
            message=strip_tags(data.get("body")))