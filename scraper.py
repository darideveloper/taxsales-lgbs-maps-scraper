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
        
        # Run scraper main loop
        self.scrape_properties()
    
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
                
    def __get_property_data__(self):
        """ Extract data from current opened result """
        pass
    
    def scrape_properties(self):
        
        selectors = {
            "link": 'a',
            "details_btn": '[ng-click="popups.openDetailModal()"]',
            "close_btn": '[ng-click="detailmodal.close()"]'
        }
        
        # Loop rows skipping the header and the navigation
        for row_index in range(2, 11):
            
            # Show row in map
            row_selector = f"{self.global_selectors["result"]}:nth-child({row_index})"
            row_link = f"{row_selector} {selectors['link']}"
            self.click_js(row_link)
            self.refresh_selenium()
            
            # Open details
            self.click_js(selectors["details_btn"])
            self.refresh_selenium()
            
            data = self.__get_property_data__()
            
            # Close details tab
            self.click_js(selectors["close_btn"])
            self.refresh_selenium()
            


if __name__ == "__main__":
    # Test the scraper
    scraper = Scraper("https://taxsales.lgbs.com/map?lat=34.085100353427414&lon=-97.84238746874999&zoom=6&offset=0&ordering=precinct,sale_nbr,uid&sale_type=SALE,RESALE,STRUCK%20OFF,FUTURE%20SALE&in_bbox=-108.91660621874999,26.25957324631036,-86.76816871874999,41.24943669001917")