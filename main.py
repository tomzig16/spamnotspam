import os
import re
from random import randint
from  decimal import *

path = "samples/"
flag_spam = "spam"
flag_nonspam = "nonspam"

cross_check_index = 300   # how many 
n_of_words_to_check = 15
spam_border = 0.3 # if more than this value -> spam, else -> not spam
repeats = 10 # when using small amount of files to validate

words_map = {}

are_paths_registered = False
file_paths = []
checkResults = []

def LoadWordsWithChecks(validationStartIndex=0, ignoreForCrossCheck=False):
    global are_paths_registered
    valueToChange = "N/A"
    file_counter = 0
    for root, dirs, files in os.walk(path):
        if flag_nonspam in root:
            valueToChange = flag_nonspam
        else:
            valueToChange = flag_spam
        counter = 1
        total_files = len(files)
        for data_file in files:
            file_path = os.path.join(root, data_file)
            if not are_paths_registered: file_paths.append(file_path)
            if (not ignoreForCrossCheck) or (file_counter < validationStartIndex or file_counter >= validationStartIndex + cross_check_index):
                print("Reading %s / %s (%s)" % (counter, total_files, root), end="\r")
                with open(file_path, 'r', errors="ignore") as f:
                    data = f.read()
                    allwords = re.findall(r"\b[a-zA-Z0-9$'\"]+", data)
                    for word in allwords:
                        try:
                            words_map[word][valueToChange] += 1
                        except KeyError:
                            words_map[word] = {flag_spam: 0, flag_nonspam: 0, "total": 0}
                            words_map[word][valueToChange] += 1
                        finally:
                            words_map[word]["total"] += 1
            counter += 1
            file_counter += 1
        print("All files in %s were read (%s files read)" % (root, total_files))
    are_paths_registered = True
    print("Done reading. Total words: %s" % (len(words_map)))

def CheckSingleFile(nOfRandomWords, fileIndex):
    word_indexes = []
    with open(file_paths[fileIndex], 'r', errors="ignore") as f:
        data = f.read()
        allwords = re.findall(r"\b[a-zA-Z0-9$'\"]+", data)
    n_of_indexes = nOfRandomWords
    if nOfRandomWords > len(allwords): n_of_indexes = len(allwords)
    for i in range(0, nOfRandomWords):
        hasCopy = True
        if n_of_indexes == len(allwords):
            for x in range(0, n_of_indexes):
                word_indexes.append(x)
        else:
            while hasCopy:
                index = randint(0, n_of_indexes)
                if index not in word_indexes:
                    word_indexes.append(index)
                    hasCopy = False
    wordChanceOfBeingSpam = [] # P(S|W) = P(W|S) / (P(W|S) + P(W|H))
    for i in range(0, n_of_indexes):
        try:
            word_in_check = words_map[allwords[word_indexes[i]]]
            wordIsSpam      = word_in_check[flag_spam] / word_in_check["total"] # P(W|S)
            wordIsNotSpam   = word_in_check[flag_nonspam] / word_in_check["total"] # P(W|H)
        except KeyError:
            wordIsSpam = 0.5
            print("%s was not seen ever before... Treating the word as %s (could be both, spam or not)" % (allwords[i], wordIsSpam))
            wordIsNotSpam = 1 - wordIsSpam
        finally:
            wordChanceOfBeingSpam.append(wordIsSpam / (wordIsSpam + wordIsNotSpam))

    # p = p1 * p2...pn / ( p1 * p2...pn + (1 - p1) * (1 - p2)...(1 - pn) )
    p_up = Decimal(1)
    # p_down1 is the same as p_up
    p_down2 = Decimal(1)
    for x in wordChanceOfBeingSpam: 
        p_up *= Decimal(x)
        p_down2 *= Decimal((1 - x))
    try:
        return Decimal(p_up / (p_up + p_down2))
    except InvalidOperation:
        # usually when values are small so it is almost like division by zero
        return 0

def SetSampleFiles():
    global file_paths
    global are_paths_registered
    if are_paths_registered: return
    for root, dirs, files in os.walk(path):
        for data_file in files:
            file_paths.append(os.path.join(root, data_file))
    are_paths_registered = True

def DoCrossValidation():
    #global file_paths
    global checkResults
    SetSampleFiles()
    try:
        os.mkdir("res")
    except FileExistsError:
        pass
    file = open("res/%sw_%s.csv" % (n_of_words_to_check, cross_check_index), "w") 
    for start_i in range(0, len(file_paths), cross_check_index):
        LoadWordsWithChecks(start_i, True)
        #file.write("Samples from %s to %s\n" % (start_i, start_i + cross_check_index - 1))
        for file_i in range(start_i, start_i + cross_check_index):
            if file_i >= len(file_paths):
                break
            ftype = file_paths[file_i].split('/')[1]
            result = CheckSingleFile(n_of_words_to_check, file_i)
            isSpam = "NotSpam"
            if spam_border <= result:
                isSpam = "Spam"
            percentage = ("%s" % (round(result * 100, 6)))
            file.write("%s,%s%%,%s,%s\n" % (file_paths[file_i], percentage, isSpam, result))
            checkResults.append(
                { "percentage": percentage, "type": ftype, "verbalResult": isSpam, "result": result }
            )
        print("Files from %s to %s - done." % (start_i, start_i + cross_check_index - 1))
        words_map.clear()
    file.close()
        



DoCrossValidation()
