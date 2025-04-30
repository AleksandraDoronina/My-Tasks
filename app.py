from distutils.log import debug
from fileinput import filename
import pandas as pd
import numpy as np
from flask import *
import os
from werkzeug.utils import secure_filename

# UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
UPLOAD_FOLDER = os.path.join('/')

# Define allowed files
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)

# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'This is your secret key to utilize session in Flask'

count = 0


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # upload file flask
        f = request.files.get('file')

        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)

        f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            data_filename))

        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'],
                                                          data_filename)

        global count
        if not os.path.isfile("interim_results.csv"):
            open("interim_results.csv", "x").close()
            pd.DataFrame([[]]).to_csv("interim_results.csv", index_label=False)
        elif count == 0:
            os.remove("interim_results.csv")
            open("interim_results.csv", "x").close()
            pd.DataFrame([[]]).to_csv("interim_results.csv", index_label=False)
        count += 1
        return render_template('index2.html')
    return render_template("index.html")


@app.route('/add_new_file')
def add_new_file():
    return render_template("index3.html")


@app.route('/show_data')
def show_data():
    # Uploaded File Path

    data_file_path = session.get('uploaded_data_file_path', None)
    # read txt
    file = open(data_file_path, "r")
    uploaded_ds = pd.read_csv("interim_results.csv")
    content = file.read()
    content = content.lower().split(r' ')
    computing = {word: content.count(word) for word in set(content)}
    current_df = pd.DataFrame()
    current_df['слово'] = list(computing.keys())
    current_df['tf, сколько раз это слово встречается в тексте'] = list(computing.values())

    current_df['слово'] = current_df['слово'].str.replace(r'\W', '')
    current_df['количество документов'] = 1
    if len(uploaded_ds) != 0:
        uploaded_ds.loc[uploaded_ds['слово'].isin(content), 'количество документов'] += 1
        current_df['всего документов'] = uploaded_ds['всего документов'].unique()[0] + 1
        # diff = current_df[~current_df['слово'].isin(uploaded_ds['слово'])][['слово', 'количество документов']]
        diff = current_df[~current_df['слово'].isin(uploaded_ds['слово'])]
        uploaded_ds = pd.concat([uploaded_ds, diff], join='inner', ignore_index=True)
        uploaded_ds['всего документов'].fillna(0)
        uploaded_ds['всего документов'] += 1
    else:
        uploaded_ds = pd.DataFrame()
        uploaded_ds['слово'] = current_df['слово']
        uploaded_ds['количество документов'] = 1
        uploaded_ds['всего документов'] = 1
        current_df['всего документов'] = uploaded_ds['всего документов']

    print(current_df['tf, сколько раз это слово встречается в тексте'])
    print(current_df['слово'])
    print(current_df['количество документов'])
    print(current_df['количество документов'])

    print(uploaded_ds['слово'])
    print(uploaded_ds['количество документов'])
    print(uploaded_ds['всего документов'])

    docs_no = uploaded_ds['всего документов'].unique()[0]
    idf_column = uploaded_ds['количество документов'].apply(lambda x: np.log(docs_no / x)).reset_index(drop=True)
    current_df['idf, обратная частота документа'] = idf_column
    print(current_df)
    current_df = current_df.sort_values(by=['idf, обратная частота документа'],
                                        ascending=False)
    current_df = current_df[['слово',
                             'tf, сколько раз это слово встречается в тексте',
                             'idf, обратная частота документа']][:50].reset_index(drop=True)
    uploaded_df_html = current_df.to_html()
    print(uploaded_ds.columns)
    uploaded_ds.to_csv("interim_results.csv", index=False)
    return render_template('show_csv_data.html',
                           data_var=uploaded_df_html)


@app.route('/stop_process')
def stop_process():
    if os.path.isfile("interim_results.csv"):
        os.remove("interim_results.csv")
    return render_template('stop_process.html')


if __name__ == '__main__':
    app.run(debug=True)
