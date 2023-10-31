from flask import Flask, render_template, request, send_from_directory
from htmx_flask import Htmx

import os
import sys
# Add the path to the parent directory to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Logfile_Parser  # Assuming Logfile_Parser.py contains your log parsing code


app = Flask(__name__, template_folder='.')
htmx = Htmx(app)

@app.route('/')
def index():
    #log_files = os.listdir('../logs/')
    log_file_options = ['access', 'auth', 'error']
    return render_template('index.html', log_files=log_file_options)

#@app.route('/static/<path:path>')
#def send_static(path):
#    return send_from_directory('static', path)

@app.route('/static/htmx.min.js')
def send_htmx_js():
    return send_from_directory('static', 'htmx.min.js')

#@app.route('/upload', methods=['GET', 'POST'])
#def upload():
#    if request.method == 'POST':
#        log_file = request.files['log_file']
#        if log_file.filename != '':
#            log_file.save(os.path.join('../logs', log_file.filename))
#
#    return render_template('upload.html')

@app.route('/list_logs')
def list_logs():
    log_files = os.listdir('../logs')
    return render_template('list_logs.html', log_files=log_files)

@app.route('/parse_logs', methods=['POST'])
def parse_logs():
    log_file = request.form['log_file']
    args = Logfile_Parser.parseArguments(f'--basedir ../ --type {log_file} --column user --all'.split(" "))

    import io
    output_buffer = io.StringIO()
    sys.stdout = output_buffer
    Logfile_Parser.parseLogs(args)
    collected_output = output_buffer.getvalue()
    sys.stdout = sys.__stdout__

    return render_template('result.html', result=collected_output)

if __name__ == '__main__':
    app.run(debug=True)
