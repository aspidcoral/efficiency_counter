import pandas as pd

def count_seconds():
    data = pd.read_csv('КПД Бип\КПД ММ УР.csv', header=1, names=['Имя']+[f'Число{i}' for i in range(1, 22)])

    data['Сумма'] = data.iloc[:, 1:].sum(axis=1)
    result = dict(zip(data['Имя'], data['Сумма']))
    print(result)
