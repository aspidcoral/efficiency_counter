import shutil, os, gspread, pandas as pd
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe


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


def serch_report() -> str:  # Находим название отчетап
    files = os.listdir(workdir)
    for file in files:
        if (
            file.endswith(".csv")
            and file != result
            and file != file_day
            and file != file_night
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

    df = df[['1 Hour Time Window', 'Hours']]  # Оставляем только нужные столбцы

    df['Hours'] = df['Hours'] / 3600  # Переводим секунды в часы
    return df


# Глобальные переменные
downloads = "C:\\Users\\Adam\\Downloads"
workdir = "C:\\Visual Studio Code my files\\Efficiency\\Tech"
file_day = 'C:\\Visual Studio Code my files\\Efficiency\Tech\\КПД Техника.csv'
file_night = 'C:\\Visual Studio Code my files\\Efficiency\Tech\\КПД Техника час 0-1.csv'
result = 'result.csv'
move_files()  # Функция
report = serch_report()

# Считаем часы по выгрузке из бипа  
day_hours = read_file(file_day)
night_hours = read_file(file_night)

all_hours = pd.concat([day_hours, night_hours], axis=0)
all_hours = all_hours.groupby(['1 Hour Time Window']).sum()  # Группируем по фамилии и суммируем часы(ночь и день)

# Считаем чаты по отчету из бипа
chats = pd.read_csv(os.path.join(workdir, report))
chats = chats[['Agent Name', 'Conversation ID']]  # Оставляем только нужные столбцы

chats = chats.groupby(['Agent Name']).count()  # Считаем кол-во повторений каждой фамилии
all_hours['kpd'] = chats['Conversation ID'] / all_hours['Hours']  # КПД = кол-во чатов / кол-во часов

all_hours = all_hours.dropna(subset=['kpd'])  # Удаляем строки без значения
all_hours = all_hours.drop(columns=['Hours'])  # Удаляем столбец "Hours"

all_hours['kpd'] = all_hours['kpd'].round().astype(int)  # Округляем числа до целых
all_hours = all_hours[all_hours['kpd'] > 0]  # Удаляем нули


# Экспорт в Google sheets

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)  # credentials.json - скаченные данные с Google Cloud
client = gspread.authorize(creds)

sheet_id = '1_Pby1bSPXGnih5K7d0iTYdbyE_HZPLv2t3oW1RooYiw' # id таблицы
workbook = client.open_by_key(sheet_id) # Вся таблица
sheet = workbook.worksheet("КПД")  # Лист в таблице

sheet.batch_clear(['M52:N81'])  # Очищаем два первых столбца
set_with_dataframe(sheet, all_hours, row=52, col=13, include_index=True)  # Выгружаем данные в Google sheet

print('Done')
