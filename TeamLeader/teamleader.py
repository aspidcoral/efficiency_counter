import shutil, os, gspread, pandas as pd
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe


# Функции
def move_files():  # Распаковываем и удаляем архив, нужные файлы переносим в рабочую папку
    files = os.listdir(downloads)  # Список всех файлов в папке

    # Распаковываем архив и удаляем его
    for file in files:
        if file.endswith(".zip"):
            arh = os.path.join(downloads, file)
            shutil.unpack_archive(arh, downloads)
            os.remove(arh)

    files = os.listdir(downloads)  # Список всех файлов в папке

    # Переносим файлы в рабочую папку
    for file in files:
        if file.endswith(".csv"):
            data = os.path.join(downloads, file)
            shutil.move(data, workdir)
        elif file.endswith(".txt"):
            txt = os.path.join(downloads, file)
            os.remove(txt)


def search_report():  # Находим название отчетап
    files = os.listdir(workdir)
    for file in files:
        if (
            file.endswith(".csv")
            and file != 'КПД ММ УР.csv'
            and file != 'Час 0-1 ММ Самокат.csv'
        ):
            report = file
            return report


def read_file(file):
    df = pd.read_csv(file)

    # Преобразуем значения в числовой формат перед суммированием
    for col in df.columns[1:]:  # Пропускаем первый столбец
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Суммируем все цифры в столбцах с 03 по 23 и записываем в столбец Total
    df['Hours'] = df.iloc[:, 1:].sum(axis=1)

    # Оставляем только нужные столбцы
    df = df[['1 Hour Time Window', 'Hours']]

    # Оставляем только строки, где в столбце '1 Hour Time Window' есть ' Тимлидер'
    df = df.loc[df['1 Hour Time Window'].str.contains(' Тимлидер')]

    # Переводим секунды в часы
    df['Hours'] = df['Hours'] / 3600
    return df


# Глобальные переменные
downloads = 'C:\\Users\\Adam\\Downloads'
workdir = 'C:\\Visual Studio Code my files\\Efficiency\\TeamLeader'
file_day = 'C:\\Visual Studio Code my files\\Efficiency\\TeamLeader\\КПД ТЛ время.csv'
move_files()  # Функция
report = search_report()
