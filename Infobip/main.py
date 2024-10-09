import shutil
import os


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


def count_seconds(data) -> None:
    # Открываем файл и пропускаем две неинф строки
    inf = open(os.path.join(workdir, data), "r")
    _ = inf.readline().split(",") + inf.readline().split(",")
    cnt = 0

    # Читаем строку, разбиваем на значения
    info = inf.readlines()
    for line in info:
        spl_line: list[str] = line.split('","')
        cnt = 0

        # Удаляем лишние символы и складываем цифры за день
        for i in range(len(spl_line)):
            if spl_line[i].endswith('"\n'):
                spl_line[i] = spl_line[i][:-2]
            elif spl_line[i].startswith('"'):
                spl_line[i] = spl_line[i][1:]

            # Считаем сумму всех секунд
            if spl_line[i].isdigit():
                cnt += int(spl_line[i])
        if not spl_line[0].endswith(' ММ'):
            spl_line[0] = ''
        # Добавляем фамилии и секунды в словарь
        operator = spl_line[0]
        if operator in d_hours:
            d_hours[operator] += cnt
        else:
            d_hours[operator] = cnt

    # Закрываем файл
    inf.close()


# Глобальные переменные
downloads = "C:\\Users\\Adam\\Downloads"
workdir = "C:\\Visual Studio Code my files\\Efficiency\\Infobip"
file_day = 'КПД ММ УР.csv'
file_night = 'Час 0-1 ММ Самокат.csv'
d_hours = {}
result = 'result.csv'
move_files()  # Функция
report: str = search_report()
count_seconds(file_day)  # Считаем секунды работы лнем

count_seconds(file_night)  # Считаем секунды работы ночью

names_hours = list(d_hours.keys())  # Список имен из отчета времени работы

# Переводим секунды в часы
for el in names_hours:
    if d_hours[el] >= 1800:
        d_hours[el] /= 3600
    else:
        d_hours[el] = 0


# Открываем файл отчета и пропускаем первую неинф строку
inf = open(os.path.join(workdir, report), "r")
_ = inf.readline().split(",")

# Читаем строки и добавляем имена в список
info = inf.readlines()
chats = [
    line.split(",")[7] for line in info if len(line.split(",")) >= 8
]  # Список всех имен(повторяются)

d_chats = {name: chats.count(name) for name in chats}  # Словарь для имен и кол-ва чатов

names_chats = list(d_chats.keys())  # Все уникальные имена из отчета

# Считаем КПД и добавляем его в словарь
d_kpd = {name: d_chats[name] / d_hours[name] for name in names_hours if name in names_chats if d_hours[name] > 0}
print(d_kpd)

round_kpd = {name: round(value) for name, value in d_kpd.items() if round(value) != 0}

with open(os.path.join(workdir, result), "w") as ouf:
    for key, value in round_kpd.items():
        ouf.write(f"{key}: {value}\n")

print("Done")
print('Dont forget to commit')
