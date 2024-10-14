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
            "result": '.row'
        }
        
        # Load page
        self.set_page(page_link)
        sleep(2)
        self.refresh_selenium()
        
        # Main loop
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
        
        


if __name__ == "__main__":
    # Test the scraper
    scraper = Scraper("https://taxsales.lgbs.com/map?lat=34.085100353427414&lon=-97.84238746874999&zoom=6&offset=0&ordering=precinct,sale_nbr,uid&sale_type=SALE,RESALE,STRUCK%20OFF,FUTURE%20SALE&in_bbox=-108.91660621874999,26.25957324631036,-86.76816871874999,41.24943669001917")