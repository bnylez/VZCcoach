# main.py

from email_handler import EmailHandler
from spreadsheet_reader import SpreadsheetReader
from calculator import QuotaCalculator
from response_builder import ResponseBuilder
import vzconfig  # assuming your config is imported as vzconfig
import datetime
import time

def main():
    print("=== Starting Daily Commission Coach Bot ===")
    
    # Step 1: Connect to email & fetch attachment
    print("Connecting to email account...")
    email_handler = EmailHandler(vzconfig.EMAIL_ACCOUNT, vzconfig.APP_PASSWORD, vzconfig.IMAP_SERVER)
    email_handler.connect()
    
    print("Searching for new email with a spreadsheet attachment...")
    email_data = email_handler.fetch_latest_spreadsheet()
    if not email_data:
        print("No new email attachment found. Exiting cycle.")
        return

    file_path = email_data.get("file_path")
    subject_info = email_data.get("subject_info")
    sender_email = email_data.get("sender_email")
    print(f"Email received from: {sender_email}")
    print(f"Attachment downloaded to: {file_path}")
    print(f"Subject info extracted: {subject_info}")

    # Step 2: Load spreadsheet into DataFrame
    print("Loading spreadsheet into DataFrame...")
    reader = SpreadsheetReader(file_path, subject_info)
    df = reader.load_dataframe()
    if df is None:
        print("Error loading spreadsheet into DataFrame. Exiting cycle.")
        return

    print("Spreadsheet loaded successfully. DataFrame preview:")
    print(df.head())

    # Step 3: Calculate performance metrics using QuotaCalculator
    print("Calculating performance metrics...")
    quota_calculator = QuotaCalculator(df)
    calc_results = quota_calculator.calculate_all()
    print("Calculated Metrics:")
    print(calc_results)

    # Step 4: Build the response email using ResponseBuilder
    print("Building the response email content...")
    builder = ResponseBuilder(calc_results)
    subject, body = builder.build_response()
    print("Response built successfully.")
    print("Generated Email Subject:", subject)
    print("Email Body Preview:")
    print(body[:300] + "\n...")  # Only showing the first 300 characters

    # Step 5: Send the response email back to the sender
    print(f"Sending response email to: {sender_email} ...")
    email_handler.send_response(sender_email, subject, body)
    print("Response email sent successfully.")

    print("=== Bot cycle complete. ===")


if __name__ == "__main__":
    # Run the bot periodically for 2 hour.
    run_duration = datetime.timedelta(hours=2)
    end_time = datetime.datetime.now() + run_duration
    interval_seconds = 60  # Check every 5 minutes (300 seconds)

    print("=== Starting periodic email checking for 1 hour ===")
    while datetime.datetime.now() < end_time:
        print("\n=== Starting a new bot cycle at", datetime.datetime.now(), "===")
        main()  # Run your main routine which checks the inbox, processes attachment, sends response, etc.
        print("Cycle complete. Sleeping for", interval_seconds, "seconds...")
        time.sleep(interval_seconds)

    print("=== One hour elapsed; bot exiting. ===")
