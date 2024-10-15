import os
from time import sleep

from dotenv import load_dotenv

from scraper import Scraper
from libs.google_sheets import SheetsManager

# Env variables
load_dotenv()
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
PAGE_LINK = os.getenv("PAGE_LINK")
SHEET_OUTPUT = os.getenv("SHEET_OUTPUT")
WAIT_SECONDS = int(os.getenv("WAIT_SECONDS"))


def main():
    # Main workflow: scrape each property found
    # and save data in google sheets

    # Header
    print("\n----------------------------------")
    print("Taxsales Lgbs Bot")
    print("----------------------------------\n")
    
    # Paths
    current_path = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(current_path, "credentials.json")

    # SCraping counters
    current_property = 1
    current_page = 1

    # Initialize the scraper and google sheets manager
    scraper = Scraper(PAGE_LINK)
    google_sheet = SheetsManager(GOOGLE_SHEET_LINK, credentials_path, SHEET_OUTPUT)
    
    # get last row
    last_row = google_sheet.get_rows_num()
    
    while True:
        
        print(f"Scraping page {current_page}...")
        
        # Extract the properties from current results page
        for property_index in range(2, 12):
            
            # Open property details
            property_found = scraper.open_property_details(property_index)
            if not property_found:
                break
            print(f"\tScraping property {current_property}...")
            
            # Extract property data
            data = scraper.get_property_data()
            if data:
                # Format and save data in google sheets
                print(f"\t\tSaving property {current_property}...")
                current_row = last_row + current_property
                data_row = data.values()
                google_sheet.write_data([data_row], current_row)
            
            # Close property details and wait
            scraper.close_property_details()
            sleep(WAIT_SECONDS)
            current_property += 1
            
        # Go to next results page
        has_next = scraper.go_next_page()
        if not has_next:
            print("No more results. Done.")
            break
        current_page += 1

    print("\n----------------------------------")
    

if __name__ == "__main__":
    main()
