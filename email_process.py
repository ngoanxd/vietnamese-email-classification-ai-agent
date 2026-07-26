from config import *
import imaplib
import email
from email.utils import parseaddr
from email.header import decode_header
from bs4 import BeautifulSoup
import re

def get_unseen_email_ids():

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)

    mail.select("inbox")

    _, data = mail.search(None, "UNSEEN")

    email_ids = data[0].split()

    mail.logout()

    return email_ids



def clean_text(text):

    if not isinstance(text, str):
        return text

    # Xóa URL
    text = re.sub(
        r'https?://\S+',
        ' ',
        text
    )

    # Xóa tag HTML
    text = re.sub(
        r'<[^>]+>',
        ' ',
        text
    )

    # Chuẩn hóa khoảng trắng
    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


def load_email(email_id):

    mail = imaplib.IMAP4_SSL(
        "imap.gmail.com"
    )

    mail.login(
        GMAIL_USER,
        GMAIL_APP_PASSWORD
    )

    mail.select("inbox")

    _, msg_data = mail.fetch(
        email_id,
        "(BODY.PEEK[])"
    )

    raw_email = msg_data[0][1]

    msg = email.message_from_bytes(
        raw_email
    )

    # =====================
    # Decode sender
    # =====================

    sender_name, sender_email = parseaddr(
        msg["From"]
    )

    decoded_name = ""

    for text, encoding in decode_header(
        sender_name
    ):

        if isinstance(text, bytes):

            decoded_name += text.decode(
                encoding or "utf-8",
                errors="ignore"
            )

        else:

            decoded_name += text

    # =====================
    # Decode subject
    # =====================

    subject = msg["Subject"]

    decoded_subject = ""

    for text, encoding in decode_header(
        subject
    ):

        if isinstance(text, bytes):

            decoded_subject += text.decode(
                encoding or "utf-8",
                errors="ignore"
            )

        else:

            decoded_subject += text

    # =====================
    # Extract body
    # =====================

    text_body = ""
    html_body = ""

    if msg.is_multipart():

        for part in msg.walk():

            if "attachment" in str(
                part.get(
                    "Content-Disposition",
                    ""
                )
            ).lower():

                continue

            content_type = (
                part.get_content_type()
            )

            payload = part.get_payload(
                decode=True
            )

            if not payload:
                continue

            charset = (
                part.get_content_charset()
                or "utf-8"
            )

            try:

                content = payload.decode(
                    charset,
                    errors="ignore"
                )

            except:

                content = payload.decode(
                    "utf-8",
                    errors="ignore"
                )

            if content_type == "text/plain":

                text_body = content

            elif content_type == "text/html":

                html_body = content

    else:

        payload = msg.get_payload(
            decode=True
        )

        if payload:

            body = payload.decode(
                errors="ignore"
            )

            if (
                msg.get_content_type()
                == "text/plain"
            ):

                text_body = body

            elif (
                msg.get_content_type()
                == "text/html"
            ):

                html_body = body

    # =====================
    # Ưu tiên text/plain
    # =====================

    if text_body:

        body = text_body

    elif html_body:

        body = BeautifulSoup(
            html_body,
            "html.parser"
        ).get_text(" ")

    else:

        body = ""

    # =====================
    # Clean body
    # =====================

    body = clean_text(body)

    mail.logout()

    return {

        "email_id": email_id,

        "name": decoded_name,

        "dc": sender_email,

        "tieude": decoded_subject,

        "nd": body

    }
