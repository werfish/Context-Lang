# <file:MANIFEST>MANIFEST.txt<file:MANIFEST/>
# <file:DataModelReqs>DataModel.txt<file:DataModelReqs/>
# <import:DB_MODELS_PY>db_models.py<import:DB_MODELS_PY/>
# <import:QUERIES_PY>queries.py<import:QUERIES_PY/>
# <import:BinanceIntegration>binance.py<import:BinanceIntegration/>

# <context:DATA_PROCESS_REQUIREMENTS>
# Requirements for this codefile (data_download_schedule.py) are as follows:
# 1. Create a function that downloads the current price of the pair mentioned in the manifest file
# from binance by using the Binance Integration class provided.
# 2. The function should store the price in the database using the ORM queries provided
# according to the data model provided in the DataModelReqs file.
# 3. The function should be scheduled to run every 1 second, at an exact second boundary.
# 4. The function should be able to handle keyboard interrupts and stop gracefully.
# 5. This code file will be run as a separate process from the main application.
# 6. The file will be run with Python data_download_schedule.py, so please setup everything
# inside the code.
# <context:DATA_PROCESS_REQUIREMENTS/>

# <prompt:CreateDataProcess>
# Please write the code according to the data process requirements.
# For context you get the MANIFEST with high level project description,
# the db models file, the queries file and the binance integration file.
# {MANIFEST}
# {DB_MODELS_PY}
# {QUERIES_PY}
# {BinanceIntegration}
# {DATA_PROCESS_REQUIREMENTS}
# <prompt:CreateDataProcess/>

# <context:DataProcess>
# <CreateDataProcess>
import time
import schedule
import logging
from binance import BinanceIntegration
from queries import create_fake_limit_order  # Assuming 'queries' is the module name where ORM queries are present.
from db import SessionLocal  # Assuming 'db' is the module name for database session management.
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Binance integration
binance_integration = BinanceIntegration()

def download_and_store_price():
    "/**Function to download BTC/USDT price and store in the database.*/"
    
    # Download the current price
    current_price_data = binance_integration.fetch_current_price('BTCUSDT')
    
    # Check for errors in fetching data
    if isinstance(current_price_data, str):
        logging.error(f"Failed to fetch current price: {current_price_data}")
        return
    
    # Store the price in database
    db = SessionLocal()
    try:
        # Note: Here we are assuming a quantity of 1 for the purpose of storing the price.
        order = create_fake_limit_order(db=db, price=current_price_data['price'], quantity=1, direction='buy')  
        logging.info(f"Stored current price in database: {order.price}")
    except Exception as error:
        logging.error(f"Error storing price in database: {error}")
    finally:
        db.close()

def run_scheduled_job():
    "/**Scheduler running every second to download and store price.*/"
    # Scheduling the task to run every second
    schedule.every(1).seconds.do(download_and_store_price)

    # Run scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logging.info("Starting the data download schedule process...")
    try:
        run_scheduled_job()
    except KeyboardInterrupt:
        logging.info("Data download schedule process interrupted and is now shutting down gracefully.")
        sys.exit()
# <CreateDataProcess/>
# <context:DataProcess/>
