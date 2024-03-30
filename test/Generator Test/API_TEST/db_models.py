# # Import global project settings and libraries
# <import>MANIFEST.txt<import/>
# <import>db.py<import/>
# <file:DataModel>DataModel.txt<file:DataModel/>

# # Prompt for generating SQLAlchemy models
# <prompt:GenerateORMModels>
# Please generate SQLAlchemy ORM models based on the project descriptions and specifications provided. 
# This should include models for calculation jobs, calculation results, and fake limit orders as detailed in the project documentation.
# db.py file contains the database engine and session setup and has a function to create the database tables if they don't exist.
# Please call this function after models are created to ensure the tables are created in the database.
# {PROJECT_DESCRIPTION} 
# {LIBRARIES} 
# {DataModel}
# {DB_PY}
# <prompt:GenerateORMModels/>

# <context:DB_MODELS_PY>
# <GenerateORMModels>
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>