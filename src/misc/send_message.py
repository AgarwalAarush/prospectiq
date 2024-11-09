import base64
from email.message import EmailMessage

import google.oauth2.service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def gmail_send_message(credentials_file):
  """Create and send an email message using credentials from a file
  Print the returned message id
  Returns: Message object, including message id
  """

  try:
    # Load credentials from the specified file
    creds = google.oauth2.service_account.Credentials.from_service_account_file(credentials_file)

    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content("This is automated draft mail")

    message["To"] = "ssoundap@andrew.cmu.edu"
    message["From"] = "aarusha@andrew.cmu.edu"
    message["Subject"] = "Hello"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message


if __name__ == "__main__":
  # Replace with the path to your credentials file
  credentials_file = 'docs/novahacksproject-dc5e2e740f31.json'
  gmail_send_message(credentials_file)