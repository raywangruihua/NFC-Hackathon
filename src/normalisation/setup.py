import nltk

downloads = [
    'punkt',
    'averaged_perceptron_tagger',
    'maxent_ne_chunker',
    'words',
    'stopwords'
]

for d in downloads:
    nltk.download(d)

print("✅ NLTK setup complete")