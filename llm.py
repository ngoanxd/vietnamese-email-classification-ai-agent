import torch 
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.load_state_dict(
    torch.load(MODEL_PATH, map_location=device)
)

model.eval()