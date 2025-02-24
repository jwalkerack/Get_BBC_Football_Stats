=========================
REPOSITORY OVERVIEW
=========================
- This repository is **1 of 4** in a data pipeline for extracting, processing, and storing BBC data.
- Focus: **Data extraction & preprocessing** using:
  → Python (web scraping & transformation)
  → AWS Lambda (serverless execution)
  → Amazon S3 (cloud storage)
- Extracted data is stored in **JSON format** in an S3 bucket, managed via a master JSON file.

=========================
DIRECTORY STRUCTURE
=========================

▶ **LAMBDA_FUNCTION/**
   ├── Contains Python scripts for:
   │   • Data Extraction → Scraping BBC data
   │   • Data Transformation → Structuring & formatting data
   │   • S3 Integration → Storing & retrieving data in S3
   ├── Includes `app.py` and dependency files for AWS Lambda deployment.

▶ **StepsActionByUser/**
   ├── Contains scripts for **manual actions & testing**.
   ├── Key scripts:
   │   • `Scenerio_Actions.py` → Defines user actions.
   │   • `FLOOD_S3.py` → Controls data rebuilds (DEV/PRD environments).
   │   • `Return_One_Match_Save_To_File.py` → Saves a single game model for testing.

=========================
SUMMARY
=========================
✔ **Extracts & prepares raw BBC data** for further processing.
✔ **Stores data in JSON format** on Amazon S3.
✔ **Automates workflows** using AWS Lambda.
✔ **Includes user-driven scripts** for data testing & validation.

