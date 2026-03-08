

# Load model directly
import torch
import torch.nn.functional as F

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Load Model ───────────────────────────────────────────────────────────────
# Downloads FinBERT from HuggingFace on first run, then caches locally.
# Fine-tuned on financial news to classify sentiment.
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
model.eval()

# LABELS = {0: 'positive', 1: 'negative', 2: 'neutral'}
# Maps the model's output index to a human-readable sentiment string
LABELS = model.config.id2label  # {0: 'positive', 1: 'negative', 2: 'neutral'}

# ── Label Remap ───────────────────────────────────────────────────────────────
# Translates FinBERT's sentiment labels into risk appetite language:
#   positive news → investors take on risk  → risk-on
#   negative news → investors flee to safety → risk-off
#   neutral news  → no clear signal          → neutral
SCALAR_MAP = {
    "positive": 'risk-on',
    "negative": 'risk-off',
    "neutral":  'neutral'
}

def predict_scalar(texts: list[str], batch_size: int):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True,
                           max_length=512, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1)
        for prob in probs:
            raw_label = LABELS[prob.argmax().item()]
            results.append(SCALAR_MAP[raw_label])
    return results

def predict_one(text: str) -> str:
    """Returns 'risk-on', 'risk-off', or 'neutral' for a single text."""
    inputs = tokenizer(text, padding=True, truncation=True,
                       max_length=512, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1)
    raw_label = LABELS[probs.argmax().item()]
    return SCALAR_MAP[raw_label]