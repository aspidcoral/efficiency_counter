from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import os, pandas as pd, shutil, gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from functions import upload_files, unzip_files, search_report, delete_files  # Функции из файла functions.py

teamleader = Blueprint('teamleader', __name__, template_folder="templates")
upload_folder = "uploads"  # Папка для загрузки файлов
file_day = 'КПД ТЛ время.csv'


def read_file(file):
    df = pd.read_csv(os.path.join(upload_folder, file))
    # Преобразуем значения в числовой формат перед суммированием
    for col in df.columns[1:]:  # Пропускаем первый столбец
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Суммируем все цифры в столбцах с 03 по 23 и записываем в столбец Total
    df['Hours'] = df.iloc[:, 1:].sum(axis=1)

    df = df[['1 Hour Time Window', 'Hours']]

    # Оставляем только строки, где в столбце '1 Hour Time Window' есть ' ММ'
    df = df.loc[df['1 Hour Time Window'].str.contains(' Тимлидер')]

    df['Hours'] = df['Hours'] / 3600
    return df


@teamleader.route("/upload", methods=['POST', 'GET'])
def tl():
    if request.method == 'POST':
        upload_files()
        unzip_files()
        return redirect(url_for("teamleader.result"))
    return render_template("teamleader.html")


@teamleader.route("/result")
def result():
    report = search_report()  # Ищем отчет в папке

    # Считаем часы по выгрузке из бипа 
    all_hours = read_file(file_day)  # Читаем файл
    all_hours.rename(columns={'1 Hour Time Window': 'Agent Name'}, inplace=True)  # Переименовываем столбец


    # Считаем чаты по отчету из бипа
    chats = pd.read_csv(os.path.join(upload_folder, report))  # Читаем файл
    chats = chats.loc[chats['Agent Name'].str.contains(' Тимлидер', case=False)]  # Оставлем только тех, у кого имя заканчивается на " Тимлидер"

    chats = chats[['Agent Name', 'Conversation ID']]  # Оставляем только нужные столбцы
    #reset_index() - Создаем новые индексы, чтобы столбец Agent name стал столбцом, а не индексацией:
    chats = chats.groupby(['Agent Name']).count().reset_index()   # Считаем кол-во повторений каждой фамилии

    # Объединяем таблицы и считаем кпд
    all_hours = all_hours.merge(chats, how='left', on='Agent Name')
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
    creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)  # credentials.json - скаченные данные с Google Cloud
    client = gspread.authorize(creds)

    sheet_id = os.getenv('SHEET_ID') # id таблицы
    workbook = client.open_by_key(sheet_id) # Вся таблица
    sheet = workbook.worksheet("КПД")  # Лист в таблице

    sheet.batch_clear(['R73:S102'])  # Очищаем два первых столбца
    set_with_dataframe(sheet, all_hours, row=73, col=18)  # Выгружаем данные в Google sheet

    delete_files()

    return redirect(url_for("home"))
