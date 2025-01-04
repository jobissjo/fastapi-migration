from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import asyncio
import aiosmtplib
from email.message import EmailMessage
from app.core.config import (EMAIL_HOST_NAME, EMAIL_HOST_USERNAME, EMAIL_HOST_PASSWORD, EMAIL_HOST_PORT)


template_path = Path(__file__).parent.parent / 'templates' / 'email'
environment = Environment(loader=FileSystemLoader(template_path))


async def render_email_template(template_name:str, **kwargs):
    template = environment.get_template(template_name)
    return await asyncio.to_thread(template.render, **kwargs)


async def send_email(recipient:str, subject:str, email_body: str):
    message = EmailMessage()
    
    message['From'] = EMAIL_HOST_USERNAME
    message['To'] = recipient
    message['subject'] = subject
    message.set_content(email_body, subtype='html')

    await aiosmtplib.send(
        message, hostname=EMAIL_HOST_NAME,
        port=EMAIL_HOST_PORT,
        username=EMAIL_HOST_USERNAME,
        password=EMAIL_HOST_PASSWORD,
        start_tls=True,
        ssl_context=aiosmtplib.SSLContext(aiosmtplib.PROTOCOL_SSLv23)  
        # For compatibility with older versions of aiosmtplib
    )