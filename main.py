import os
import re

path = "samples/"
flag_spam = "spam"
flag_nonspam = "nonspam"
words_map = {}

valueToChange = "N/A"
for root, dirs, files in os.walk(path):
    if flag_nonspam in root:
        valueToChange = flag_nonspam
    else:
        valueToChange = flag_spam
    counter = 1
    total_files = len(files)
    for data_file in files:
        print("Reading %s / %s (%s)" % (counter, total_files, root), end="\r")
        with open(os.path.join(root, data_file), 'r', errors="ignore") as f:
            data = f.read()
            allwords = re.findall(r"\b[a-zA-Z0-9$'\"]+", data)
            for word in allwords:
                try:
                    words_map[word][valueToChange] += 1
                except KeyError:
                    words_map[word] = {flag_spam: 0, flag_nonspam: 0}
                    words_map[word][valueToChange] += 1
        counter += 1
    print("All files in %s were read (%s files read)" % (root, total_files))

print("Done reading. Total words: %s" % (len(words_map)))