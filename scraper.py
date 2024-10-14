import os
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
        self.set_page(page_link)
        sleep(2)
        self.refresh_selenium()
        
        # Prepare the scraper
        self.__accept_terms__()
        self.__wait_load__()
    
    def __accept_terms__(self):
        """ Accept the terms of service. """
        
        print("Accepting terms of service...")
        
        selectors = {
            "btn_accept": '[ng-click="dm.agree()"]'
        }
        self.click_js(selectors["btn_accept"])
        self.refresh_selenium()
        
    def __wait_load__(self):
        """ Wait for the page to load. """
        
        print("Waiting for the page to load...")
        
        # Wait for results to laod
        for _ in range(3):
            results_num = self.get_elems(self.global_selectors["result"])
            if len(results_num) > 0:
                return
            sleep(2)
            
        # Raise error if no results
        raise print("Error: No results found.")
                
    def get_property_data(self):
        """ Extract data from current opened result """
        sleep(3)
        return {}
    
    def open_property_details(self, property_index: int) -> bool:
        """ Open the details of a property.

        Args:
            property_index (int): index of the property to open

        Returns:
            bool: True if the property was found and opened, False otherwise
        """
        
        selectors = {
            "link": 'a',
            "details_btn": '[ng-click="popups.openDetailModal()"]',
        }
        
        # generate selectors
        row_selector = f"{self.global_selectors["result"]}:nth-child({property_index})"
        row_link = f"{row_selector} {selectors['link']}"
        is_row_link = self.get_elem(row_link)
        
        # Validate if row is a link
        if not is_row_link:
            return False
        
        # Open details
        self.click_js(row_link)
        self.refresh_selenium()
        self.click_js(selectors["details_btn"])
        sleep(2)
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