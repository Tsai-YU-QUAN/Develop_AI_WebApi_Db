# @author: tsai tim

import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_bootstrap import Bootstrap
import pickle
import pyodbc
import logging
import numpy as np

app = Flask(__name__)
bootstrap = Bootstrap(app)

# read from AI Model, we must split Model data processing and Web API
model = pickle.load(open('irisModel.pkl', 'rb'))

baseFlower = ['setosa', 'versicolor', 'virginica']

# GUI
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        listData = []
        listData.append(request.values['sepal_length'])
        listData.append(request.values['sepal_width'])
        listData.append(request.values['petal_length'])
        listData.append(request.values['petal_width'])
        prediction = model.predict(np.array(listData).reshape(1, -1))
        str_prediction = baseFlower[int(prediction)]

        # insert into DBLog
        insertLogFile(str(request.values['sepal_length']), str(request.values['sepal_width']),
                      str(request.values['petal_length']), str(request.values['petal_width']), str_prediction)
        return render_template('index.html', pr_text='預測的花是 {}'.format(str_prediction))
    if request.method == 'GET':
        return render_template('index.html')

# API method(Input: File URL, Data list)
@app.route('/predict_api', methods=['POST'])
def predict_api():

    data = request.get_json(force=True)
    datalist = np.array(list(data.values()))
    prediction = model.predict([datalist])

    str_prediction = str(baseFlower[int(prediction)])

    # insert into DBLog
    insertLogFile(str(datalist[0]), str(datalist[1]),
                  str(datalist[2]), str(datalist[3]), str_prediction)
    # jsonify: 可回傳更小的Data Size,冒號,空白移除，回傳是: Content-Type: application/json
    return jsonify(str_prediction)


def insertLogFile(sepal_length, sepal_width, petal_length, petal_width, prediction):
    server = 'localhost\\SQLEXPRESS'
    database = 'AIrisData'
    username = 'username'
    password = 'password'

    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server +
                          ';DATABASE='+database+';UID='+username+';PWD=' + password)
    cursor = cnxn.cursor()

    cursor.execute("insert into LogFile(sepal_length, sepal_width, petal_length, petal_width, prediction) values (?, ?, ?, ?, ?)",
                   sepal_length, sepal_width, petal_length, petal_width, prediction)
    cnxn.commit()


if __name__ == "__main__":
    # run internal IP, EX: http://192.XX.XX.XX:5000/，but default is localhost
    app.run(debug=True, host='0.0.0.0')
