# <file:MANIFEST>MANIFEST.txt<file:MANIFEST/>
# <file:DataModelReqs>DataModel.txt<file:DataModelReqs/>
# <import:DB_MODELS_PY>db_models.py<import:DB_MODELS_PY/>
# <import:QUERIES_PY>queries.py<import:QUERIES_PY/>
# <import:BinanceIntegration>binance.py<import:BinanceIntegration/>
# <import:DB_PY>db.py<import:DB_PY/>

# <context:DATA_PROCESS_REQUIREMENTS>
# Requirements for this codefile (data_download_schedule.py) are as follows:
# 1. Create a function that downloads the current price of the pair mentioned in the manifest file
# from binance by using the Binance Integration class provided from the binance.py file.
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
# Remember that this file needs to be run with "PYTHON data_download_schedule.py"
# project filenames are listed in the manifest.
# {MANIFEST}
# {DB_MODELS_PY}
# {DB_PY}
# {QUERIES_PY}
# {BinanceIntegration}
# {DATA_PROCESS_REQUIREMENTS}
# <prompt:CreateDataProcess/>

# <context:DataProcess>
# <CreateDataProcess>
from datetime import datetime
import schedule
import time
from threading import Event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import PriceData, Base
from binance import BinanceIntegration

# Import necessary components to establish a connection to the database
from db import DATABASE_URL, SessionLocal

# Setup Binance Integration
binance_integration = BinanceIntegration()

# Create database connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Define the scheduled function
def fetch_and_store_price():
    # Fetch current BTC/USDT price using BinanceIntegration
    current_price = binance_integration.get_current_price()
    print(current_price)
    
    # Store the price in the database
    price_data = PriceData(price=current_price, timestamp=datetime.utcnow())
    session.add(price_data)
    session.commit()

# Schedule the function to run every second at an exact second boundary
schedule.every(1).seconds.do(fetch_and_store_price)

# Graceful shutdown event
shutdown_event = Event()

def run_continuously(interval=1):
    """
    Continuously run, while waiting for schedule to run jobs at each elapsed interval.
    """
    cease_continuous_run = shutdown_event.wait(interval)
    while not cease_continuous_run:
        schedule.run_pending()
        cease_continuous_run = shutdown_event.wait(interval)

def graceful_shutdown(signum, frame):
    """
    Triggered when a signal is received, stops new scheduling and waits for jobs to finish.
    """
    print(f"Received exit signal: {signum}, shutting down gracefully...")
    shutdown_event.set()

# Listen for keyboard interrupt (SIGINT)
try:
    # Start the background thread
    import threading
    continuous_thread = threading.Thread(target=run_continuously)
    continuous_thread.start()
    
    # Keep the script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Process interrupted by the user, stopping schedule...")
    shutdown_event.set()

# Wait for the last jobs to complete before exiting
continuous_thread.join()

print("Scheduler shutdown successfully, exiting now.")
# <CreateDataProcess/>
# <context:DataProcess/>
