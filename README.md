# Business_card_image_to_text_extracting_with_OCR
## Overview
This Python project allows users to extract relevant information from business cards uploaded as images. The extracted data includes details such as name, designation, contact information, and company name. Users can verify and edit the extracted data before saving it to a MySQL database. Additionally, the project provides functionality to read data from the database, modify existing records, and delete unnecessary entries.

## Features
## 1. Image Upload and OCR:
  - Users can upload business card images via a Streamlit application.
  - The EasyOCR library is used to extract text from the images, along with bounding box coordinates (bbox).
## 2. Data Grouping:
  - Based on the height of the bounding boxes, the extracted text is grouped into three categories:
    ### Group 1:
          - Name and designation
    ### Group 2:
          - Mobile number, email address, website, street address, city, state, and pincode
    ### Group 3:
          - Company name
## 3. Data Verification and Editing:
  - Users can review the extracted data and make corrections if necessary.
  - The Streamlit DataFrame Editor component allows easy editing of the data.
## 4. Database Interaction:
  - The project connects to a MySQL database.
  - Users can store the verified data along with the uploaded image in the database.
  - Existing records can be retrieved, modified, or deleted as needed.
## 5. Image Storage:
  - The uploaded image is converted to binary format before storing it in the database.

## Settingup Instructions:
- Clone the repository to your local machine using (https://github.com/Nandha2790/business_card_image_to_text_extracting_with_OCR) .
- Install Python (if not already installed).
- Install the required libraries.
- Ensure MySQL is installed and running on your machine.
## Usage:
  1. Upload a business card image.
  2. Review the extracted data.
  3. Edit any inaccuracies.
  4. Save the verified data to the MySQL database.
  5. Retrieve, modify, or delete records as needed.

### Contact:
For any questions or feedback, feel free to reach out to [email_id: nandha2790@gmail.com]

### License:
This project is licensed under the Apache-2.0 license - see the LICENSE.md file for details
