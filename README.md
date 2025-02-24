
REPOSITORY OVERVIEW
===================
This repository is **1 of 4** in an **end-to-end data pipeline** that extracts, processes, and stores BBC data for analytical purposes.  

It focuses on the **data extraction and preprocessing phase**, using:
**Python** for web scraping  
**AWS Lambda** for serverless execution  
**Amazon S3** for cloud storage  

The extracted data is **stored in JSON format** in an S3 bucket, controlled via master JSON file for entity management

Directory overview

**LAMBDA_FUNCTION**

Contains .py that are used to perform data extraction and data tranformation and data interactions with S3. This code as well as app.py and dependacy files are saved to deployment packagefor lambda 
**StepsActionByUser** 

Using the Scenerio_Actions.py 
FLOOD_S3 , where data re builds can be performed ( Config , controls if this happens in DEV or Production)
Return_One_Match_Save_To_File  saves an Game Model to file . Used for testing purposes



