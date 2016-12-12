import os, subprocess
from flask import Flask, flash, render_template, request, redirect, url_for, send_file, Response
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags

app = Flask(__name__)
app.debug=True

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUT_FOLDER'] = 'out'
app.config['FILTER'] = 'filters/filter_3.png'
app.config['SCRIPT'] = 'scripts/encode.py'
app.secret_key ='asdlkjfho2837hlfbvhzv8o7n3af'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash("No file uploaded", "Error")
            return render_template("home.html.jinja")
        f = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if f.filename == '':
            flash("Nonexistent file", "Error")
            return render_template("home.html.jinja")

        path = secure_filename(f.filename)
        fname = ''.join(path.split('.')[:-1])
        f.save(path)
        result = subprocess.call(['python', app.config['SCRIPT'], path])

        if result:
            flash("Conversion failed...", "Error")
            return render_template("home.html.jinja")

        outzip = app.config['OUT_FOLDER'] + '/' + fname + '.zip'
        subprocess.call(['zip', '-r', outzip, os.path.join(app.config['OUT_FOLDER'], fname)])

        return send_file(outzip, attachment_filename=outzip, as_attachment=True)
    return render_template("home.html.jinja")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
