from __future__ import unicode_literals, print_function
import re
import codecs
import pycrfsuite
import os

"""
본 소스코드는 CRF_TRAIN.py로 생성한 모델을 가지고 test 하는 소스입니다.

model_name에는 테스트할 모델이름을 적어주세요.

입력으로는 ==> test.txt
출력으로는 ==> pred.txt
"""

model_name="model01" # 테스트 할 모델이름을 지정해주세요.


#BIE 테그만들기
def raw2corpus(raw_path, corpus_path):
    raw = codecs.open(raw_path, encoding='utf-8')
    raw_sentences = raw.read().split('\n')
    corpus = codecs.open(corpus_path, 'w', encoding='utf-8')
    sentences = []
    for raw_sentence in raw_sentences:
        if not raw_sentence:
            continue
        text = re.sub(r'(\ )+', ' ', raw_sentence).strip()
        taggeds = []
        for i in range(len(text)):
            if i == 0:
                taggeds.append('{}/B'.format(text[i]))
            elif text[i] != ' ':
                successor = text[i - 1]
                if successor == ' ':
                    taggeds.append('{}/B'.format(text[i]))
                else:
                    taggeds.append('{}/I'.format(text[i]))
        sentences.append(' '.join(taggeds))
    corpus.write('\n'.join(sentences))


#raw2corpus('data_newpaper.txt', 'train.txt')  #BIE 테그 만들기
    

#BIE 테그 복구시키기
def corpus2raw(corpus_path, raw_path):
    corpus = codecs.open(corpus_path, encoding='utf-8')
    corpus_sentences = corpus.read().split('\n')
    raw = codecs.open(raw_path, 'w', encoding='utf-8')
    sentences = []
    for corpus_sentence in corpus_sentences:
        taggeds = corpus_sentence.split(' ')
        text = ''
        len_taggeds = len(taggeds)
        for tagged in taggeds:
            try:
                word, tag = tagged.split('/')
                if word and tag:
                    if tag == 'B':
                        text += ' ' + word
                    else:
                        text += word
            except:
                pass
        sentences.append(text.strip())
    raw.write('\n'.join(sentences))

#corpus2raw('train.txt', 'restored.txt')  #BIE 테그를 없애기


"""
여기는 Feature 정의 부분입니다.
"""
#CRF에 학습시킬 feature를 정의. 여기선 좌우 2글자까지를 보고 해당 인덱스의 글자에 태그를 맞추는 조건부 확률 문제로 생각하겠다.
def corpus2sent(path):
    corpus = codecs.open(path, encoding='utf-8').read()
    raws = corpus.split('\n')
    sentences = []
    for raw in raws:
        tokens = raw.split(' ')
        sentence = []
        for token in tokens:
            try:
                word, tag = token.split('/')
                if word and tag:
                    sentence.append([word, tag])
            except:
                pass
        sentences.append(sentence)
    return sentences

def index2feature(sent, i, offset):
    word, tag = sent[i + offset]
    if offset < 0:
        sign = ''
    else:
        sign = '+'
    return '{}{}:word={}'.format(sign, offset, word)

def word2features(sent, i):
    L = len(sent)
    word, tag = sent[i]
    features = ['bias']
    features.append(index2feature(sent, i, 0))
    if i > 1:
        features.append(index2feature(sent, i, -2))
    if i > 0:
        features.append(index2feature(sent, i, -1))
    else:
        features.append('bos')
    if i < L - 2:
        features.append(index2feature(sent, i, 2))
    if i < L - 1:
        features.append(index2feature(sent, i, 1))
    else:
        features.append('eos')
    return features

def sent2words(sent):
    return [word for word, tag in sent]

def sent2tags(sent):
    return [tag for word, tag in sent]

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


tagger = pycrfsuite.Tagger()
tagger.open(model_name+".crfsuite") #모델 불러와서 태거로써 사용해보자.



raw2corpus('test.txt', 'test_tmp.txt')  #BI 테그 만들기  test 셋
test_sents = corpus2sent('test_tmp.txt')
test_x = [sent2features(sent) for sent in test_sents]
test_y = [sent2tags(sent) for sent in test_sents]

pred_y = [tagger.tag(x) for x in test_x]


def flush(path, X, Y):
    result = codecs.open(path, 'w', encoding='utf-8')
    for x, y in zip(X, Y):
        result.write(' '.join(['{}/{}'.format(feature[1].split('=')[1], tag) for feature, tag in zip(x, y)]))
        result.write('\n')
    result.close()

flush('test_tmp.txt', test_x, pred_y)
corpus2raw('test_tmp.txt', 'pred.txt') #결국 출력으로 pred.txt가 나온다.

os.remove('test_tmp.txt') #test_tmp 삭제


from itertools import chain
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer

def report(test_y, pred_y):
    lb = LabelBinarizer()
    test_y_combined = lb.fit_transform(list(chain.from_iterable(test_y)))
    pred_y_combined = lb.transform(list(chain.from_iterable(pred_y)))
    tagset = sorted(set(lb.classes_))
    class_indices = {cls: idx for idx, cls in enumerate(tagset)}
    print(classification_report(test_y_combined, pred_y_combined, labels=[class_indices[cls] for cls in tagset], target_names=tagset))

report(test_y, pred_y)
