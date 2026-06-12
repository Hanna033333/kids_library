from supabase_client import supabase

def check_data():
    print("Checking book_library_info table...")
    try:
        response = supabase.table("book_library_info").select("*").execute()
        data = response.data
        print(f"Total rows: {len(data)}")
        if data:
            print("Sample data:")
            for item in data[:5]:
                print(item)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
