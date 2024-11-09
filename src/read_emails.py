import json
import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class ReadEmails:

	def read_email(self):
		"""Shows basic usage of the Gmail API.
		Lists the user's Gmail labels.
		"""
		creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists("token.json"):
			creds = Credentials.from_authorized_user_file("token.json", SCOPES)

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					"credentials.json", SCOPES
				)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open("token.json", "w") as token:
				token.write(creds.to_json())

		try:
			# Call the Gmail API
			service = build("gmail", "v1", credentials=creds)
			results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=10).execute()
			messages = results.get("messages", [])

			email_data = []

			self.json_transfer("data/emails.json", "data/email-database.json")
			self.json_clear("data/emails.json")

			for message in messages:
				msg_id = message["id"]
				msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
				
				# Access specific fields
				snippet = msg.get("snippet")  # Short preview of the email body
				payload = msg.get("payload")  # Contains headers and body information
				parts = payload.get("parts", [])
				
				# Initialize dictionary to store email info
				email_info = {"id": msg_id, "headers": {}, "body": ""}
				
				# Example: Accessing subject and sender
				headers = payload.get("headers", [])
				
				# Extract specific headers (e.g., Subject, From)
				for header in headers:
					if header["name"] in ["Subject", "From", "Date"]:
						email_info["headers"][header["name"]] = header["value"]

				# Function to get the body from the parts
				def get_body(parts):
					for part in parts:
						if part.get("mimeType") == "text/plain":  # Plain text part of the email
							return part["body"].get("data", "")
						elif part.get("mimeType") == "text/html":  # HTML part (if needed)
							return part["body"].get("data", "")
						elif "parts" in part:  # If there are nested parts
							return get_body(part["parts"])
					return ""

				# Decode and clean up the body content
				raw_body = get_body(parts)
				if raw_body:
					decoded_body = base64.urlsafe_b64decode(raw_body.encode("UTF-8")).decode("UTF-8")
					email_info["body"] = self.clean_string(decoded_body)

				# Append structured email info to the list
				email_data.append(email_info)
				
			# Write the collected email data to a JSON file
			with open("data/emails.json", "w") as json_file:
				json.dump(email_data, json_file, indent=4)
		except HttpError as error:
			# TODO(developer) - Handle errors from gmail API.
			print(f"An error occurred: {error}")

	def json_transfer(self, source, destination):
		with open(source, "r") as json_file:
			data = json.load(json_file)
		with open(destination, "w") as json_file:
			json.dump(data, json_file)

	def json_clear(self, source):
		with open(source, "w") as json_file:
			json.dump([], json_file)

	def clean_string(self, text):
		# Remove occurrences of \u, \r, and \n
		cleaned_text = text.replace("\u2019","'").replace("\u201d","'").replace("\\u", "").replace("\r", "").replace("\n", "")
		return cleaned_text

if __name__ == "__main__":
	read_emails = ReadEmails()
	read_emails.read_email()