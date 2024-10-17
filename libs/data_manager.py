from libs.google_sheets import SheetsManager


class DataManager(SheetsManager):
    
    def __init__(self, google_sheet_link, creds_path, sheet_name=None):
        """ Construtor of the class"""

        super().__init__(google_sheet_link, creds_path, sheet_name)
        
        # Get all data from google sheet
        self.data = []
        self.__update_sheet_data__()
        
    def __update_sheet_data__(self):
        """ Get all data from the google sheet with empty rows removed
        """
        
        data = self.get_data()
        data = list(filter(lambda row: row["Property Street"], data))
        self.data = data
        
    def __get_case_number_row__(self, case_number: str):
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
        