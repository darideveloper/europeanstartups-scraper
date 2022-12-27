import os
from time import sleep
from logs import logger
from scraping_manager.automate import Web_scraping
from dotenv import load_dotenv

def main (): 
    
    # Read credentials from .env file
    load_dotenv ()
    CHROME_PATH = os.environ.get("CHROME_PATH")
    HEADLESS = os.environ.get("SHOW_BROWSER") == "False"
    
    # Start scraper
    logger.info ("Killing chrome...")
    web_page = "https://app.europeanstartups.co/companies.startups/f/data_type/anyof_Verified/regions/allof_European%20Union"
    scraper = Web_scraping(web_page, headless=False, chrome_folder=CHROME_PATH, start_killing=True)
    logger.info ("Starting scraper...")
    
    # Main selectors
    selector_row = ".virtual-list.table-list > .table-list-item"
    
    # Wait until the page is loaded
    logger.info ("Wating for page load...")
    selector_first_elem = f"{selector_row}:first-child .entity-name__info .entity-name__name-text"
    while True:
        first_elem_text = scraper.get_text(selector_first_elem)
        if first_elem_text:
            break
        else: 
            sleep (3)
            scraper.refresh_selenium()
    print ()
            


if __name__ == "__main__":
    main()