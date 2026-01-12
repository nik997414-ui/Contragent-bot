import os
from dadata import Dadata
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DADATA_API_KEY")
SECRET_KEY = os.getenv("DADATA_SECRET_KEY")

print(f"Testing with API KEY: {API_KEY[:5]}***")

try:
    dadata = Dadata(API_KEY, SECRET_KEY) if SECRET_KEY else Dadata(API_KEY)
    # Test with Sberbank INN
    result = dadata.find_by_id("party", "7707083893")
    
    if result:
        print("SUCCESS! Found company:")
        print(result[0]['value'])
        print("Status:", result[0]['data']['state']['status'])
    else:
        print("FAILED: No result found (but no error).")

except Exception as e:
    print(f"ERROR: {e}")
