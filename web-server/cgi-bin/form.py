#!/usr/bin/env python3
import cgi
from pymystem3 import Mystem
import re

from gensim.models.word2vec import Word2Vec
model = Word2Vec.load_word2vec_format('/home/egor/Downloads/ruscorpora_mean_hs.model.bin', binary=True)

form = cgi.FieldStorage()
text = form.getfirst("annotation")
quality = float(form.getfirst("quality", "не задано"))
word = int(form.getfirst("word", "не задано"))

print(text)
print(quality)
print(word)

m = Mystem()
lemmas = m.lemmatize(text)
groups = ['S', 'A']
sortLemmas = list(filter(lambda x: 'analysis' in x
                         and len(x['analysis']) > 0
                         and x['analysis'][0]['gr'].split('=')[0].split(',')[0] in groups
                         and x['analysis'][0]['lex'] + '_' + x['analysis'][0]['gr'].split('=')[0].split(',')[0] in model
                         , m.analyze(text)))

listLemmas = list(map(lambda x: x['analysis'][0]['lex'] + '_' + x['analysis'][0]['gr'].split('=')[0].split(',')[0],
                      sortLemmas))

dictLemmas = dict(map(lambda x: (x, listLemmas.count(x)), listLemmas))
sortDict = sorted(dictLemmas.items(), key=lambda t: -t[1])
mostPopularWord = list(map(lambda x: x[0], sortDict))


def getLemmas(analyzeText):
    groups = ['S', 'A']
    sortLemmas = list(filter(lambda x: 'analysis' in x
                         and len(x['analysis']) > 0
                         and x['analysis'][0]['gr'].split('=')[0].split(',')[0] in groups
                         and x['analysis'][0]['lex'] + '_' + x['analysis'][0]['gr'].split('=')[0].split(',')[0] in model
                         , analyzeText))
    sortLemmas = list(map(lambda x: x['analysis'][0]['lex'] + '_' + x['analysis'][0]['gr'].split('=')[0].split(',')[0], sortLemmas))
    return sortLemmas


sentences = re.findall(r'[^.!?]+[.?!(...)]{1}', text)
lemmasSentences = list(map(lambda x: {"analyze": m.analyze(x), "text": x, "lemmas": getLemmas(m.analyze(x))},
                           sentences))


result = list(map(lambda x: x['text'], list(filter(lambda lemm: len(lemm['lemmas']) > 3
                     and model.n_similarity(lemm['lemmas'], mostPopularWord[:word]) > quality,
                     lemmasSentences))))

print("Content-type: text/html\n")
print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Обработка данных форм</title>
        </head>
        <body>""")

print("<h1>Annotation!</h1>")

for sentence in result:
    print("<p>{}</p>".format(sentence))

print("""</body>
        </html>""")
