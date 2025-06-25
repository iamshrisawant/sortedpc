# models/learner/trainer.py

from models.learner.preprocessor import build_features_and_labels
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import numpy as np

def train_model():
    X, y, label_encoder = build_features_and_labels()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("[RESULT] Classification Report:\n")
    all_class_indices = np.arange(len(label_encoder.classes_))  # Ensures all known classes are listed
    print(classification_report(
        y_test,
        y_pred,
        labels=all_class_indices,
        target_names=label_encoder.classes_,
        zero_division=0  # Avoid division by zero warnings for missing classes
    ))

    joblib.dump(model, "models/learner/xgb_model.joblib")
    joblib.dump(label_encoder, "models/learner/label_encoder.joblib")

    print("[SUCCESS] Model saved as xgb_model.joblib")
    print("[SUCCESS] Label encoder saved as label_encoder.joblib")

if __name__ == "__main__":
    train_model()
    print("[INFO] Training process completed successfully.")
