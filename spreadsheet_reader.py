import pandas as pd

class SpreadsheetReader:
    def __init__(self, file_path, subject_info=None):
        """
        :param file_path: Path to the downloaded spreadsheet.
        :param subject_info: (Optional) Additional info (e.g., day info from subject) to add to the DataFrame.
        """
        self.file_path = file_path
        self.subject_info = subject_info

    def load_dataframe(self):
        """Loads the spreadsheet into a pandas DataFrame."""
        try:
            if self.file_path.endswith('.xlsx'):
                # For Excel files
                df = pd.read_excel(self.file_path)
            elif self.file_path.endswith('.csv'):
                # For CSV files
                df = pd.read_csv(self.file_path)
            else:
                raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")
            print("Spreadsheet loaded into DataFrame successfully.")

            # If subject_info is provided, add it as a new column with the expected name.
            if self.subject_info:
                df["EmailSubjectInfo"] = self.subject_info
            return df
        except Exception as e:
            print("Error loading spreadsheet:", e)
            return None
