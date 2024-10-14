import os
from time import sleep

from dotenv import load_dotenv

from scraper import Scraper

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

    # Initialize the scraper
    scraper = Scraper(PAGE_LINK)
    
    while True:
        
        # Extract the properties from current results page
        for property_index in range(2, 11):
            property_found = scraper.open_property_details(property_index)
            if not property_found:
                break
            data = scraper.get_property_data()
            print(data)
            # scraper.save_data(data, SHEET_OUTPUT)
            scraper.close_property_details()
    

if __name__ == "__main__":
    main()
