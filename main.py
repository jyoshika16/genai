from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os
from google import genai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Gemini client
client = genai.Client(api_key="your api key")

def extract_text_from_pdf(pdf_path):
    extracted_text = ""

    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text

    return extracted_text


@app.route("/", methods=["GET", "POST"])
def index():
    ats_score = None

    if request.method == "POST":
        pdf_file = request.files["resume"]

        if pdf_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
            pdf_file.save(file_path)

            extracted_text = extract_text_from_pdf(file_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Here is my resume text:
{extracted_text}

Question:
Give an approximate ATS score out of 100 and a short reason.
"""
            )

            ats_score = response.text

    return render_template("index.html", ats_score=ats_score)


if __name__ == "__main__":
    app.run(debug=True)
