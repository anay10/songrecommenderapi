from django.core.mail import EmailMessage

class Util:
    @staticmethod #helps to use this class method without instantiating this class instance
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()