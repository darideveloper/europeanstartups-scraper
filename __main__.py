import os
from time import sleep
from logs import logger
from scraping_manager.automate import Web_scraping
from dotenv import load_dotenv

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
                
def main (): 
    
    # Scraping workflow
    scraper = Scraper ()
    scraper.wait_table_load()
    print ("done")

if __name__ == "__main__":
    main()