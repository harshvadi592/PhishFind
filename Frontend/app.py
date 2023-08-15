from flask import Flask, render_template, request
import joblib
import pandas as pd
from prediction.features import exportToDataSet

app = Flask("fake_website_identifier")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urlPage", methods=["GET"])
def urlPage():
    return render_template("urlPage.html", prediction=-1)


@app.route("/urlPage", methods=["POST"])
def submit():
    url = request.form["url"]
    exportToDataSet(url)

    knn = joblib.load("./prediction/knn.pkl")
    prediction_knn = knn.predict(pd.read_csv("test.csv"))

    svm = joblib.load("./prediction/svm.pkl")
    prediction_svm = svm.predict(pd.read_csv("test.csv"))

    forest = joblib.load("./prediction/forest.pkl")
    prediction_forest = forest.predict(pd.read_csv("test.csv"))

    tree = joblib.load("./prediction/tree.pkl")
    prediction_tree = tree.predict(pd.read_csv("test.csv"))

    cnn = joblib.load("./prediction/cnn.pkl")
    prediction_cnn = cnn.predict(pd.read_csv("test.csv"))

    rnn = joblib.load("./prediction/rnn.pkl")
    prediction_rnn = rnn.predict(pd.read_csv("test.csv"))

    lstm = joblib.load("./prediction/lstm.pkl")
    prediction_lstm = lstm.predict(pd.read_csv("test.csv"))

    if prediction_cnn[0][0] <= 0.5:
        prediction_cnn[0][0] = int(0)
    else:
        prediction_cnn[0][0] = int(1)

    if prediction_rnn[0][0] <= 0.5:
        prediction_rnn[0][0] = int(0)
    else:
        prediction_rnn[0][0] = int(1)

    if prediction_lstm[0][0] <= 0.5:
        prediction_lstm[0][0] = int(0)
    else:
        prediction_lstm[0][0] = int(1)

    prediction = (
        prediction_knn[0]
        + prediction_svm[0]
        + prediction_forest[0]
        + prediction_tree[0]
        + int(prediction_cnn[0][0])
        + int(prediction_rnn[0][0])
        + int(prediction_lstm[0][0])
    )

    print(prediction)

    prediction = int(prediction / 4)

    print(prediction)

    return render_template("urlPage.html", prediction=prediction, url=url)


# app.run(debug=False, host="0.0.0.0")
app.run(debug=False)
