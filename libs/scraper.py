import os
import sys
from time import sleep
from datetime import datetime

from libs.web_scraping import WebScraping


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(current_path, "cookies.pkl")


class Scraper(WebScraping):
    
    def __init__(self, page_link: str, headless: bool = False):
        """ Initialize the scraper.
        
        Args:
            page_link (str): link to the page to scrape (with zoom and offset)
            headless (bool): run the browser in headless mode
        """
        
        print("Starting scraper...")
        
        super().__init__(
            headless=headless,
        )
        
        # Global data
        self.global_selectors = {
            "result": '.result-body > .ng-scope:not(div)'
        }
        
        # Load page
        self.page_link = page_link
        self.set_page(page_link)
        sleep(2)
        self.refresh_selenium()
        
        # Prepare the scraper
        self.__accept_terms__()
        self.__wait_load_results__()
        
        # Take screenshot
        self.screenshot("page_loaded")
    
    def __accept_terms__(self):
        """ Accept the terms of service. """
        
        print("Accepting terms of service...")
        
        selectors = {
            "btn_accept": '[ng-click="dm.agree()"]'
        }
        self.click_js(selectors["btn_accept"])
        self.refresh_selenium()
        
    def __wait_load_results__(self):
        """ Wait for the page to load. """
        
        print("Waiting for the page to load...")
        
        # Wait for results to laod
        for _ in range(3):
            
            # Validate if results are loaded (3 times)
            for _ in range(4):
                results_num = self.get_elems(self.global_selectors["result"])
                if len(results_num) > 0:
                    return
                sleep(2)
                self.refresh_selenium()
                
            # Reload page
            print("Error: Results not loaded. Reloading page...")
            self.driver.refresh()
            sleep(2)
            self.__accept_terms__()
            
        # Raise error if no results
        print("Error: No results found. Try again later or use a different link.")
        sys.exit()
                
    def get_property_data(self) -> dict:
        """ Extract data from current opened result
        
        Returns:
            list: property data gruoped
                [
                    {
                        street (str): street address
                        city (str): city
                        state (str): state
                        zip_code (str): zip code
                        country (str): country
                        maps_link (str): link to google maps
                        sale_date (str): date of the sale
                        status (str): status of the sale
                        sale_type (str): type of sale
                        date_pulled (str): date of the scraping
                        sale_notes (str): notes of the sale
                        judgment_date (str): date of the judgment
                        adjudget_value (str): adjudget value
                        es_min_bid (str): estimated minimum bid
                        equity (str): equity
                        equity_percent (str): equity percent
                        account_number (str): account number
                        case_number (str): case number
                        case_style (str): case style
                        link (str): link to the property,
                        address_error (bool): if there was an error in the address
                    }
                ]
        """
        
        selectors = {
            "address": 'h1',
            "country": 'dd:nth-child(2)',
            "maps_link": 'br + a[href^="https://www.google.com/maps/"]',
            "sale_date": 'dd:nth-child(6)',
            "status": 'dd:nth-child(14)',
            "sale_type": 'dd:nth-child(4)',
            "sale_notes": 'h3 + dl dd:last-child',
            "judgment_date": 'h3 + dl dd:nth-child(16)',
            "adjudget_value": 'dd:nth-child(10)',
            "es_min_bid": 'dd:nth-child(12)',
            'account_number': 'dd:nth-child(8)',
            'cause_number': 'h3 + dl dd:nth-child(8)',
            'case_style': 'h3 + dl dd:nth-child(14)',
        }
        
        raw_data = {}
        for field, selector in selectors.items():
            raw_data[field] = self.get_text(selector)
            
        # Extract address data
        try:
            address_parts = raw_data["address"].split(",")
            street = address_parts[0]
            address_parts = address_parts[1].split("-")
            address_parts = address_parts[0].strip().split()
            postal_code = address_parts[-1]
            state = address_parts[-2]
            city = " ".join(address_parts[:-2])
        except Exception:
            print("\t\tError: Address format not recognized. Skipping property address.")
            street = raw_data["address"]
            city = ""
            state = ""
            postal_code = ""
        
        # Get google maps link
        maps_link = self.get_attrib(selectors["maps_link"], "href")
        
        # Calculate equity and fix quantities
        if not raw_data["adjudget_value"]:
            raw_data["adjudget_value"] = "$0"
        if not raw_data["es_min_bid"]:
            raw_data["es_min_bid"] = "$0"
        adjudget_value_str = raw_data["adjudget_value"].replace("$", "").replace(",", "")
        es_min_bid_str = raw_data["es_min_bid"].replace("$", "").replace(",", "")
        adjudget_value = float(adjudget_value_str)
        es_min_bid = float(es_min_bid_str)
        equity = adjudget_value - es_min_bid
        equity_percent = 0
        if adjudget_value > 0:
            equity_percent = int(equity / adjudget_value * 10000) / 100
            
        today = datetime.now().strftime("%m/%d/%Y")
        
        return {
            "street": street,
            "city": city,
            "state": state,
            "zip_code": postal_code,
            "country": raw_data["country"],
            "maps_link": maps_link,
            "sale_date": raw_data["sale_date"],
            "status": raw_data["status"],
            "sale_type": raw_data["sale_type"],
            "date_pulled": today,
            "sale_notes": raw_data["sale_notes"],
            "judgment_date": raw_data["judgment_date"],
            "adjudget_value": f"${adjudget_value}",
            "es_min_bid": f"${es_min_bid}",
            "equity": f"${equity}",
            "equity_percent": f"{equity_percent}%",
            "account_number": raw_data["account_number"],
            "case_number": raw_data["cause_number"],
            "case_style": raw_data["case_style"],
            "link": self.page_link,
            "address_error": not bool(city),
        }
    
    def open_property_details(self, property_index: int) -> bool:
        """ Open the details of a property.

        Args:
            property_index (int): index of the property to open

        Returns:
            bool: True if the property was found and opened, False otherwise
        """
        
        selectors = {
            "detals_btn": '[ng-click="listing.openDetailModal()"]',
        }
        
        # generate selectors
        row_selector = f"{self.global_selectors["result"]}:nth-child({property_index})"
        row_details_btn = f"{row_selector} {selectors['detals_btn']}"
        is_row_details = self.get_elems(row_details_btn)
        
        # Validate if row is a link
        if not is_row_details:
            return False
        
        # Open details
        self.click_js(row_details_btn)
        sleep(1)
        self.refresh_selenium()
        
        return True
    
    def close_property_details(self):
        """ Close the details of a property. """
        
        selectors = {
            "close_btn": '[ng-click="detailmodal.close()"]',
        }
            
        # Close details tab
        self.click_js(selectors["close_btn"])
        self.refresh_selenium()
        
    def go_next_page(self) -> bool:
        """ Validate if there is a next page and go to it."""
        
        selectors = {
            "next": '.pagination-next:not(.disabled) > a'
        }
        
        is_next = self.get_elems(selectors["next"])
        if not is_next:
            return False
    
        self.click_js(selectors["next"])
        self.refresh_selenium()
        self.__wait_load_results__()
        
        return True