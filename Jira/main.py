import shutil
import os


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


def count_seconds(data):  # Считаем время в статусе (секунды)
    # Открываем файл и пропускаем две неинф строки
    inf = open(os.path.join(workdir, data), "r")
    _ = inf.readline().split(",") + inf.readline().split(",")
    cnt = 0

    # Читаем строку, разбиваем на значения
    info = inf.readlines()
    for line in info:
        spl_line = line.split('","')
        cnt = 0

        # Удаляем лишние символы и складываем цифры за день
        for i in range(len(spl_line)):
            if spl_line[i].endswith('"\n'):
                spl_line[i] = spl_line[i][:-2]
            elif spl_line[i].startswith('"'):
                spl_line[i] = spl_line[i][1:]
            if spl_line[i].endswith(' ММ'):
                spl_line[i] = spl_line[i][:-3]
            # Считаем сумму всех секунд
            if spl_line[i].isdigit():
                cnt += int(spl_line[i])
            
        # Добавляем фамилии и секунды в словарь
        operator = spl_line[0]
        if operator in d_hours:
            d_hours[operator] += cnt
        else:
            d_hours[operator] = cnt

    # Закрываем файл
    inf.close()


def read_nicknames():  # Считываем никнеймы из файла d_names.csv
    d_names = {}
    with open("КПД Jira\\d_names.csv", "r") as inf:
        nicknames = inf.read().split("\n")
    for el in nicknames:
        list = el.split(": ")
        d_names[list[0]] = list[1]
    return d_names


# Глобальные переменные
downloads = "C:\\Users\\Adam\\Downloads"
workdir = "C:\\Visual Studio Code my files\\КПД\\КПД Jira"
file_day = "Время в статусе Доп_ Канал.csv"
d_hours = {}
result = 'result.csv'
move_files()  # Функция
report = serch_report()
d_names = read_nicknames()

count_seconds(file_day)  # Считаем секунды работы лнем

names_hours = list(d_hours.keys())  # Список имен из отчета времени работы

# Переводим секунды в часы
for el in names_hours:
    if d_hours[el] >= 1800:
        d_hours[el] /= 3600
    else:
        d_hours[el] = 0


# Открываем файл отчета и пропускаем первую неинф строку
inf = open(os.path.join(workdir, report), "r")
top = inf.readline().split(",")

# Читаем строки и добавляем имена в список
info = inf.readlines()
nicknames = [line.split(',')[6] for line in info if len(line.split(',')) > 6] # Список никнеймов
chats = [d_names[name] for name in nicknames if name in d_names.keys()]  # Переводим никнеймы в имена (повторяются)
inf.close()

d_chats = {name: chats.count(name) for name in chats}  # Словарь для имен и кол-ва тикетов

names_chats = list(d_chats.keys())  # Все уникальные имена из отчета


# Считаем КПД и добавляем его в словарь
d_kpd = {name: d_chats[name] / d_hours[name] for name in names_hours if name in names_chats and d_hours[name] > 0}
print(*d_kpd.items(), sep='\n') 

round_kpd = {name: round(value) for name, value in d_kpd.items() if round(value) != 0}

with open(os.path.join(workdir, result), "w") as ouf:
    for key, value in round_kpd.items():
        ouf.write(f"{key}: {value}\n")

print("Done")
