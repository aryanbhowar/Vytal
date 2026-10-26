"""Train the heart model. Usage: .venv\\Scripts\\python.exe -m ml.training.heart_model_training"""

from ml.training.train_binary_risk_model import train_and_save

if __name__ == "__main__":
    train_and_save("heart")
