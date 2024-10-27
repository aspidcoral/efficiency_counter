import shutil
import os
import pandas as pd

# Функции
def move_files() -> None:  # Распаковываем и удаляем архив, нужные файлы переносим в рабочую папку
    files: list[str] = os.listdir(downloads)  # Список всех файлов в папке

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
            txt: str = os.path.join(downloads, file)
            os.remove(txt)


def search_report() -> str:  # Находим название отчетап
    files: list[str] = os.listdir(workdir)
    for file in files:
        if (
            file.endswith(".csv")
            and file != result
            and file != file_day
            and file != file_night
        ):
            report: str = file
            return report


def count_seconds(data):
   pass


# Глобальные переменные
downloads = "C:\\Users\\Adam\\Downloads"
workdir = "C:\\Visual Studio Code my files\\Efficiency\\Infobip"
file_day = 'C:\\Visual Studio Code my files\\Efficiency\\Infobip\\КПД ММ УР.csv'
file_night = 'C:\\Visual Studio Code my files\\Efficiency\\Infobip\\Час 0-1 ММ Самокат.csv'
result = 'C:\\Visual Studio Code my files\\Efficiency\\Infobip\\result.csv'
move_files()  # Функция
report= search_report()

# # Переводим секунды в часы
# for el in names_hours:
#     if d_hours[el] >= 1800:
#         d_hours[el] /= 3600
#     else:
#         d_hours[el] = 0

def read_file(file):
    df = pd.read_csv(file)

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

print(read_file(file_day))
# print(read_file(file_night))
