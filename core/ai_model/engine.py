import pandas as pd
import os
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'dataset.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'model_cache.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'vectorizer_cache.pkl')

class CivicAI:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.model_confidence = 0.0
        
        # Enhanced Priority Keywords with variations
        self.priority_keywords = {
            'High': [
                # Emergency/Life-threatening
                'fire', 'blast', 'explosion', 'spark', 'sparking', 'live wire', 'electric shock',
                'current', 'death', 'casualty', 'blood', 'murder', 'robbery', 'assault', 'attack',
                'gas leak', 'poison', 'poisoning', 'drowning', 'snatching', 'rape', 'molestation',
                'collapse', 'building collapse', 'dam break', 'flood', 'landslide',
                # Critical infrastructure
                'power outage', 'water shortage', 'sewage overflow', 'emergency', 'urgent'
            ],
            'Medium': [
                # Health & Sanitation
                'garbage', 'waste', 'smell', 'stench', 'odor', 'leak', 'leakage', 'sewage', 'stagnant',
                'mosquito', 'dengue', 'malaria', 'disease', 'infection', 'unhygienic', 'hygiene',
                # Infrastructure
                'jam', 'jammed', 'broken', 'damage', 'damaged', 'dirty', 'choked', 'blockage', 'blocked',
                'pothole', 'worn', 'deterioration', 'crack',
                # Traffic & Safety
                'traffic', 'congestion', 'vehicle', 'collision', 'stolen', 'theft', 'theft suspect',
                # Utilities
                'water supply', 'power supply', 'electricity', 'power'
            ],
            'Low': [
                # Maintenance
                'park', 'bench', 'grass', 'paint', 'painting', 'faded', 'poster', 'banner', 'banner posting',
                'cleaning', 'clean', 'leaves', 'parking', 'space', 'tree', 'trees', 'beautification',
                'light pole', 'street sign', 'road sign', 'marking', 'line marking',
                'minor', 'small', 'maintenance'
            ]
        }

        # Enhanced Department Keywords with variations
        self.dept_keywords = {
            'Electricity': [
                'light', 'pole', 'wire', 'current', 'power', 'meter', 'voltage', 'transformer', 'electric',
                'electricity', 'electrical', 'bulb', 'lamp', 'light bulb', 'street light', 'street lighting',
                'connection', 'electricity meter', 'electric pole', 'live wire', 'short circuit', 'tripping'
            ],
            'Water': [
                'water', 'pipe', 'tap', 'leakage', 'supply', 'tank', 'drain', 'drainage', 'sewer',
                'sewage', 'water supply', 'water line', 'water tank', 'leakage point', 'water meter'
            ],
            'Police': [
                'theft', 'robbery', 'fight', 'crime', 'traffic', 'signal', 'noise', 'stolen', 'police',
                'accident', 'law', 'order', 'security', 'unsafe', 'molestation', 'rape', 'assault',
                'helmet', 'seatbelt', 'traffic rule', 'drunk', 'speeding', 'rash driving'
            ],
            'PWD': [
                'road', 'pothole', 'bridge', 'street', 'divider', 'repair', 'pavement', 'concrete',
                'asphalt', 'sidewalk', 'footpath', 'ramp', 'slope', 'road condition', 'road repair',
                'manhole', 'street repair', 'road marking'
            ],
            'Health': [
                'mosquito', 'dengue', 'malaria', 'food', 'hospital', 'dog', 'stray', 'animal', 'medicine',
                'health', 'clinic', 'medical', 'disease', 'hygiene', 'sanitation', 'pest', 'rats',
                'expired', 'pharmacy', 'license', 'food safety', 'food poisoning'
            ],
            'Fire': [
                'fire', 'smoke', 'blast', 'cylinder', 'gas', 'lpg', 'explosion', 'burning', 'burn',
                'fire station', 'emergency', 'rescue'
            ],
            'Municipal': [
                'garbage', 'dustbin', 'cleaning', 'tree', 'park', 'encroachment', 'toilet', 'municipal',
                'waste', 'waste management', 'sweeping', 'collection', 'public', 'community',
                'park maintenance', 'green space', 'open dump', 'open dumping', 'encroachment removal'
            ]
        }

        # Load or train ML model
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Load cached model or train from scratch"""
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                with open(VECTORIZER_PATH, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("✅ AI Engine Loaded from Cache (Improved v2.0)")
            else:
                self._train_model()
        except Exception as e:
            print(f"⚠️ Cache Load Error: {e}, Training from scratch...")
            self._train_model()

    def _train_model(self):
        """Train model from dataset"""
        try:
            if not os.path.exists(CSV_PATH):
                print("⚠️ Dataset not found.")
                return

            # Read dataset
            self.data = pd.read_csv(CSV_PATH)
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(self.data['label'])
            
            # Build vectorizer with improved parameters
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                lowercase=True,
                stop_words='english',
                sublinear_tf=True
            )
            X = self.vectorizer.fit_transform(self.data['text'])
            
            # Train RandomForest (better than Naive Bayes for this use case)
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X, y)
            
            # Cache the model
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            with open(VECTORIZER_PATH, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            print("✅ AI Engine Trained & Cached (Improved v2.0)")
            print(f"   - TF-IDF Vectorizer: 5000 features, bigrams enabled")
            print(f"   - RandomForest: 100 trees, max_depth=20")
            print(f"   - Training samples: {len(self.data)}")
            
        except Exception as e:
            print(f"⚠️ Training Error: {e}")


    def predict(self, text, confidence_threshold=0.3):
        """
        Predict department and priority with confidence scoring
        
        Args:
            text: Complaint description
            confidence_threshold: Minimum confidence for ML prediction (0.0-1.0)
        
        Returns:
            tuple: (predicted_dept, predicted_prio, confidence_score)
        """
        text_lower = text.lower()
        predicted_dept = "Municipal"  # Default
        predicted_prio = "Low"        # Default
        confidence = 0.0
        
        # 1. PRIORITY DETECTION (Keyword-based - highest accuracy)
        for word in self.priority_keywords['High']:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                predicted_prio = "High"
                break
        
        if predicted_prio == "Low":  # If not High, check Medium
            for word in self.priority_keywords['Medium']:
                if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                    predicted_prio = "Medium"
                    break
        
        # 2. ML-BASED DEPARTMENT DETECTION with confidence scoring
        ml_dept = None
        ml_confidence = 0.0
        
        if self.model and self.vectorizer and self.label_encoder:
            try:
                X = self.vectorizer.transform([text])
                probabilities = self.model.predict_proba(X)[0]
                max_prob_idx = probabilities.argmax()
                ml_confidence = probabilities[max_prob_idx]
                
                if ml_confidence >= confidence_threshold:
                    ml_dept = self.label_encoder.inverse_transform([max_prob_idx])[0]
                    confidence = ml_confidence
                    
                    # Map dataset names to system names
                    dept_mapping = {
                        'Municipality': 'Municipal',
                        'Electricity': 'Electricity',
                        'Water': 'Water',
                        'Police/Traffic': 'Police',
                        'Police': 'Police',
                        'PWD': 'PWD',
                        'Health': 'Health',
                        'Health Department': 'Health',
                        'Fire': 'Fire',
                        'Municipal': 'Municipal'
                    }
                    predicted_dept = dept_mapping.get(ml_dept, "Municipal")
            except Exception as e:
                pass  # Fall back to keyword matching
        
        # 3. FALLBACK KEYWORD CHECK (If ML didn't provide confident prediction)
        if ml_confidence < confidence_threshold:
            found_keyword = False
            for dept, keywords in self.dept_keywords.items():
                for word in keywords:
                    if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                        if not found_keyword:
                            predicted_dept = dept
                            found_keyword = True
                            confidence = 0.5  # Lower confidence for keyword match
                        break
                if found_keyword:
                    break
        
        return predicted_dept, predicted_prio, round(confidence, 3)

# Initialize AI bot
ai_bot = CivicAI()