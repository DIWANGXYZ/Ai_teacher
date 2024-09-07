import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']


files = ['edit.html', 'index.html', 'main.py']
for file in files:
    encoding = detect_encoding(file)
    print(f"{file}: {encoding}")