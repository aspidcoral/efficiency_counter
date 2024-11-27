import shutil, os, gspread, pandas as pd
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe


# Функции
def move_files():  # Распаковываем и удаляем архив, нужные файлы переносим в рабочую папку
    files = os.listdir(downloads)  # Список всех файлов в папке

    # Переносим файлы в рабочую папку
    for file in files:
        if file.endswith(".csv"):
            data = os.path.join(downloads, file)
            shutil.move(data, workdir)


def serch_report():  # Находим название отчета
    files = os.listdir(workdir)
    for file in files:
        if (
            file.endswith(".csv")
            and file != result
            and file != file_day
            and file != 'd_names.csv'
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


def read_nicknames():  # Считываем никнеймы из файла d_names.csv
    d_names = {}
    with open("Jira\\d_names.csv", "r") as inf:
        nicknames = inf.read().split("\n")
    for el in nicknames:
        list = el.split(": ")
        d_names[list[0]] = list[1]
    return d_names


# Глобальные переменные
downloads = "C:\\Users\\Adam\\Downloads"
workdir = "C:\\Visual Studio Code my files\\Efficiency\\Jira"
file_day = 'C:\\Visual Studio Code my files\\Efficiency\\Jira\\Время в статусе Доп_ Канал.csv'
result = 'result.csv'
move_files()  # Функция
report = serch_report()
d_names = pd.read_csv('Jira\\d_names.csv')

all_hours = read_file(file_day)
all_hours.rename(columns={'1 Hour Time Window': 'Имя'}, inplace=True)  # Меняем имя столбца

chats = pd.read_csv(os.path.join(workdir, report))
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
creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)  # credentials.json - скаченные данные с Google Cloud
client = gspread.authorize(creds)

sheet_id = '1_Pby1bSPXGnih5K7d0iTYdbyE_HZPLv2t3oW1RooYiw' # id таблицы
workbook = client.open_by_key(sheet_id) # Вся таблица
sheet = workbook.worksheet("КПД")  # Лист в таблице

sheet.batch_clear(['I73:J102'])  # Очищаем два первых столбца
set_with_dataframe(sheet, chats, row=73, col=9)  # Выгружаем данные в Google sheet

print('Done')
