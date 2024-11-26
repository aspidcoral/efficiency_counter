import os

workdir = "C:\\Visual Studio Code my files\\Efficiency\\Infobip"


def delete_files():

    files = os.listdir(workdir)
    print(files)

    for file in files:
        if file.endswith('.csv') and file != 'result.csv':
            delete = os.path.join(workdir, file)
            os.remove(delete)


delete_files()
print('Deleted')
