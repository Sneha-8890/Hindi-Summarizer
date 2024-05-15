from flask import Flask, render_template, request, redirect, url_for
import os
import requests
from bs4 import BeautifulSoup
import pdfplumber
import json
from Rough import rough

app = Flask(__name__)

# Define the path where the uploaded text will be stored
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploaded_files')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
PARAMS = {"key": "AIzaSyA9iu_23l4DwxwJ_NfzeY0jkQISS1Vi2SI"}
uploaded_text = ""

def abstractive(text, num):
    words = (len(text.split(" "))*num)//100
    print(len(text), words, sep = " ")
    text = text + "remove English or other languages and summarize it in " + str(words) + "words in Hindi in an abstractive manner"
    data = {"contents": [
        {"role": "user",
         "parts": [{"text": text}]}]}
    r = requests.post(url=URL, params=PARAMS, json=data)
    ans = json.loads(r.text)['candidates'][0]['content']['parts'][0]['text']
    return ans

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            main_text = ""
            for paragraph in soup.find_all('p'):
                main_text += paragraph.text + '\n'
            return main_text.strip()
        else:
            return "Error: Unable to fetch URL"
    except Exception as e:
        return "Error: " + str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global uploaded_text
    upload_type = request.form['uploadType']
    extractive_summary = ""  # Initialize extractive summary variable
    if upload_type == 'text':
        uploaded_text = request.form['textInput']
        
    elif upload_type == 'pdf':
        pdf_file = request.files['fileInput']
        uploaded_text = extract_text_from_pdf(pdf_file)
        uploaded_text = uploaded_text + " remove other language words than Hindi and grammatically correct and reconstruct the scattered words"
        data = {"contents": [
            {"role": "user",
             "parts": [{"text": uploaded_text}]}]}
        r = requests.post(url=URL, params=PARAMS, json=data)
        uploaded_text = json.loads(r.text)['candidates'][0]['content']['parts'][0]['text']
    elif upload_type == 'url':
        url = request.form['urlInput']
        uploaded_text = extract_text_from_url(url)

    
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_text.txt'), 'w', encoding='utf-8') as file:
            file.write(uploaded_text)

    # Get the extractive summary
    import extractive

    summary_percent = int(request.form.get('summaryPercent', 100))  # Default to 100% if not provided

    abstractive_summary = abstractive(uploaded_text, summary_percent)
    extractive_summary = extractive.summary(uploaded_text, summary_percent)

    # Compute metrics for both summaries
    abstractive_precision, abstractive_recall, abstractive_fscore = rough(uploaded_text,abstractive_summary)
    extractive_precision, extractive_recall, extractive_fscore = rough(uploaded_text, extractive_summary)

    #return render_template('result.html', text=abstractive_summary, extractive_summary=extractive_summary)
    return render_template('result.html', text=abstractive_summary, extractive_summary=extractive_summary,
                           abstractive_precision=abstractive_precision, abstractive_recall=abstractive_recall,
                           abstractive_fscore=abstractive_fscore,
                           extractive_precision=extractive_precision, extractive_recall=extractive_recall,
                           extractive_fscore=extractive_fscore)
if __name__ == '__main__':
    app.run(debug=True)
