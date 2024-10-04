from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
from transformers import BartTokenizer, BartForConditionalGeneration
import os

app = Flask(__name__)
CORS(app)

model = BartForConditionalGeneration.from_pretrained('sshleifer/distilbart-cnn-12-6')
tokenizer = BartTokenizer.from_pretrained('sshleifer/distilbart-cnn-12-6')

@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    pdf_file = request.files['file']
    
    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    # Save the PDF temporarily
    pdf_path = os.path.join('temp', pdf_file.filename)
    pdf_file.save(pdf_path)

    extracted_text = ""
    total_pages = 0
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)  # Get total number of pages
            for page in pdf.pages:
                extracted_text += page.extract_text()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(pdf_path)

    if extracted_text:
        inputs = tokenizer([extracted_text], truncation=True, return_tensors='pt')
        input_length = inputs['input_ids'].shape[1]
        dynamic_max_length = max(56, int(input_length * 0.2))
        summary_ids = model.generate(inputs['input_ids'], num_beams=4, early_stopping=True, max_length=dynamic_max_length)
        summarized_text = [tokenizer.decode(g, skip_special_tokens=True) for g in summary_ids]
        summary = summarized_text[0]
    else:
        summary = "No text found in the PDF."

    return jsonify([{'summary': summary}])

if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(host='0.0.0.0', port=5000, debug=True)
