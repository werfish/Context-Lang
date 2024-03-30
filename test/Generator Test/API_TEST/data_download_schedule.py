# <file:MANIFEST>MANIFEST.txt<file:MANIFEST/>
# <file:DataModelReqs>DataModel.txt<file:DataModelReqs/>
# <import:DB_MODELS_PY>db_models.py<import:DB_MODELS_PY/>
# <import:QUERIES_PY>querries.py<import:QUERIES_PY/>
# <import:BinanceIntegration>binance.py<import:BinanceIntegration/>

# <context:DATA_PROCESS_REQUIREMENTS>
# Requirements for this codefile (data_download_schedule.py) are as follows:
# 1. Create a function that downloads the current price of the pair mentioned in the manifest file
# from binance by using the Binance Integration class provided.
# 2. The function should store the price in the database using the ORM queries provided
# according to the data model provided in the DataModelReqs file.
# 3. The function should be scheduled to run every 1 second, at an exact second boundary.
# 4. The function should run indefinitely until manually stopped.
# 5. The function should be able to handle exceptions and log them to a log file.
# 6. The function should be able to handle keyboard interrupts and stop gracefully.
# 7. This code file will be run as a separate process from the main application.
# 8. The file will be run with Python data_download_schedule.py, so please setup everything
# inside the code.
# <context:DATA_PROCESS_REQUIREMENTS/>

# <prompt:CreateDataProcess>
# Please write the code according to the data process requirements.
# For context you get the MANIFEST with high level project description,
# the data model requirements, the db models file, the queries file and the binance integration file.
# {MANIFEST}
# {DataModelReqs}
# {DB_MODELS_PY}
# {QUERIES_PY}
# {BinanceIntegration}
# <prompt:CreateDataProcess/>

# <context:DataProcess>
# <CreateDataProcess>
# <CreateDataProcess/>
# <context:DataProcess/>
