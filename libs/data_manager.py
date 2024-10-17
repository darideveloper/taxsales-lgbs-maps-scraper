import os
import json
from libs.google_sheets import SheetsManager


class DataManager(SheetsManager):

    def __init__(self, google_sheet_link: str, creds_path: os.path,
                 cache_path: os.path, sheet_name: str = None):
        """ Construtor of the class

        Args:
            google_sheet_link (str): google sheet link
            creds_path (os.path): path to the credentials file
            cache_path (os.path): path to the cache file
            sheet_name (str): name of the sheet
        """

        super().__init__(google_sheet_link, creds_path, sheet_name)

        # Get all data from google sheet
        self.data = []
        self.__update_sheet_data__()

        # Save cache file
        self.cache_path = cache_path

    def __update_sheet_data__(self):
        """ Get all data from the google sheet with empty rows removed
        """

        data = self.get_data()
        data = list(filter(lambda row: row["Property Street"], data))
        self.data = data

    def __get_case_number_row__(self, case_number: str) -> dict:
        """ Get the row of a case number

        Args:
            case_number (str): case number

        Returns:
            dict: row of the case number
        """

        # Get the case row
        case_number_row = list(filter(
            lambda row: row["Case Number"] == case_number,
            self.data
        ))
        if case_number_row:
            return case_number_row[0]
        else:
            return {}
        
    def __create_cache_file__(self):
        """ Create cache file with default data """

        data = {
            "last_page": "",
            "last_page_num": 1,
            "finished": False
        }
        
        with open(self.cache_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_case_status(self, case_number: str) -> str:
        """ Get the status of a case

        Args:
            case_number (str): case number

        Returns:
            str: case status
        """

        # Get the case status
        case_status_row = self.__get_case_number_row__(case_number)
        if case_status_row:
            return case_status_row["Status"]
        else:
            return ""

    def insert_property(self, data: dict):
        """ Insert a property data in the google sheet

        Args:
            data (dict): property scraped data
        """

        self.__update_sheet_data__()

        # Insert data in the bottom of the google sheet
        last_row = len(self.data)
        data_row = list(data.values())
        self.write_data([data_row], last_row + 2)

    def update_property(self, data):
        """ Update a property data in the google sheet

        Args:
            data (dict): property scraped data
        """

        self.__update_sheet_data__()

        # Get row index of the case number
        case_number = data["case_number"]
        case_number_row = self.__get_case_number_row__(case_number)
        row_index = self.data.index(case_number_row)

        # Replace the row with the new data
        data_row = list(data.values())
        self.write_data([data_row], row_index + 2)

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
        
        # Create file if not exists
        if not os.path.exists(self.cache_path):
            self.__create_cache_file__()

        with open(self.cache_path, "r") as file:
            return json.load(file)
