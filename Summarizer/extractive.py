import re
import math
from collections import defaultdict


def preprocess_text(text):
    text = re.sub(r'[\d\n,"()\'’:.?]', '', text)  # Clean text from unwanted characters
    sentences = text.split(u"।")
    sentences = [sentence.strip() + u"।" for sentence in sentences if sentence.strip()]  # Add full stop if missing
    return sentences


def remove_stopwords(sentences):
    with open("C:\\Users\\Tanuja\\OneDrive\\Documents\\Python Scripts\\Summarizer[1]\\Summarizer\\stopwords.txt", encoding="utf8") as f:
        stopwords = {line.strip() for line in f}
    tokens = []
    for sentence in sentences:
        words = sentence.split()
        filtered_words = [word for word in words if word not in stopwords]
        tokens.extend(filtered_words)
    return set(tokens)


def compute_sentence_values(tokens, sentences):
    freqTable = defaultdict(int)
    for word in tokens:
        freqTable[word] += 1

    sentenceValue = {}
    for sentence in sentences:
        for word in sentence.split():
            if word in freqTable:
                if sentence not in sentenceValue:
                    sentenceValue[sentence] = 0
                sentenceValue[sentence] += freqTable[word]

    max_value = max(sentenceValue.values(), default=1)
    min_value = max(sentenceValue.values(), default=0)
    if max_value==min_value:
        min_value=0
    for sentence in sentences:
        sentenceValue[sentence] = (sentenceValue[sentence]-min_value) / (max_value-min_value)
    return sentenceValue


def summary(text, percent_length):
    sentences = preprocess_text(text)
    tokens = remove_stopwords(sentences)
    sentenceValue = compute_sentence_values(tokens, sentences)
    ranked_sentences = sorted(sentenceValue.items(), key=lambda x: x[1], reverse=True)

    summary_length = int(len(sentences) * percent_length / 100)
    summary_sentences = [sentence for sentence, _ in ranked_sentences[:summary_length]]

    # Ensure each sentence ends with a full stop "।"
    final_summary = []
    for sentence in summary_sentences:
        if not sentence.endswith(u"।"):
            sentence += u"।"
        final_summary.append(sentence)

    summary = ' '.join(final_summary)

    return summary

