"""Gmail API client for reading emails."""

import os
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_gmail_service():
    """Create and return Gmail API service using environment credentials."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        missing = []
        if not client_id:
            missing.append("GOOGLE_CLIENT_ID")
        if not client_secret:
            missing.append("GOOGLE_CLIENT_SECRET")
        if not refresh_token:
            missing.append("GOOGLE_REFRESH_TOKEN")
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"]
    )

    return build("gmail", "v1", credentials=credentials)


def _extract_body(payload: Dict[str, Any]) -> str:
    """Extract email body from message payload."""
    body = ""

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                if "data" in part["body"]:
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break
            elif part["mimeType"] == "text/html" and not body:
                if "data" in part["body"]:
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
    elif "body" in payload and "data" in payload["body"]:
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    return body


def get_unread_emails(hours: int = 24) -> List[Dict[str, Any]]:
    """
    Fetch unread emails from the past N hours.

    Args:
        hours: Number of hours to look back (default: 24)

    Returns:
        List of email dictionaries with id, subject, body, snippet, and date
    """
    service = get_gmail_service()

    # Calculate timestamp for filtering
    cutoff_time = datetime.now() - timedelta(hours=hours)
    after_timestamp = int(cutoff_time.timestamp())

    # Build query
    query = f"is:unread after:{after_timestamp}"

    try:
        # Get list of message IDs
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=100
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for message in messages:
            msg = service.users().messages().get(
                userId="me",
                id=message["id"],
                format="full"
            ).execute()

            headers = msg["payload"]["headers"]
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "(No Subject)"
            )
            date = next(
                (h["value"] for h in headers if h["name"].lower() == "date"),
                ""
            )

            body = _extract_body(msg["payload"])

            emails.append({
                "id": msg["id"],
                "subject": subject,
                "snippet": msg.get("snippet", ""),
                "body": body,
                "date": date
            })

        return emails

    except HttpError as error:
        raise Exception(f"Gmail API error: {error}")
