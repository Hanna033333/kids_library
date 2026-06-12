import asyncio
import aiohttp
import os
import sys

# Add parent dir to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from core.config import DATA4LIBRARY_KEY
from services.loan_status import fetch_loan_status_single

async def test_api():
    print(f"Key loaded: {DATA4LIBRARY_KEY[:10]}..." if DATA4LIBRARY_KEY else "Key NOT loaded")
    
    if not DATA4LIBRARY_KEY:
        print("Error: DATA4LIBRARY_KEY is missing")
        return

    isbn = "9788936434120" # The Vegetarian (known book)
    print(f"Testing ISBN: {isbn}")
    
    async with aiohttp.ClientSession() as session:
        result = await fetch_loan_status_single(session, isbn)
        print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test_api())
