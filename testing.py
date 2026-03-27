import os
import requests
import time
from dotenv import load_dotenv, find_dotenv

# 1. Force Python to find the exact path of the .env file
env_path = find_dotenv()
print(f"Looking for .env file... Found at: {env_path}")

# 2. Force it to load and OVERRIDE any existing ghost variables
is_loaded = load_dotenv(env_path, override=True)
print(f"Did it successfully load the file? {is_loaded}")

# --- SETUP: Pulling from Environment Variables ---
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

print(f"Notion Key captured: {bool(NOTION_API_KEY)}")
print(f"Database ID captured: {bool(DATABASE_ID)}\n")

# Safety check
if not NOTION_API_KEY or not DATABASE_ID:
    print("Error: Still Missing Environment Variables!")
    exit(1)

# --- SETUP: Pulling from Environment Variables ---
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

# Safety check to make sure the variables are actually loaded
if not NOTION_API_KEY or not DATABASE_ID:
    print("Error: Missing Environment Variables!")
    print("Please ensure both NOTION_API_KEY and DATABASE_ID are exported in your terminal session.")
    exit(1)

# --- FAKE DATA ---
fake_payments = [
    {"merchant": "Starbucks", "amount": 6.50, "category": "Food & Drink"},
    {"merchant": "Netflix", "amount": 15.99, "category": "Subscriptions"},
    {"merchant": "Shell Station", "amount": 45.00, "category": "Transport"}
]

def add_to_notion(merchant, amount, category):
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    notion_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Amount": {"number": amount},
            "Merchant": {"title": [{"text": {"content": merchant}}]},
            "Category": {"select": {"name": category}}
        }
    }
    
    response = requests.post(url, headers=headers, json=notion_data)
    
    if response.status_code == 200:
        print(f"Successfully added: {merchant} for ${amount}")
    else:
        print(f"Failed to add {merchant}.")
        print(f"Error Message: {response.text}")

# --- RUN THE TEST ---
print("Sending fake data to Notion using Environment Variables...\n")
for payment in fake_payments:
    add_to_notion(payment["merchant"], payment["amount"], payment["category"])
    # Small pause to avoid hitting Notion's rate limit
    time.sleep(0.5) 

print("\nDone! Check your Notion database.")