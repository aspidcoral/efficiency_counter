import win32com.client
from datetime import datetime

# Подключение к Outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# Получение папки "Отправленные"
sent_items = outlook.GetDefaultFolder(5)  # 5 - индекс для папки "Sent Mail"

# Подсчет сообщений по часам
email_count_by_hour = {}

# Проход по каждому сообщению в папке "Отправленные"
for item in sent_items.Items:
    if item.Class == 43:  # 43 - класс для почтовых сообщений
        sent_time = item.SentOn  # Дата и время отправки
        sent_hour = sent_time.hour  # Получение только часа отправки

        # Если час уже есть в словаре, увеличиваем счетчик
        if sent_hour in email_count_by_hour:
            email_count_by_hour[sent_hour] += 1
        else:
            email_count_by_hour[sent_hour] = 1

# Вывод результатов
for hour, count in sorted(email_count_by_hour.items()):
    print(f"С {hour:02d}:00 до {hour:02d}:59 было отправлено {count} сообщений")
