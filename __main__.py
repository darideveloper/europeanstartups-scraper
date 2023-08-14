import os
import csv
from time import sleep
from logs import logger
from dotenv import load_dotenv
from collections import OrderedDict
from scraping_manager.automate import Web_scraping

# Read credentials from .env file
load_dotenv ()
CHROME_PATH = os.environ.get("CHROME_PATH")
HEADLESS = os.environ.get("SHOW_BROWSER") == "False"

class Scraper (Web_scraping):
    def __init__ (self): 
        """ Read credentials from .env and start scraper """
        
        # Start scraper-
        logger.info ("Killing chrome...")
        web_page = "https://app.europeanstartups.co/companies.startups/f/data_type/anyof_Verified/regions/allof_European%20Union"
        super().__init__(web_page, headless=HEADLESS, chrome_folder=CHROME_PATH, start_killing=True)
        logger.info ("Starting scraper and loading page...")
        
        # CSS global selectors
        self.selector_row = ".virtual-list.table-list > .table-list-item"
        self.selector_table = "#window-scrollbar > div:first-child"
        
        # Global data for csv file
        self.headers = []
        
        # Outpur file
        self.csv_file = os.path.join (os.path.dirname(__file__), "output.csv")
        
        # Clean output file
        with open (self.csv_file, "w") as file:
            file.write("")
     
        # List of business already extracted
        self.last_bussiness = []
        
        # Counter of number of scrolls in page
        self.scroll_counter = 1
        self.scroll_units = 2500
                
    def __save_csv__ (self, data, multiple_rows=False):
        """ Save row in the output csv file """
        
        logger.debug ("Saving data in csv file: {','.join(data)}")
        
        with open (self.csv_file, "a", encoding='UTF-8', newline='') as file:
            csv_writer = csv.writer(file)
            
            if multiple_rows: 
                csv_writer.writerows(data)
            else:
                csv_writer.writerow(data)
            
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
        logger.info ("Scraping data...")
        selector_current_row = f"{self.selector_row}:nth-child(row_num)"
        
        selectors_row = OrderedDict()
        selectors_row ["name"] = (f"{selector_current_row} .table-list-columns-fixed.hbox .entity-name__name-text", "text")
        selectors_row ["details_link"] = (f"{selector_current_row} .table-list-columns-fixed.hbox a.entity-name__name-text", "link")
        selectors_row ["dealroom_signal"] = (f"{selector_current_row} .table-list-columns > .startupRankingRating .ranking-bar-legend", "text")
        selectors_row ["market"] = (f"{selector_current_row} .table-list-columns > .companyMarket .markets-column", "text")
        selectors_row ["type"] = (f"{selector_current_row} .table-list-columns > .type .business-type-column", "text")
        selectors_row ["launch_date"] = (f"{selector_current_row} .table-list-columns > .launchDate time", "text")
        selectors_row ["valuation"] = (f"{selector_current_row} .table-list-columns > .valuation", "text")
        selectors_row ["total_funding"] = (f"{selector_current_row} .table-list-columns > .totalFunding", "text") 
        selectors_row ["location"] = (f"{selector_current_row} .table-list-columns > .hqLocations", "text")
        selectors_row ["last_round"] = (f"{selector_current_row} .table-list-columns > .lastFundingEnhanced .funding-round-cell-wrapper", "text")
        selectors_row ["revenue"] = (f"{selector_current_row} .table-list-columns > .revenue", "text")
        selectors_row ["revenue"] = (f"{selector_current_row} .table-list-columns > .revenue", "text")
        selectors_row ["status"] = (f"{selector_current_row} .table-list-columns > .companyStatus", "text")
        selectors_row ["growth_stage"] = (f"{selector_current_row} .table-list-columns > .growthStage > span > span", "text")
        
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
        self.__wait_load__(selectors_row ["name"][0].replace("row_num", str(1)), 0)            
        
        # Get number for rows
        rows_num = len(self.get_elems(self.selector_row))
        
        # Loop over rows
        data_rows = []
        for row_num in range (1, rows_num + 1):
        # for row_num in range (1, 2): # DEBUG
            
            # incress row number
            rows_num += 1

            # List for store data or the current row 
            data_row = []
            
            # Extract headers and save in csv
            if not self.headers:
                self.headers = [name.upper().replace("_", " ") for name in selectors_row.keys()]
                self.headers += [name.upper().replace("_", " ") for name in selectors_details.keys()]
                self.__save_csv__ (self.headers)
                
            # Extract data from rows page
            for _, (selector_value, selector_type) in selectors_row.items():
                value = self.__get_value__ (selector_value.replace("row_num", str(row_num)), selector_type)
                data_row.append(value)
                
            # valiudate if current row (with link) is in last_bussiness
            if data_row [1] in self.last_bussiness:
                
                logger.debug (f"Row skipped: {data_row [0]} {data_row [1]}")
                
                # Skip duplicated row
                continue
            
            logger.info (f"\tcurrent bussiness: {data_row[0]}")
            
            # Save current row link in last_bussiness
            self.last_bussiness.append (data_row [1])
                
            # Open details page
            self.open_tab()
            self.switch_to_tab(1)
            
            self.set_page(data_row [1])
            sleep (10)
            self.refresh_selenium (back_tab=1)
            
            # Wait to load current details page using an elem as reference
            h1 = self.get_text ("h1.name")
            if not h1:
                sleep (20)
                
                self.driver.refresh ()
                break
            
            # Extract data from details page
            for _, (selector_value, selector_type) in selectors_details.items():
                value = self.__get_value__ (selector_value, selector_type)
                data_row.append(value)
            
            # Go back to results page
            self.close_tab()
            self.switch_to_tab(0)
            
            # Save current row
            data_rows.append (data_row)
            
            # Debug status
            logger.debug (f"New bussiness: {','.join(data_row)}")
            
        # Show status
        logger.info (f"New bussiness extracted: {len(data_rows)}")
            
        # Save rows in csv
        if data_rows:
            self.__save_csv__ (data_rows, multiple_rows=True)
            
        return len(data_rows)
        
    def load_more_results (self):
        """ Load more rows / results in table """
        
        sleep (2)
        self.refresh_selenium ()
        print ()
        logger.info ("Loading more results...")

        # Scroll down for load more results
        self.scroll(self.selector_table, 0, self.scroll_counter*self.scroll_units)
        sleep (2)
        self.scroll(self.selector_table, 0, self.scroll_counter*self.scroll_units)
        sleep (2)
        self.scroll_counter += 1
            
        # Refresh page
        sleep(15)
        self.refresh_selenium()
                
def main (): 
    
    # Scraping workflow
    scraper = Scraper ()
    tries = 0
    while True:
        
        # Extract data and load more results
        results_found = scraper.extract_row ()
        scraper.load_more_results ()
        
        # End loop where no more results are found
        if not results_found:
            tr1es += 1
            
            if tries >= 3: 
                break
            
            continue  

        tries = 0

        
    print ("done")

if __name__ == "__main__":
    main()