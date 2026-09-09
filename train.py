import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
 
ARTIFACT_DIR = "artifacts"
 
 
def load_arrays():
    X_train = np.load(os.path.join(ARTIFACT_DIR, "X_train.npy"))
    X_test = np.load(os.path.join(ARTIFACT_DIR, "X_test.npy"))
    y_train = np.load(os.path.join(ARTIFACT_DIR, "y_train.npy"))
    y_test = np.load(os.path.join(ARTIFACT_DIR, "y_test.npy"))
    return X_train, X_test, y_train, y_test
 
 
def train():
    X_train, X_test, y_train, y_test = load_arrays()
 
    print("Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)
 
    y_pred = model.predict(X_test)
 
    print("\n=== Evaluation on held-out test set ===")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification report (0=normal, 1=attack):")
    print(classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix:")
    print("             pred normal  pred attack")
    cm = confusion_matrix(y_test, y_pred)
    print(f"true normal   {cm[0][0]:>10}  {cm[0][1]:>12}")
    print(f"true attack   {cm[1][0]:>10}  {cm[1][1]:>12}")
 
    model_path = os.path.join(ARTIFACT_DIR, "model.joblib")
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")
 
 
if __name__ == "__main__":
    train()
 