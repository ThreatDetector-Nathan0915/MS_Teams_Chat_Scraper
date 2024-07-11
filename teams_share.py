import requests
import json
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Constants
TENANT_ID = 'your_tenant_id'
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
TEAMS_CHANNEL_ID = 'your_teams_channel_id'
SHAREPOINT_SITE_ID = 'your_sharepoint_site_id'
SHAREPOINT_FOLDER_ID = 'your_sharepoint_folder_id'

# Authentication
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

# Scrape Teams Chat
def get_teams_chat_history(token):
    url = f"https://graph.microsoft.com/v1.0/teams/{TEAMS_CHANNEL_ID}/channels/{TEAMS_CHANNEL_ID}/messages"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Upload to SharePoint
def upload_to_sharepoint(token, content, filename):
    url = f"https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_SITE_ID}/drive/items/{SHAREPOINT_FOLDER_ID}:/{filename}:/content"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain'
    }
    response = requests.put(url, headers=headers, data=content)
    response.raise_for_status()
    return response.json()

# Main function
def main():
    token = get_access_token()
    chat_history = get_teams_chat_history(token)
    
    # Format the chat history
    formatted_content = json.dumps(chat_history, indent=4)
    
    # Generate a filename with the current date
    filename = f"teams_chat_history_{datetime.now().strftime('%Y-%m-%d')}.txt"
    
    # Upload the formatted content to SharePoint
    upload_to_sharepoint(token, formatted_content, filename)

# Scheduler setup
scheduler = BlockingScheduler()
scheduler.add_job(main, 'cron', day_of_week='mon,wed,fri', hour=10)  # Schedule for Monday, Wednesday, Friday at 10 AM

if __name__ == "__main__":
    scheduler.start()
