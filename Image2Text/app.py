import cv2
import logging

def preprocess_invoice(image_path):
  # Read image
  image = cv2.imread(image_path)

  # Convert to grayscale and apply thresholding
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

  # Find contours (potential text regions)
  cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

  logging.info(f"Found {len(cnts)} contours as potential text regions.")

  # Filter and select potential text regions
  text_regions = []
  for c in cnts:
    # Filter based on area, aspect ratio, etc.
    if cv2.contourArea(c) > 100 and ...:  # Define filtering criteria
      text_regions.append(c)

  return image, text_regions

import pytesseract
import logging

def extract_text(image, region):
  # Extract ROI (Region of Interest) based on the contour
  x, y, w, h = cv2.boundingRect(region)
  roi = image[y:y+h, x:x+w]

  try:
    # Perform OCR with PyTesseract
    text = pytesseract.image_to_string(roi, config='--psm 6')  # Adjust config as needed
    return text.strip()
  except Exception as e:
    logging.error(f"Error during OCR for region: {e}")
    return ""


import re

def clean_text(text):
  # Remove unnecessary characters, line breaks, etc.
  text = re.sub(r'[^\w\s\.,-]', '', text)  # Replace non-alphanumeric with space
  text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
  return text.lower()  # Convert to lowercase



from transformers import TFBertForTokenClassification

# Define custom entity labels (modify as needed)
entity_labels = ['O', 'PATIENT_NAME', 'MEDICATION', 'DOSAGE', 'DOCTOR_NOTE']

# Load pre-trained BERT model (e.g., BioBERT)
model_name = 'bert-base-uncased'
model = TFBertForTokenClassification.from_pretrained(model_name, num_labels=len(entity_labels))

# Prepare training data (preprocessing, tokenization, label encoding)
# ... (refer to TensorFlow tutorials for data preparation)

# Train the model
# ... (refer to TensorFlow tutorials for model training)

def predict_entities(text):
  # Tokenize the text and prepare input for the model
  inputs = ...  # Refer to TensorFlow BERT tokenization examples

  # Make predictions
  with tf.Session() as sess:
    logits = model(inputs)[0]
    predictions = tf.argmax(logits, axis=-1).numpy()

  # Map predictions to entity labels
  entities = []
  for i, pred in enumerate(predictions):
    if pred != 0:  # Ignore padding label
      entities.append((text.split()[i], entity_labels[pred]))
  return entities

from transformers import TFBertForTokenClassification
from tensorflow.keras.metrics import Precision, Recall, F1Score

# Define custom entity labels (modify as needed)
entity_labels = ['O', 'PATIENT_NAME', 'MEDICATION', 'DOSAGE', 'DOCTOR_NOTE']

# Load pre-trained BERT model (e.g., BioBERT)
model_name = 'bert-base-uncased'
model = TFBertForTokenClassification.from_pretrained(model_name, num_labels=len(entity_labels))

# Prepare training data (preprocessing, tokenization, label encoding)
# ... (refer to TensorFlow tutorials for data preparation)

# Define custom metrics callback (example)
class NERMetrics(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs=None):
    precision_metric = Precision(name='precision')
    recall_metric = Recall(name='recall')
    f1_metric = F1Score(name='f1_score')

    # Calculate metrics for each entity label
    for label in entity_labels[1:]:  # Skip 'O' label
      y_true = self.model.validation_data[1][:, 1:]  # Extract true labels (ignore padding)
      y_pred = np.argmax(self.model.predict(self.model.validation_data[0])[0], axis=-1)
      precision = precision_metric(y_true[:, entity_labels.index(label)], y_pred)
      recall = recall_metric(y_true[:, entity_labels.index(label)], y_pred)
      f1 = f1_metric(y_true[:, entity_labels.index(label)], y_pred)

      logging.info(f"Epoch {epoch+1}: Entity '{label}' - Precision: {precision.numpy():.4f}, Recall: {recall.numpy():.4f}, F1-Score: {f1.numpy():.4f}")

# Train the model with custom metrics callback
model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True))
model.fit(training_data, epochs=10, validation_data=validation_data, callbacks=[NERMetrics()])

def predict_entities(text):
  # Tokenize the text and prepare input for the model
  inputs = ...  # Refer to TensorFlow BERT tokenization examples

  # Make predictions
  with tf.Session() as sess:
    logits = model(inputs)[0]
    predictions = tf.argmax(logits, axis=-1).numpy()

  # Map predictions to entity labels
  entities = []
  for i, pred in enumerate(predictions):
    if pred

