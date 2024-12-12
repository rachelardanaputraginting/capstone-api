import os
import re
import logging
import numpy as np
import pickle
import nltk

from tensorflow.keras.preprocessing.sequence import pad_sequences
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import tensorflow as tf

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure NLTK resources are downloaded
def ensure_nltk_resources():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')

ensure_nltk_resources()

class EmergencyCaseClassifier:
    def __init__(self, base_path=None):
        """
        Initialize the classifier with optional base path for model files
        
        :param base_path: Base directory for model files. If None, uses the current directory
        """
        logging.info("Initializing EmergencyCaseClassifier...")

        # Determine base path
        if base_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Construct full paths to model files
        self.model_path = os.path.join(base_path, 'models/emergency_case_model.h5')
        self.tokenizer_path = os.path.join(base_path, 'models/tokenizer.pickle')
        self.label_encoder_path = os.path.join(base_path, 'models/label_encoder.pickle')
        
        # Validate file existence
        self._validate_files()
        
        # Initialize preprocessing components
        self._init_preprocessing()
        
        # Load machine learning components
        self._load_ml_components()

    def _validate_files(self):
        """Check if all required model files exist"""
        files_to_check = [
            self.model_path, 
            self.tokenizer_path, 
            self.label_encoder_path
        ]
        
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required model file not found: {file_path}")
        logging.info("All required model files found.")

    def _init_preprocessing(self):
        """Initialize text preprocessing components"""
        logging.info("Initializing text preprocessing components...")

        # Stemmer
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        
        # Stopwords
        self.stop_words = set(stopwords.words('indonesian'))
        
        # Custom stopwords to keep
        custom_stopwords = {"tidak", "kecil", "besar"}
        self.stop_words = self.stop_words - custom_stopwords
        
        # Maximum sequence length for padding
        self.MAX_SEQUENCE_LENGTH = 100
        logging.info("Text preprocessing components initialized.")

    def _load_ml_components(self):
        """Load machine learning model and encoders"""
        logging.info("Loading machine learning components...")

        try:
            # Load LSTM model
            self.model = tf.keras.models.load_model(self.model_path)
            
            # Load tokenizer
            with open(self.tokenizer_path, 'rb') as handle:
                self.tokenizer = pickle.load(handle)
            
            # Load label encoder
            with open(self.label_encoder_path, 'rb') as handle:
                self.label_encoder = pickle.load(handle)
            logging.info("Machine learning components loaded successfully.")

        except Exception as e:
            raise RuntimeError(f"Error loading machine learning components: {e}")

    def preprocess_text(self, text):
        """
        Preprocess input text
        
        :param text: Input text to preprocess
        :return: Preprocessed tokens
        """
        logging.info("Preprocessing text...")

        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[\^\w\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [word for word in tokens if word not in self.stop_words]
        
        # Stem tokens
        tokens = [self.stemmer.stem(word) for word in tokens]

        logging.info("Text preprocessing completed.")
        return tokens

    def predict(self, text):
        """
        Predict emergency case label for given text
        
        :param text: Input text to classify
        :return: Predicted label
        """
        if not text.strip():
            raise ValueError("Input text is empty.")

        try:
            logging.info("Predicting emergency case...")
            
            # Preprocess text
            tokens = self.preprocess_text(text)
            
            # Convert to sequence
            sequence = self.tokenizer.texts_to_sequences([tokens])
            
            # Pad sequence
            padded = pad_sequences(sequence, padding='post', maxlen=self.MAX_SEQUENCE_LENGTH)
            
            # Predict
            prediction = self.model.predict(padded)
            
            # Get predicted index
            predicted_index = np.argmax(prediction, axis=1)
            
            # Return label
            label = self.label_encoder.inverse_transform(predicted_index)[0]
            logging.info(f"Prediction completed. Predicted label: {label}")
            return label

        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            raise RuntimeError(f"Prediction error: {e}")

# Create a singleton instance
try:
    emergency_classifier = EmergencyCaseClassifier()
except Exception as e:
    logging.error(f"Failed to initialize EmergencyCaseClassifier: {e}")
    raise

def predict_emergency_case(text):
    """
    Convenience function to predict emergency case label
    
    :param text: Input text to classify
    :return: Predicted label
    """
    return emergency_classifier.predict(text)
