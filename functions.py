from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import os, pandas as pd, shutil, gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe


upload_folder = "uploads"  # Папка для загрузки файлов
os.makedirs(upload_folder, exist_ok=True)
file_day = 'КПД ММ УР.csv'
file_night = 'Час 0-1 ММ Самокат.csv'


def upload_files():
    files = request.files.getlist('file')  # Получаем список загруженных файлов
    for file in files:
        # Обрабатываем каждый файл
        file.save(os.path.join(upload_folder, file.filename))  # Сохраняем файл
    return 'Files uploaded successfully!'


def unzip_files():  # Распаковываем и удаляем архив, нужные файлы переносим в рабочую папку
    files = os.listdir(upload_folder)  # Список всех файлов в папке

    # Распаковываем архив и удаляем его
    for file in files:
        if file.endswith(".zip"):
            arh = os.path.join(upload_folder, file)
            shutil.unpack_archive(arh, upload_folder)
            os.remove(arh)

    files = os.listdir(upload_folder)  # Список всех файлов в папке

    for file in files:
        if file.endswith(".txt"):
            txt = os.path.join(upload_folder, file)
            os.remove(txt)


def search_report():  # Находим название отчетап
    files = os.listdir(upload_folder)
    for file in files:
        if (
            file.endswith(".csv")
            and file != 'КПД ММ УР.csv'
            and file != 'Час 0-1 ММ Самокат.csv'
            and file != 'Время в статусе Доп_ Канал.csv'
            and file != 'КПД ТЛ время.csv'
            and file != 'КПД Техника.csv'
            and file != 'КПД Техника час 0-1.csv'
        ):
            report = file
            return report


def delete_files():
    files = os.listdir(upload_folder)
    for file in files:
        delete = os.path.join(upload_folder, file)
        os.remove(delete)
