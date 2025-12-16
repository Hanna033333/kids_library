import os
try:
    from dotenv import load_dotenv
    print("Imported dotenv")
    load_dotenv()
    print("Loaded dotenv")
except Exception as e:
    print(f"Dotenv error: {e}")

try:
    from core.database import supabase
    print("Imported supabase")
except Exception as e:
    print(f"Supabase error: {e}")

print("Debug script finished")
