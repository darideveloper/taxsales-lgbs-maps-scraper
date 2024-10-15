from libs.google_sheets import SheetsManager


class DataManager(SheetsManager):
    
    def __init__(self, google_sheet_link, creds_path, sheet_name=None):
        """ Construtor of the class"""

        super().__init__(google_sheet_link, creds_path, sheet_name)
        
        # Get all data from google sheet
        self.data = self.get_data()
        
    def get_case_status(self, case_number: str) -> str:
        """ Get the status of a case
        
        Args:
            case_number (str): case number
        
        Returns:
            str: case status
        """
        
        # Get the case status
        case_status_row = list(filter(
            lambda row: row["Case Number"] == case_number,
            self.data
        ))
        if case_status_row:
            return case_status_row[0]["Status"]
        else:
            return ""