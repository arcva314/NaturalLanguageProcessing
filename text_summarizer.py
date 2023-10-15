import numpy as np
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import networkx as nx
from PyPDF2 import PdfReader
import docx
import os
import requests
from bs4 import BeautifulSoup

def file_reader(file_name):
    file = open(file_name, 'r')
    filedata = file.readlines()
    sentences = []
    for i in range(len(filedata)):
        processed_file = filedata[i].strip().split(". ")
        for sentence in processed_file:
            sentences.append(sentence.replace("[^a-zA-z0-9]", " ").split(" "))
    if file_name == "working_file.txt":
        os.remove(file_name)
    return sentences

def pdf_reader(file_name, start, end):
    reader = PdfReader(file_name)
    text = ''
    for i in range(start, end+1):
        pages = reader.pages[i]
        for word in pages.extract_text().split('\n'):
            if word[-1] == '.' and word[-2] != "[A-Z]":
                f = open("working_file.txt", 'a')
                f.write(text + word + "\n")
                f.close()
                text = ''
            else:
                text += word.strip() + " "
    return file_reader("working_file.txt")

def read_docx(file_name):
    def getText(filename):
        doc = docx.Document(filename)
        fullText = []
        for para in doc.paragraphs:
            if (len(para.text) > 1):
                fullText.append(para.text)
        return fullText
    txt = getText(file_name)
    sentences = []
    for i in range(len(txt)):
        processed_txt = txt[i].strip().split(". ")
        for sentence in processed_txt:
            sentences.append(sentence.replace("[^a-zA-z0-9]", " ").split(" "))
    return sentences

def url_reader(link):
    result = requests.get(link)
    soup = BeautifulSoup(result.text, 'html.parser')
    txt = ''
    for script in soup(['p']):
        txt += script.get_text().strip() + "\n"
    lines = [l for l in txt.split("\n") if len(l.split()) > 10]
    sentences = []
    for i in range(len(lines)):
        processed_txt = lines[i].strip().split(". ")
        for sentence in processed_txt:
            sentences.append(sentence.replace("[^a-zA-z0-9]", " ").split(" "))
    return sentences

def sentence_similarity(s1, s2, stopwords):
    s1 = [l.lower() for l in s1]
    s2 = [l.lower() for l in s2]
    all_words = list(set(s1 + s2))
    vec1 = [0] * len(all_words)
    vec2 = [0] * len(all_words)
    for word in s1:
        if word in stopwords:
            continue
        vec1[all_words.index(word)] += 1
    for word in s2:
        if word in stopwords:
            continue
        vec2[all_words.index(word)] += 1
    return 1 - cosine_distance(vec1, vec2)

def similarity_matrix(sentences, stopwords):
    similarity = np.zeros((len(sentences), len(sentences)))
    for i1 in range(len(sentences)):
        for i2 in range(len(sentences)):
            if i1 == i2:
                continue
            similarity[i1][i2] = sentence_similarity(sentences[i1], sentences[i2], stopwords)
    return similarity

def execute(mode, file_name, k=5):
    stop_words = stopwords.words('english')
    sum_text = []
    if mode == 1:
        sentences = url_reader(file_name)
    elif mode == 2:
        sentences = read_docx(file_name)
    elif mode == 3:
        sentences = pdf_reader(file_name)
    elif mode == 4:
        sentences = file_reader(file_name)
    else:
        print('Invalid mode, must be between 1 and 4')
        exit()
    og = []
    for i in range(len(sentences)):
        og.append(" ".join(sentences[i]))
    sentence_similiarity_matrix = similarity_matrix(sentences, stop_words)
    graph = nx.from_numpy_array(sentence_similiarity_matrix)
    scores = nx.pagerank(graph)
    ranked = sorted(((scores[i], s) for i,s in enumerate(sentences)), reverse=True)
    for i in range(k):
        sum_text.append(" ".join(ranked[i][1]))
    sum_text_ordered = {}
    for sent in sum_text:
        sum_text_ordered.update({og.index(sent): sent})
    print("Summarized Text:")
    for k in sorted(sum_text_ordered.keys()):
        if sum_text_ordered[k][-1] == ".":
            print(sum_text_ordered[k])
        else:
            print(sum_text_ordered[k] + ".")
#example using hydroquinone wiki page
mode = int(input("Enter mode (1 = url, 2 = docx, 3 = pdf, 4 = text file) "))
execute(mode, "https://en.wikipedia.org/wiki/Hydroquinone", 15)