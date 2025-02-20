import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
from nicegui import ui

# Global variables
scraped_data = []
email_receiver = ""
scraping_url = ""
is_scraping_scheduled = False

# Function to scrape data
def scrape_website():
    global scraped_data
    try:
        response = requests.get(scraping_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Scrape all headings (h1, h2, h3) from the page
        headings = []
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            headings.append(tag.text.strip())

        # Save scraped data
        scraped_data = headings
        ui.notify(f"Scraped {len(headings)} items from {scraping_url}", type="positive")
    except Exception as e:
        ui.notify(f"Error during scraping: {e}", type="negative")

# Function to save data to CSV
def save_to_csv():
    if not scraped_data:
        ui.notify("No data to save. Please scrape first.", type="warning")
        return

    df = pd.DataFrame(scraped_data, columns=["Headings"])
    df.to_csv("scraped_data.csv", index=False)
    ui.notify("Data saved to scraped_data.csv", type="positive")

# Function to send email
def send_email():
    if not scraped_data:
        ui.notify("No data to send. Please scrape first.", type="warning")
        return

    if not email_receiver:
        ui.notify("Please enter an email address.", type="warning")
        return

    # Email configuration
    sender_email = "your_email@example.com"  # Replace with your email
    sender_password = "your_password"  # Replace with your email password
    subject = "Scraped Data Report"

    # Create email content
    body = "\n".join(scraped_data)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Use your email provider's SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_receiver, msg.as_string())
        ui.notify(f"Email sent to {email_receiver}", type="positive")
    except Exception as e:
        ui.notify(f"Error sending email: {e}", type="negative")

# Function to schedule scraping
def schedule_scraping():
    global is_scraping_scheduled
    if is_scraping_scheduled:
        schedule.clear()
        is_scraping_scheduled = False
        ui.notify("Scraping schedule stopped.", type="info")
    else:
        interval = int(interval_input.value)
        schedule.every(interval).minutes.do(scrape_website)
        is_scraping_scheduled = True
        ui.notify(f"Scraping scheduled every {interval} minutes.", type="positive")

# NiceGUI Interface
with ui.column().classes("w-full max-w-2xl mx-auto p-4"):
    ui.label("Web Scraping Automation Tool").classes("text-2xl font-bold text-center mb-4")

    # Input for URL
    ui.label("Enter the URL to scrape:").classes("text-lg")
    url_input = ui.input("URL", value="https://example.com").classes("w-full mb-4")

    # Input for email
    ui.label("Enter your email to receive scraped data:").classes("text-lg")
    email_input = ui.input("Email", value="").classes("w-full mb-4")

    # Input for scheduling interval
    ui.label("Schedule scraping every (minutes):").classes("text-lg")
    interval_input = ui.number(value=60, min=1).classes("w-full mb-4")

    # Buttons
    with ui.row().classes("w-full justify-center gap-4"):
        ui.button("Scrape Now", on_click=lambda: scrape_website()).classes("bg-blue-500 text-white")
        ui.button("Save to CSV", on_click=lambda: save_to_csv()).classes("bg-green-500 text-white")
        ui.button("Send Email", on_click=lambda: send_email()).classes("bg-purple-500 text-white")
        ui.button("Schedule Scraping", on_click=lambda: schedule_scraping()).classes("bg-orange-500 text-white")

# Function to run the scheduler in the background
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
import threading
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Run NiceGUI app
ui.run(title="Web Scraping Automation", port=8080)