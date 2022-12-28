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
        
    def __wait_load__ (self, selector, back_tab):
        """ Wait until the table is loaded """
        
        logger.info ("Wating for page load...")
        while True:
            elem_text = self.get_text(selector)
            if elem_text:
                break
            else: 
                sleep (2)
                self.refresh_selenium(back_tab=back_tab)
                
    def __save_row_csv__ (self, row):
        """ Save row in the output csv file """
        
        with open (self.csv_file, "a", encoding='UTF-8', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(row)
            
    def __get_value__ (self, selector_value, selector_type):
        """Get value from selector

        Args:
            selector_value (str): css selector of the value to extract
            selector_type (str): type of the css selector (text, link or text-all)

        Returns:
            str: value who match with the selector and type
        """
        
        # Get cell value from selector
        if selector_type == "text":
            value = self.get_text(selector_value)
        elif selector_type == "link":
            value = self.get_attrib(selector_value, "href")
        elif selector_type == "text-all":
            value = ", ".join(self.get_texts (selector_value))
        elif selector_type == "link-all":
            value = ", ".join(self.get_attribs(selector_value, "href"))
        else:
            value = "-"
        
        # Format value
        if not value:
            value = "-"
            
        # Clen value
        value = value.replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("  ", " ").strip()
        
        return value
                
    def extract_row (self):
        """ Extract data of the currect visible rows """
        
        
        # CSS selectors
        selector_current_row = f"{self.selector_row}:nth-child(row_num)"
        
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
        
        selectors_details = OrderedDict()
        selectors_details ["empleoyees"] = (".field.employees > .description", "text")
        selectors_details ["ownership"] = (".field.ownership > .description", "text")
        selectors_details ["market_cap"] = (".field.market-cap > .description", "text")
        selectors_details ["debt"] = (".field.net-debt > .description", "text")
        selectors_details ["website"] = (".item-details-info__website > a", "link")
        selectors_details ["firm_value"] = (".field.firm-valuation > .description", "text")
        selectors_details ["tags"] = (".company-tags li", "text")
        selectors_details ["socials"] = (".item-details-info__website > .resource-urls > a", "link-all")
        
        
        # Wait load current results page using first elem as reference
        self.__wait_load__(selectors_row ["name"].replace("row_num", str(1)), 0)
        
        # Get number for rows
        rows_num = len(self.get_elems(self.selector_row))
        
        # Loop over rows
        for row_num in range (1, rows_num + 1):
            
            # Extract headers and save in csv
            if not self.headers:
                self.headers = [name.upper().replace("_", " ") for name in selectors_row.keys()]
                self.headers += [name.upper().replace("_", " ") for name in selectors_details.keys()]
                self.__save_row_csv__ (self.headers)
                
            
            # Extract data from rows and format
            data_row = []
            for _, selector in selectors_row.items():
                
                # Get cell value
                cell_value = self.get_text(selector.replace("row_num", str(row_num)))
                if not cell_value:
                    cell_value = "-"
                    
                # Clean cell and save
                cell_value = cell_value.replace("\n", ", ")
                data_row.append(cell_value)
                
            # Open details page
            details_link = self.get_attrib(selectors_row ["name"].replace("row_num", str(row_num)), "href") 
            self.open_tab()
            self.switch_to_tab(1)
            self.set_page(details_link)
            
            # Wait to load current details page using an elem as reference
            self.__wait_load__(selectors_details ["empleoyees"][0], 1)
            
            # Extract data from details page
            for _, (selector_value, selector_type) in selectors_details.items():
                value = self.__get_value__ (selector_value, selector_type)
                data_row.append(value)
            
            # Go back to results page
            self.close_tab()
            self.switch_to_tab(0)
            
            # Save row in csv
            self.__save_row_csv__ (data_row)
            print ()
                
def main (): 
    
    # Scraping workflow
    scraper = Scraper ()
    scraper.extract_row ()
    print ("done")

if __name__ == "__main__":
    main()