
REPOSITORY OVERVIEW
===================
This repository is **1 of 4** in an **end-to-end data pipeline** that extracts, processes, and stores BBC data for analytical purposes.  

It focuses on the **data extraction and preprocessing phase**, using:
**Python** for web scraping  
**AWS Lambda** for serverless execution  
**Amazon S3** for cloud storage  

The extracted data is **stored in JSON format** in an S3 bucket, controlled via master JSON file for entity management

Directory overview

--LAMBDA_FUNCTION - Contains code that is uploaded to Lambda ( as well as dependancies files ) as Zip , deployment
--StepsActionByUser - Contains code that allows for testing , such as downloading current game model to file , running data floods ( all of the data to date)



