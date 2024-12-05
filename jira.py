from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import os, pandas as pd, shutil, gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from functions import upload_files, unzip_files, search_report, delete_files  # Функции из файла functions.py


jira = Blueprint('jira', __name__, template_folder="templates")
upload_folder = "uploads"  # Папка для загрузки файлов
file_day = 'Время в статусе Доп_ Канал.csv'


def read_file(file):
    df = pd.read_csv(os.path.join(upload_folder, file))
    # Преобразуем значения в числовой формат перед суммированием
    for col in df.columns[1:]:  # Пропускаем первый столбец
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Суммируем все цифры в столбцах с 03 по 23 и записываем в столбец Total
    df['Hours'] = df.iloc[:, 1:].sum(axis=1)

    df = df[['1 Hour Time Window', 'Hours']]

    # Оставляем только строки, где в столбце '1 Hour Time Window' есть ' ММ'
    df = df.loc[df['1 Hour Time Window'].str.contains(' ММ')]

    df['Hours'] = df['Hours'] / 3600
    return df


@jira.route("/upload", methods=['POST', 'GET'])
def jra():
    if request.method == 'POST':
        upload_files()
        unzip_files()
        flash("КПД Jira посчитано успешно!", "success")
        return redirect(url_for("jira.result"))
    return render_template("jira.html")


@jira.route("/result")
def result():
    report = search_report()  # Ищем отчет в папке
    d_names = pd.read_csv('d_names.csv')  # Читаем список имен-никнеймов

    all_hours = read_file(file_day)
    all_hours.rename(columns={'1 Hour Time Window': 'Имя'}, inplace=True)  # Меняем имя столбца

    chats = pd.read_csv(os.path.join(upload_folder, report))
    chats = chats[['Исполнитель', 'Приоритет']]
    chats.rename(columns={'Приоритет': 'Чаты'}, inplace=True)  # Меняем имя столбца

    chats = chats.groupby(['Исполнитель'], as_index=False).count()

    chats = pd.merge(chats, d_names, how="left", on='Исполнитель')
    chats = pd.merge(chats, all_hours, how="left", on='Имя')

    chats['KPD'] = chats['Чаты'] / chats['Hours']
    chats = chats.dropna(subset=['KPD'])  # Удаляем строки без значения

    chats['KPD'] = chats['KPD'].round().astype(int)  # Округляем числа до целых
    chats = chats[chats['KPD'] > 0]  # Удаляем нули

    chats = chats[['Имя', 'KPD']]


    # Экспорт в Google sheets

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    
    # Получаем данные из переменных окружения
    credentials = {
       'type': os.getenv('GOOGLE_TYPE'),
       'project_id': os.getenv('GOOGLE_PROJECT_ID'),
       'private_key_id': os.getenv('GOOGLE_PRIVATE_KEY_ID'),
       'private_key': os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),  # Заменяем \n на новую строку
       'client_email': os.getenv('GOOGLE_CLIENT_EMAIL'),
       'client_id': os.getenv('GOOGLE_CLIENT_ID'),
       'auth_uri': os.getenv('GOOGLE_AUTH_URI'),
       'token_uri': os.getenv('GOOGLE_TOKEN_URI'),
       'auth_provider_x509_cert_url': os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL'),
       'client_x509_cert_url': os.getenv('GOOGLE_CLIENT_CERT_URL'),
       'universe_domain': 'googleapis.com'
    }

    creds = Credentials.from_service_account_info(credentials, scopes=scopes)
    
    # creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)  # credentials.json - скаченные данные с Google Cloud    client = gspread.authorize(creds)
    client = gspread.authorize(creds)
    sheet_id = os.getenv('SHEET_ID') # id таблицы
    workbook = client.open_by_key(sheet_id) # Вся таблица
    sheet = workbook.worksheet("КПД")  # Лист в таблице

    sheet.batch_clear(['I73:J102'])  # Очищаем два первых столбца
    set_with_dataframe(sheet, chats, row=73, col=9)  # Выгружаем данные в Google sheet

    delete_files()

    return redirect(url_for("home"))
