import os
import json
from libs.google_sheets import SheetsManager


class DataManager(SheetsManager):

    def __init__(self, google_sheet_link: str, creds_path: os.path,
                 cache_path: os.path, sheet_output: str = None, sheet_input: str = None):
        """ Construtor of the class

        Args:
            google_sheet_link (str): google sheet link
            creds_path (os.path): path to the credentials file
            cache_path (os.path): path to the cache file
            sheet_name (str): name of the sheet
        """

        super().__init__(google_sheet_link, creds_path, sheet_output)
        
        # Save sheets names
        self.sheet_input = sheet_input
        self.sheet_output = sheet_output

        # Get all data from google sheet
        self.data = {
            sheet_input: [],
            sheet_output: []
        }
        self.__update_sheet_data__(self.sheet_output)
        self.__update_sheet_data__(self.sheet_input)

        # Save cache file
        self.cache_path = cache_path

    def __update_sheet_data__(self, sheet_name: str):
        """ Save in instance all data from the google sheet with empty rows removed
        
        Args:
            sheet_name (str): name of the sheet
        """
        
        # Change to the correct sheet
        self.set_sheet(sheet_name)

        # Clean empty rows
        data = self.get_data()
        data = list(filter(lambda row: row["Property Street"], data))
        
        # Save data
        self.data[sheet_name] = data

    def __create_cache_file__(self):
        """ Create cache file with default data """

        data = {
            "last_page": "",
            "last_page_num": 1,
            "finished": False
        }
        
        with open(self.cache_path, "w") as file:
            json.dump(data, file, indent=4)
            
    def __heightlight__(self, range: str):
        """ Highlight a range in red color
        
        Args:
            range (str): range to highlight
        """
        
        color = (244 / 255, 204 / 255, 204 / 255)
        self.set_bg_color(range, color)
        print(f"\tHightlighted range: {range}")

    def get_account_number_row(self, account_number: str, sheet_name: str = "") -> dict:
        """ Get the row of a case number

        Args:
            account_number (str): case number

        Returns:
            dict: row of the case number
        """
        
        if not sheet_name:
            sheet_name = self.sheet_output

        # Get the case row
        account_number_row = list(filter(
            lambda row: str(row["Account Number"]) in str(account_number),
            self.data[sheet_name]
        ))
        if account_number_row:
            return account_number_row[0]
        else:
            return {}

    def get_case_status(self, account_number: str) -> str:
        """ Get the status of a case

        Args:
            account_number (str): account number

        Returns:
            str: case status
        """

        # Get the case status
        case_status_row = self.get_account_number_row(account_number)
        if case_status_row:
            return case_status_row["Status"]
        else:
            return ""

    def insert_property(self, data: dict):
        """ Insert a property data in the google sheet

        Args:
            data (dict): property scraped data
        """
        
        # Set the correct sheet and update data
        self.set_sheet(self.sheet_output)
        self.__update_sheet_data__(self.sheet_output)

        # Insert data in the bottom of the google sheet
        last_row = len(self.data[self.sheet_output])
        data_row = list(data.values())
        data_row_str = list(map(str, data_row))
        self.write_data([data_row_str], last_row + 2)
        
        # Hightlight the row in red if there is an address_error
        if data["address_error"]:
            range = self.get_range(last_row + 2, 1, len(data_row))
            self.__heightlight__(range)

    def update_property(self, data):
        """ Update a property data in the google sheet

        Args:
            data (dict): property scraped data
        """
        
        # Set the correct sheet and update data
        self.set_sheet(self.sheet_output)
        self.__update_sheet_data__(self.sheet_output)

        # Get row index of the case number
        account_number = data["account_number"]
        account_number_row = self.get_account_number_row(account_number)
        row_index = self.data[self.sheet_output].index(account_number_row)

        # Replace the row with the new data
        data_row = list(data.values())
        self.write_data([data_row], row_index + 2)
        
        # Hightlight the row in red if there is an address_error
        if data["address_error"]:
            range = self.get_range(row_index + 2, 1, len(data_row))
            self.__heightlight__(range)

    def update_page_cache(self, page_link: str, page_num: int, finished: bool):
        """ Save in local json file the last page link and
        if it have finished the scraping

        Args:
            page_link (str): last page link
            page_num (int): last page number
            finished (bool): if the scraping have finished
        """

        # Update data
        current_cache = self.get_cache()
        current_cache["last_page"] = page_link
        current_cache["last_page_num"] = page_num
        current_cache["finished"] = finished

        # Write data
        with open(self.cache_path, "w") as file:
            json.dump(current_cache, file, indent=4)

    def get_cache(self) -> dict:
        """ Get the cache data

        Returns:
            dict: cache data
        """
        
        try:
            with open(self.cache_path, "r") as file:
                cache_data = json.load(file)
        except Exception:
            cache_data = {}
        
        # Create file if not exists
        if not cache_data:
            self.__create_cache_file__()

            with open(self.cache_path, "r") as file:
                cache_data = json.load(file)
                
        return cache_data