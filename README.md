# CRF_Korea_Automatic_Spacing_Module
CRF base Korea Automatic Spacing Module(CRF를 이용한 한국어 자동 띄어쓰기)

## Introduction
CRF를 이용한 한국어 자동 띄어쓰기 모듈입니다.

딥러닝 방식을 이용하기 전 많이 사용하던 방식입니다.

## Module
- CRF_TRAIN.py ==> Pycrfsuite를 이용하여 모델을 만들어주는 소스입니다.
- CRF_TEST.py ==> 만들어진 모델을 바탕으로 테스트를 해볼 수 있는 소스입니다.

## 기술 소개
CRF에 대한 자세한 설명은 하단의 링크를 참고해주세요. <br>
https://ratsgo.github.io/machine%20learning/2017/11/10/CRF/

## Install
- pip install sklearn
- pip install python-crfsuite

## Data
- train data와 test data는 신문기사를 크롤링한 데이터를 임의로 넣어놓았습니다.
- 여러분의 한국어 단일 코퍼스를 이용하여 테스트를 진행해보세요.
