import os
import csv
from time import sleep
from logs import logger
from dotenv import load_dotenv
from collections import OrderedDict
from scraping_manager.automate import Web_scraping

class Scraper (Web_scraping):
    def __init__ (self): 
        """ Read credentials from .env and start scraper """
        
        # Read credentials from .env file
        load_dotenv ()
        CHROME_PATH = os.environ.get("CHROME_PATH")
        HEADLESS = os.environ.get("SHOW_BROWSER") == "False"
        
        # Start scraper
        logger.info ("Killing chrome...")
        web_page = "https://app.europeanstartups.co/companies.startups/f/data_type/anyof_Verified/regions/allof_European%20Union"
        super().__init__(web_page, headless=False, chrome_folder=CHROME_PATH, start_killing=True)
        logger.info ("Starting scraper...")
        
        # CSS global selectors
        self.selector_row = ".virtual-list.table-list > .table-list-item"
        
        # Global data for csv file
        self.headers = []
        
        # Outpur file
        self.csv_file = os.path.join (os.path.dirname(__file__), "output.csv")
        
        # Clean output file
        with open (self.csv_file, "w") as file:
            file.write("")
        
    def wait_table_load (self):
        """ Wait until the table is loaded """
        
        logger.info ("Wating for page load...")
        selector_first_elem = f"{self.selector_row}:first-child .entity-name__info .entity-name__name-text"
        while True:
            first_elem_text = self.get_text(selector_first_elem)
            if first_elem_text:
                break
            else: 
                sleep (3)
                self.refresh_selenium()  
                
    def __save_row_csv__ (self, row):
        """ Save row in the output csv file """
        
        with open (self.csv_file, "a", encoding='UTF-8', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(row)
                
    def extract_row_data (self):
        """ Extract data of the currect visible rows """
        
        # Get number for rows
        rows_num = len(self.get_elems(self.selector_row))
        
        # Loop over rows
        for row_num in range (1, rows_num + 1):
            
            # CSS selectors
            selector_current_row = f"{self.selector_row}:nth-child({row_num})"
            selectors_row = OrderedDict()
            selectors_row ["name"] = f"{selector_current_row} .table-list-columns-fixed.hbox .entity-name__name-text"
            selectors_row ["dealroom_signal"] = f"{selector_current_row} .table-list-columns > .startupRankingRating .ranking-bar-legend"
            selectors_row ["market"] = f"{selector_current_row} .table-list-columns > .companyMarket .markets-column"
            selectors_row ["type"] = f"{selector_current_row} .table-list-columns > .type .business-type-column"
            selectors_row ["launch_date"] = f"{selector_current_row} .table-list-columns > .launchDate time"
            selectors_row ["valuation"] = f"{selector_current_row} .table-list-columns > .valuation"
            selectors_row ["total_funding"] = f"{selector_current_row} .table-list-columns > .totalFunding" 
            selectors_row ["location"] = f"{selector_current_row} .table-list-columns > .hqLocations"
            selectors_row ["last_round"] = f"{selector_current_row} .table-list-columns > .lastFundingEnhanced .funding-round-cell-wrapper"
            selectors_row ["revenue"] = f"{selector_current_row} .table-list-columns > .revenue"
            selectors_row ["revenue"] = f"{selector_current_row} .table-list-columns > .revenue"
            selectors_row ["status"] = f"{selector_current_row} .table-list-columns > .companyStatus"
            selectors_row ["growth_stage"] = f"{selector_current_row} .table-list-columns > .growthStage > span > span"
            
            # Extract headers and save in csv
            if not self.headers:
                headers = [name.upper().replace("_", " ") for name in selectors_row.keys()]
                self.__save_row_csv__ (headers)
                
            
            # Extract data and format
            data_row = []
            for name, selector in selectors_row.items():
                
                # Get cell value
                cell_value = self.get_text(selector)
                if not cell_value:
                    cell_value = "-"
                    
                # Clean cell and save
                cell_value = cell_value.replace("\n", ", ")
                data_row.append(cell_value)
            
            # Save row in csv
            self.__save_row_csv__ (data_row)
            
                
def main (): 
    
    # Scraping workflow
    scraper = Scraper ()
    scraper.wait_table_load()
    scraper.extract_row_data ()
    print ("done")

if __name__ == "__main__":
    main()