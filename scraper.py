import os
import pickle
from time import sleep
from datetime import datetime

from libs.web_scraping import WebScraping


# Paths
current_path = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(current_path, "cookies.pkl")


class Scraper(WebScraping):
    
    def __init__(self, user_email: str, user_password: str, headless: bool = False):
        """ Initialize the scraper.
        
        Args:
            user_email (str): user email
            user_password (str): user password
            headless (bool): run the browser in headless mode
        """
        
        print("Starting scraper...")
        
        super().__init__(
            headless=headless,
        )
        
        # Global data
        self.home_page = "https://research.txcourts.gov/CourtRecordsSearch/#!"
        self.global_selectors = {
            "spinner": '[mdb-progress-spinner]',
            "btn_login": '#signInLink',
        }
        
    def __set_home_page__(self):
        """ Load home page and refresh """
        
        self.set_page(self.home_page)
        sleep(2)
        self.refresh_selenium()

    