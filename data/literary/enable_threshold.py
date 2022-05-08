import os

PATH = os.curdir
threshold = 40000  # порог по кол-ву символов в одном тексте
list_names = os.listdir(PATH)
roots = []

for name in list_names:
    if not (name.endswith('.py') or name.endswith('.txt') or 'DS_Store' in name):
        roots.append(PATH + '/' + name)

os.mkdir('filtered' + str(threshold))
filt_path = 'filtered' + str(threshold)
for root in roots:
    os.mkdir('filtered' + str(threshold) + '/' + root)

for t_path in roots:
    for root, dirs, files in os.walk(t_path):
        for filename in files:
            file_path = t_path + '/' + filename
            with open(file_path, 'r') as f:
                text = f.read()
                fileID = 0
                threshold_ = 40000
                # while threshold <= len(text):
                while fileID < 11 and threshold_ <= len(text):
                    with open('filtered' + str(threshold) + '/' + root + '/' + str(fileID) + '.txt', 'a',
                              encoding='utf-8') as currentFile:
                        new_text = text[threshold_ - 40000:threshold_]
                        currentFile.write(new_text)
                        currentFile.close()
                        fileID += 1
                        threshold_ += 40000


for t_path in os.listdir(filt_path):
    print(t_path)
    print(len([name for name in os.listdir(t_path) if os.path.isfile(os.path.join(t_path, name))]))