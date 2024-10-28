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


# Show settings
print("\n----------------------------------")
print(">>>>>> Taxsales Lgbs Bot <<<<<<")
print("GOOGLE_SHEET_LINK: ", GOOGLE_SHEET_LINK)
print("PAGE_LINK: ", PAGE_LINK)
print("SHEET_OUTPUT: ", SHEET_OUTPUT)
print("WAIT_SECONDS: ", WAIT_SECONDS)
print("----------------------------------\n")


def main():
    # Main workflow: scrape each property found
    # and save data in google sheets
    
    current_page_link = PAGE_LINK
    current_page = 1

    # Paths
    current_path = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(current_path, "credentials.json")
    cache_path = os.path.join(current_path, "cache.json")

    # Initialize data manager
    data_manager = DataManager(GOOGLE_SHEET_LINK, credentials_path,
                               cache_path, SHEET_OUTPUT)
    
    # Validate last page scraped and last status
    cache = data_manager.get_cache()
    if cache["last_page"] and not cache["finished"]:
        print(f"Resuming scraping from page '{cache['last_page']}'...")
        current_page_link = cache["last_page"]
        current_page = cache["last_page_num"]
        
    # Initialize scraper
    scraper = Scraper(current_page_link)
    
    # Scraping counters
    current_property = (current_page - 1) * 10 + 1

    while True:

        current_page_link = scraper.driver.current_url
        data_manager.update_page_cache(current_page_link, current_page, False)

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
                case_number = data["case_number"]
                old_status = data_manager.get_case_status(case_number)
                
                # Update or insert data
                if old_status:
                    data_manager.update_property(data)
                else:
                    data_manager.insert_property(data)

            # Close property details and wait
            scraper.close_property_details()
            sleep(WAIT_SECONDS)
            current_property += 1

        # Go to next results page
        has_next = scraper.go_next_page()
        if not has_next:
            data_manager.update_page_cache(current_page_link, 1, True)
            print("No more results. Done.")
            break
        current_page += 1

    print("\n----------------------------------")


if __name__ == "__main__":
    main()
