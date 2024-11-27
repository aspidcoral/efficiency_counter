import os

workdir1 = "C:\\Visual Studio Code my files\\Efficiency\\Infobip"
workdir2 = "C:\\Visual Studio Code my files\\Efficiency\\Jira"
workdir3 = "C:\\Visual Studio Code my files\\Efficiency\\Tech"
workdir4 = "C:\\Visual Studio Code my files\\Efficiency\\TeamLeader"


def delete_files(workdir):

    files = os.listdir(workdir)
    print(files)

    for file in files:
        if file.endswith('.csv') and file != 'd_names.csv':
            delete = os.path.join(workdir, file)
            os.remove(delete)


delete_files(workdir1)
delete_files(workdir2)
delete_files(workdir3)
delete_files(workdir4)

print('Deleted')
