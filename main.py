from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, pandas as pd, shutil
from infobip import infobip
from jira import jira
from tech import tech
from teamleader import teamleader


app = Flask(__name__)
app.register_blueprint(infobip, url_prefix="/infobip")  # Ссылаемся на файл инфобипа
app.register_blueprint(jira, url_prefix="/jira")  # Ссылаемся на файл инфобипа
app.register_blueprint(tech, url_prefix="/tech")  # Ссылаемся на файл инфобипа
app.register_blueprint(teamleader, url_prefix="/teamleader")  # Ссылаемся на файл инфобипа
upload_folder = "uploads"  # Папка для загрузки файлов
app.config['UPLOAD_FOLDER'] = upload_folder  # Добавляем адрес папки в конфигурацию flask-приложения


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)  # Запуск
