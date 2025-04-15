# email_handler.py
import imaplib
import email
import os
from email.header import decode_header
import vzconfig  # Import settings from your config file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ensure the attachments directory exists
if not os.path.isdir(vzconfig.DOWNLOAD_DIR):
    os.makedirs(vzconfig.DOWNLOAD_DIR)
    print(f"Created directory: {vzconfig.DOWNLOAD_DIR}")

class EmailHandler:
    def __init__(self, email_address, password, imap_server):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.connection = None

    def connect(self):
        """Connects to the email server via IMAP."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server)
            self.connection.login(self.email_address, self.password)
            print("Connected to email server successfully.")
        except Exception as e:
            print("Failed to connect or log in:", e)
            self.connection = None

    def fetch_latest_spreadsheet(self):
        """
        Searches the inbox for an unseen email with a spreadsheet attachment.
        Extracts metadata from the subject line (e.g., "Day 4/22").
        Downloads and returns a dictionary with:
          - file_path: the downloaded file path
          - subject_info: extra information parsed from the subject line.
          - sender_email: the email address of the sender.
        """
        if not self.connection:
            print("Not connected to email server.")
            return None

        try:
            self.connection.select("inbox")
            status, messages = self.connection.search(None, 'UNSEEN')
            if status != "OK":
                print("No messages found!")
                return None

            # Process each email until you find one with an attachment.
            email_ids = messages[0].split()
            for email_id in email_ids:
                status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue

                for response in msg_data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        
                        # Extract subject and decode it
                        subject_encoded = msg.get("Subject", "")
                        subject_parts = decode_header(subject_encoded)
                        subject = ""
                        for part, encoding in subject_parts:
                            if isinstance(part, bytes):
                                part = part.decode(encoding if encoding else "utf-8", errors="ignore")
                            subject += part
                        
                        # For our purposes, subject_info is the complete subject.
                        subject_info = subject  
                        
                        # Extract sender email from "From" header.
                        sender = msg.get("From", "")
                        # Using email.utils.parseaddr to extract the email address.
                        from email.utils import parseaddr
                        sender_email = parseaddr(sender)[1]

                        # Look through the parts for an attachment
                        for part in msg.walk():
                            if part.get_content_maintype() == "multipart":
                                continue
                            if part.get("Content-Disposition") is None:
                                continue
                            filename = part.get_filename()
                            if filename:
                                filename_decoded = decode_header(filename)[0][0]
                                if isinstance(filename_decoded, bytes):
                                    filename_decoded = filename_decoded.decode()
                                # Check file type
                                if filename_decoded.endswith(('.xlsx', '.csv')):
                                    file_path = os.path.join(vzconfig.DOWNLOAD_DIR, filename_decoded)
                                    with open(file_path, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    print(f"Attachment saved to {file_path}")
                                    return {"file_path": file_path, "subject_info": subject_info, "sender_email": sender_email}
            print("No spreadsheet attachment found.")
            return None
        except Exception as e:
            print("Error while fetching email:", e)
            return None
        finally:
            self.connection.logout()

    def send_response(self, recipient, subject, body):
        """
        Sends an email using SMTP to the provided recipient with the given subject and body.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_address
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            print(f"Connecting to SMTP server {vzconfig.SMTP_SERVER} on port {vzconfig.SMTP_PORT}...")
            server = smtplib.SMTP_SSL(vzconfig.SMTP_SERVER, vzconfig.SMTP_PORT)
            server.login(self.email_address, self.password)
            server.sendmail(self.email_address, recipient, msg.as_string())
            server.quit()
            print("Response email sent successfully to:", recipient)
        except Exception as e:
            print("Error sending email:", e)
