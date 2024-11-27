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

    df = df[['1 Hour Time Window', 'Hours']]

    # Оставляем только строки, где в столбце '1 Hour Time Window' есть ' ММ'
    df = df.loc[df['1 Hour Time Window'].str.contains(' ММ')]

    df['Hours'] = df['Hours'] / 3600
    return df


# Глобальные переменные
downloads = "C:\\Users\\Adam\\Downloads"
workdir = "C:\\Visual Studio Code my files\\Efficiency\\Infobip"
file_day = 'C:\\Visual Studio Code my files\\Efficiency\\Infobip\\КПД ММ УР.csv'
file_night = 'C:\\Visual Studio Code my files\\Efficiency\\Infobip\\Час 0-1 ММ Самокат.csv'
move_files()  # Функция
report = search_report()

# Считаем часы по выгрузке из бипа  
day_hours = read_file(file_day)
night_hours = read_file(file_night)

all_hours = pd.concat([day_hours, night_hours], axis=0)
#reset_index() - Создаем новые индексы, чтобы столбец Agent name стал столбцом, а не индексацией:
all_hours = all_hours.groupby(['1 Hour Time Window']).sum().reset_index()  # Группируем по фамилии и суммируем часы(ночь и день)
all_hours.rename(columns={'1 Hour Time Window': 'Agent Name'}, inplace=True)  # Переименовываем столбец


# Считаем чаты по отчету из бипа
chats = pd.read_csv(os.path.join(workdir, report))
chats = chats.loc[chats['Agent Name'].str.contains(' ММ')]  # Оставлем только тех, у кого имя заканчивается на " ММ"

chats = chats[['Agent Name', 'Conversation ID']]  # Оставляем только нужные столбцы
#reset_index() - Создаем новые индексы, чтобы столбец Agent name стал столбцом, а не индексацией:
chats = chats.groupby(['Agent Name']).count().reset_index()  # Считаем кол-во повторений каждой фамилии


all_hours = all_hours.merge(chats, how='left', on='Agent Name')  # Объединяем Agent name и Chats в одну таблицу
all_hours['kpd'] = chats['Conversation ID'] / all_hours['Hours']  # КПД = кол-во чатов / кол-во часов

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

sheet_id = '1_Pby1bSPXGnih5K7d0iTYdbyE_HZPLv2t3oW1RooYiw' # id таблицы
workbook = client.open_by_key(sheet_id) # Вся таблица
sheet = workbook.worksheet("КПД")  # Лист в таблице

sheet.batch_clear(['D74:E102'])  # Очищаем два первых столбца
set_with_dataframe(sheet, all_hours, row=73, col=4)  # Выгружаем данные в Google sheet

print('Done')
