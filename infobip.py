from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, json
import os, pandas as pd, shutil, gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv  # Для загрузки переменных из .env файла
from functions import upload_files, unzip_files, search_report, delete_files  # Функции из файла functions.py


load_dotenv()  # Загружаем переменные из файла .env
infobip = Blueprint('infobip', __name__, template_folder="templates")
upload_folder = "uploads"  # Папка для загрузки файлов
file_day = 'КПД ММ УР.csv'
file_night = 'Час 0-1 ММ Самокат.csv'


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


@infobip.route("/upload", methods=['POST', 'GET'])
def ib():
    if request.method == 'POST':
        upload_files()
        unzip_files()
        return redirect(url_for("infobip.result"))
    return render_template("infobip.html")


@infobip.route("/result")
def result():
    report = search_report()  # Ищем отчет в папке

    # Считаем часы по выгрузке из бипа  
    day_hours = read_file(file_day)
    night_hours = read_file(file_night)

    # Соединяем ночные и дневные часы
    all_hours = pd.concat([day_hours, night_hours], axis=0)
    all_hours['1 Hour Time Window'] = all_hours['1 Hour Time Window'].str.replace('Стажер ', '')   # Удаляем слово "Стажер " из значений столбца "1 Hour Time Window"

    #reset_index() - Создаем новые индексы, чтобы столбец Agent name стал столбцом, а не индексацией:
    all_hours = all_hours.groupby(['1 Hour Time Window']).sum().reset_index()  # Группируем по фамилии и суммируем часы(ночь и день)
    all_hours.rename(columns={'1 Hour Time Window': 'Agent Name'}, inplace=True)  # Переименовываем столбец

    # Считаем чаты по отчету из бипа
    chats = pd.read_csv(os.path.join(upload_folder, report))
    chats = chats.loc[chats['Agent Name'].str.contains(' ММ')]  # Оставлем только тех, у кого имя заканчивается на " ММ"
    chats['Agent Name'] = chats['Agent Name'].str.replace('Стажер ', '')   # Удаляем слово "Стажер " из значений столбца 'Agent Name'

    chats = chats[['Agent Name', 'Conversation ID']]  # Оставляем только нужные столбцы
    #reset_index() - Создаем новые индексы, чтобы столбец Agent name стал столбцом, а не индексацией:
    chats = chats.groupby(['Agent Name']).count().reset_index()  # Считаем кол-во повторений каждой фамилии

    # Объединяем таблицы и считаем кпд
    all_hours = all_hours.merge(chats, how='left', on='Agent Name')  # Объединяем Agent name и Chats в одну таблицу
    all_hours['kpd'] = all_hours['Conversation ID'] / all_hours['Hours']  # КПД = кол-во чатов / кол-во часов

    all_hours = all_hours.dropna(subset=['kpd'])  # Удаляем строки без значения
    all_hours = all_hours.drop(columns=['Hours'])  # Удаляем столбец "Hours"

    all_hours['kpd'] = all_hours['kpd'].round().astype(int)  # Округляем числа до целых
    all_hours = all_hours[all_hours['kpd'] > 0]  # Удаляем нули
    all_hours = all_hours[['Agent Name', 'kpd']]

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
    
    # creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)  # credentials.json - скаченные данные с Google Cloud
    client = gspread.authorize(creds)

    sheet_id = os.getenv('SHEET_ID') # id таблицы
    workbook = client.open_by_key(sheet_id) # Вся таблица
    sheet = workbook.worksheet('КПД')  # Лист в таблице

    sheet.batch_clear(['D74:E102'])  # Очищаем два первых столбца
    set_with_dataframe(sheet, all_hours, row=73, col=4)  # Выгружаем данные в Google sheet

    delete_files()  # Удаляем файлы

    return redirect(url_for('home'))
