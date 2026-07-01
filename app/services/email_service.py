from dotenv import load_dotenv
import os
import resend

load_dotenv()

print(os.getenv("RESEND_API_KEY"))

resend.api_key = os.getenv("RESEND_API_KEY")


def enviar_email(destinatario, asunto, html):
    resend.Emails.send(
        {
            "from": "turnos@farixio.com",
            "to": [destinatario],
            "subject": asunto,
            "html": html,
        }
    )