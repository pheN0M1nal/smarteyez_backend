from django.conf import settings

class MessageTemplates:
    @staticmethod
    def email_verification_email(token:str):
        return f"""
        <p>get started with smart-eyez
        <br>
        <p><a href={settings.EMAIL_VERIFY_PAGE}?token={token}>Verify my account</p>"""