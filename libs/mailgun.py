from requests import post, Response
from typing import Union, List
import os

class Mailgun():
    MAIL_DOMAIN = 'mg.housesofyateley.net'
    MAILGUN_API_BASEURL = 'https://api.eu.mailgun.net/v3/{}'.format(MAIL_DOMAIN)
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', None)

    @classmethod
    def send_email(cls,
                   from_email: str,
                   from_title: str,
                   to_email: List[str],
                   subject: str,
                   text: str,
                   html: str) -> Union [Response, None]:
        """
        Send an address confirmation email to the user
        """
        if cls.MAILGUN_API_KEY:
            return post(
                    cls.MAILGUN_API_BASEURL + "/messages",
                    auth=("api", cls.MAILGUN_API_KEY),
                    data={
                        "from": f"{from_title} <{from_email}>",
                        "to": to_email,
                        "subject": subject,
                        "text": text,
                        "html": html
                    })
        else:
            print(f"No Mailgun API key in environment - cannot send confirmation email to {to_email}")
            return None
