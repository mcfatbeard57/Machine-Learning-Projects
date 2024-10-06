# Preprocessing (Add Logging):
import cv2
import logging

def preprocess_invoice(image_path):
  # ... (Existing code for image reading, grayscale conversion, thresholding)

  logging.info(f"Found {len(cnts)} contours as potential text regions.")

  # Filter and select potential text regions
  text_regions = []
  for c in cnts:
    # Filter based on area, aspect ratio, etc.
    if cv2.contourArea(c) > 100 and ...:  # Define filtering criteria
      text_regions.append(c)

  return image, text_regions


# 2. Text Extraction and Cleaning (Combine Steps):
import pytesseract
import re
import logging

def extract_and_clean_text(image, region):
  # Extract ROI (Region of Interest) based on the contour
  x, y, w, h = cv2.boundingRect(region)
  roi = image[y:y+h, x:x+w]

  try:
    # Perform OCR with PyTesseract
    text = pytesseract.image_to_string(roi, config='--psm 6')  # Adjust config as needed
    text = text.strip()
  except Exception as e:
    logging.error(f"Error during OCR for region: {e}")
    return ""

  # Clean the extracted text
  clean_text = re.sub(r'[^\w\s\.,-]', '', text)  # Replace non-alphanumeric with space
  clean_text = re.sub(r'\s+', ' ', clean_text)  # Collapse multiple spaces
  clean_text = clean_text.lower()  # Convert to lowercase
  return clean_text



# 3. Data Preprocessing (Tokenization and Label Encoding):

from transformers import BertTokenizer

def prepare_data(data):
  tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Adjust model name

  # Define function to process a single invoice (text, labels)
  def process_invoice(text, labels):
    # Tokenize the text
    encoded_text = tokenizer(text, padding='max_length', truncation=True)

    # Encode labels (replace with your label encoding logic)
    encoded_labels = [entity_labels.index(label) for label in labels]

    return encoded_text['input_ids'], encoded_text['attention_mask'], encoded_labels

  # Process all invoices in the data
  encoded_data = []
  for text, labels in data:
    encoded_data.append(process_invoice(text, labels))

  return encoded_data

# Example usage
training_data = [(extract_and_clean_text(image, region), entity_annotations) for image, regions in training_images for region in regions]
encoded_training_data = prepare_data(training_data)

# Similar logic for validation and test data



from transformers import TFBertForTokenClassification
from tensorflow.keras.metrics import Precision, Recall, F1Score
import tensorflow as tf

# Define custom entity labels (modify as needed)
entity_labels = ['O', 'PATIENT_NAME', 'MEDICATION', 'DOSAGE', 'DOCTOR_NOTE']

# Load pre-trained BERT model (e.g., BioBERT)
model_name = 'bert-base-uncased'
model = TFBertForTokenClassification.from_pretrained(model_name, num_labels=len(entity_labels))


# 4. NER Model (TensorFlow) - Metrics, Logging, and Storing Results:
# Prepare training data (preprocessing, tokenization, label encoding)
encoded_training_data = prepare_data(training_data)
# Similar logic for validation and test data

# Define custom metrics callback (example)
class NERMetrics(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs=None):
    precision_metric = Precision(name='precision')
    recall_metric = Recall(name='recall')
    f1_metric = F1Score(name='f1_score')

    # Calculate metrics for each entity label
    for label in entity_labels[1:]:  # Skip 'O' label
      y_true = self.model.validation_data[1][:, 1:]
