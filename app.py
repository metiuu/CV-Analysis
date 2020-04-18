#PDF Lib
import io
import pdfminer
from pdfminer.converter import *
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdevice import PDFDevice
import PyPDF2
import string

#Grammar & Spelling Lib
import pylanguagetool
import nltk
from spellchecker import SpellChecker

# Flask initialization
from flask import *
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#CORS
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template("home.html")


@app.route('/api/result', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        f = request.files['cvfile']
        sc = SpellChecker()
        shortened_words = []
        testList = list()
        text = extract_text_from_pdf(f)
        word_count = len(text.split())
        text_array = text.strip().split('\n')
        for i in range (len(text_array)):
            text_array[i] = "<p>" + text_array[i] + "</p>"

        #Spellchecking
        clonedList = text
        misspelled = sc.unknown(clonedList.split())
        for m in misspelled:
            shortened_words.append(reduce_lengthening(m))
        for s in range(len(shortened_words)):
            shortened_words[s] = sc.correction(shortened_words[s])

        text = Markup(''.join(text_array))
        return render_template("result.html", text=text, word_count = word_count, misspelled=misspelled, corrected=shortened_words)

def extract_text_from_pdf(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager,
                              fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
        page_interpreter.process_page(page)
    text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        #Omit a strange symbol and break the string to a new line
        return text.replace(text[-1], '\n')

def reduce_lengthening(text):
    pattern = re.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1",text)

if __name__ == '__main__':
    app.run(debug=True)