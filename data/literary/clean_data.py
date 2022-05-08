import re
import unicodedata
import os

PATH = os.curdir
list_names = os.listdir(PATH)
roots = []

for name in list_names:
    if not (name.endswith('.py') or name.endswith('.txt') or 'DS_Store' in name):
        roots.append(PATH + '/' + name)
print(roots)

for t_path in roots:
    for root, dirs, files in os.walk(t_path):
        for filename in files:
            file_path = t_path + '/' + filename
            print(t_path + '/' + filename)  # путь к текущему тексту
            with open(file_path, 'r') as f:
                text = f.read()
                new_text = unicodedata.normalize("NFKD", text)
                with open(file_path.replace('.txt','clean') + '.txt', 'a') as out:
                    out.write(new_text)
            os.remove(file_path)

