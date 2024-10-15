import os
from time import sleep

from dotenv import load_dotenv

from libs.scraper import Scraper
from libs.data_manager import DataManager

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

    # Initialize libraries
    scraper = Scraper(PAGE_LINK)
    data_manager = DataManager(GOOGLE_SHEET_LINK, credentials_path, SHEET_OUTPUT)
    
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
                
                # Validate new case status
                print("\t\tValidating case status...")
                case_number = data["case_number"]
                old_status = data_manager.get_case_status(case_number)
                new_status = data["status"]
                status_change = False
                
                if old_status and old_status != new_status:
                    status_change = True
                    data["status_change"] = "Yes"
                    
                # Log status change
                if status_change:
                    print("\t\tSaving status change...")
                else:
                    print("\t\tNo status change")
                                
                # Update or insert data
                if old_status:
                    print("\t\tUpdating property...")
                    data_manager.update_property(data)
                else:
                    print("\t\tSaving property...")
                    data_manager.insert_property(data)
            
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
