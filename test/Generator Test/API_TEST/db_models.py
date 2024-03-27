# # Import global project settings and libraries
# <import>MANIFEST.txt<import/>
# <import>DataModel.txt<import/>
# <import>db.py<import/>

# # Prompt for generating SQLAlchemy models
# <prompt:GenerateORMModels>
# Please generate SQLAlchemy ORM models based on the project descriptions and specifications provided. This should include models for calculation jobs, calculation results, and fake limit orders as detailed in the project documentation.
# database setup is in db.py file.
# {PROJECT_DESCRIPTION} 
# {LIBRARIES} 
# {DB_PY}
# <prompt:GenerateORMModels/>

# <context:DB_MODELS_PY>
# <GenerateORMModels>
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>