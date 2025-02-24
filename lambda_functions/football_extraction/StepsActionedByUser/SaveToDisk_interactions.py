## What is the Purpose of this code

import json
import os
import logging
import json
import os
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def save_match_to_file(match_data, filename, folder_path=None):
    """Saves JSON match data to a user-defined folder or a default one if not provided."""
    try:
        # Convert the match data to a formatted JSON string
        json_data = json.dumps(match_data, indent=2, ensure_ascii=False)

        # Use user-defined folder path or default to 'test_data' inside the current project
        if folder_path is None:
            folder_path = os.path.join(os.getcwd(), "test_data")

        # Create the directory if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Define the full path for the output file
        file_path = os.path.join(folder_path, filename)

        # Write the JSON data to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(json_data)

        print(f"Match data successfully saved to {file_path}")

    except Exception as e:
        print(f"Error saving match data: {e}")








