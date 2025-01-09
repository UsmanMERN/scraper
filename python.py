import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
nltk.download("all")

text = "NLTK is a powerful library for natural language processing."
words = word_tokenize(text)
sentences = sent_tokenize(text)

print(words)
print(sentences)