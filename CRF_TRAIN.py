# -*- coding: utf-8 -*-

"""
CRF를 이용한 한국어 띄어쓰기 모듈입니다.
본 소스코드는 CRF 모델을 만드는 소스코드 입니다.
model_name은 지정 가능합니다.
"""

from __future__ import unicode_literals, print_function

import re
import codecs



model_name="model01" # 모델이름을 지정해주세요.


"""
여기는 전처리 부분입니다.
띄어쓰기 학습 데이터 만들 때 BI 테그 사용.
"""
#BI 테그만들기
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
        features.append(index2feature(sent, i, -1))#실험해보기 어느게 더 좋은지 !!!!!!!!!!
        #features.append(index2feature(sent, i, -3))#실험해보기 어느게 더 좋은지 !!!!!!!!!!
        #features.append(index2feature(sent, i, -4))#실험해보기 어느게 더 좋은지 !!!!!!!!!!
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


"""
여기는 학습하는 부분입니다.
"""
import pycrfsuite

train_sents = corpus2sent('train.txt')

train_x = [sent2features(sent) for sent in train_sents]
train_y = [sent2tags(sent) for sent in train_sents]



trainer = pycrfsuite.Trainer()
for x, y in zip(train_x, train_y):  
    trainer.append(x, y)
trainer.train(model_name+".crfsuite") #학습한 모델을 저장할 파일 경로가 된다.  #최종 모델 결과임 


#raw2corpus('data_newpaper.txt', 'train.txt')  #BI 테그 만들기
#corpus2raw('train.txt', 'restored.txt')  #BI 테그를 없애기



