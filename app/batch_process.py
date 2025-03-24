import os
import sqlite3
import logging
import requests


# Logging
logging.basicConfig(
    filename='app/logs/batch.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# CONSTANTS
API_URL = 'http://127.0.0.1:8000/predict/'
TEST_IMAGES_DIR = r".//app/test_images"
DB_FILE = 'database/prediction.db'


# Checking api run
def check_api():
    """Check if API is running before processing images."""
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False
    return False


# DATABASE INITIALIZATION
def initialze_db():
   """Create a database to store batch processing predictions."""

   conn = sqlite3.connect(DB_FILE)
   cursor = conn.cursor()
   cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        predicted_class TEXT,
        confidence REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
   """)
   conn.commit()
   conn.close()
   logging.info("Database initialized.")


def process_image():
    """Process new images, send them to the API, and store predictions."""

    for filename in os.listdir(TEST_IMAGES_DIR):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            file_path = os.path.join(TEST_IMAGES_DIR, filename)
            logging.info(f'Processing image: {filename}')

            try:
                with open(file_path, "rb") as image_file:
                    response = requests.post(API_URL, files={"file": ("image.jpg", image_file, "image/jpeg")})
                if response.status_code == 200:
                    result = response.json()
                    save_prediction(filename=filename, result=result)
                else:
                    logging.warning(f'Error processing {filename}: {response.json()}')
                    
            except Exception as e:
                logging.error(f'Unexpected error processing {filename}: {str(e)}')


def save_prediction(filename, result):
    """Save prediction results in the database."""

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (filename, predicted_class, confidence)
            VALUES (?, ?, ?)
        """, (filename, result['predicted_class'], result['confidence']))
        conn.commit()
        conn.close()
        logging.info(f'Saved to database: {result}')

    except Exception as e:
        logging.error(f'Database error: {str(e)}')


if __name__ == "__main__":
    logging.info('Checking if API is running...')
    if check_api():
        logging.info('FastAPI is running. Starting batch processing')
        initialze_db()
        process_image()
        logging.info('Batch processing completed!!!')
    else:
        logging.error('FastAPI is NOT running!!! Please start the server first.')