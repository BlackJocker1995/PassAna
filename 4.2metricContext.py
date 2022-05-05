import pickle
import time

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

from context.contextClassifier import CNNClassifierGlove
from context.passFinderContext import PassFinderContextClassifier
from passwd.pwdClassifier import NgramPwdClassifier
import numpy as np

from tokenizer.tool import load_pkl


def flowContextClassifier():
    X = load_pkl('./dataset/nogan_test_data.pkl').reshape(-1)
    raw_X = X
    Y = load_pkl('./dataset/nogan_test_label.pkl').reshape(-1)

    cnnContextClassifier = CNNClassifierGlove(padding_len=256)

    X, Y = cnnContextClassifier.words2vec(X, Y, fit=False)
    cnnContextClassifier.load_model('model/context/model_my.h5')

    a = time.time()
    y_pred = cnnContextClassifier.model.predict(X)
    b = time.time()
    print(b-a)

    Y = Y.argmax(axis=1)
    y_pred = y_pred.argmax(axis=1)

    index1 = Y == 1
    index2 = y_pred == 0
    out_index = index1 * index2

    print(raw_X[out_index])
    matrix = confusion_matrix(Y, y_pred)
    # draw_map(matrix, ['Ordinary', 'Password'])
    # plt.show()
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)


def flowContextClassifierTrainedNoGan():
    X = load_pkl('./dataset/nogan_test_data.pkl').reshape(-1)
    raw_X = X
    Y = load_pkl('./dataset/nogan_test_label.pkl').reshape(-1)

    cnnContextClassifier = CNNClassifierGlove(padding_len=512)

    X, Y = cnnContextClassifier.words2vec(X, Y, fit=False)
    cnnContextClassifier.load_model('model/context/model_nogan.h5')

    y_pred = cnnContextClassifier.model.predict(X)

    Y = Y.argmax(axis=1)
    y_pred = y_pred.argmax(axis=1)

    index1 = Y == 1
    index2 = y_pred == 0
    out_index = index1 * index2

    print(raw_X[out_index])

    matrix = confusion_matrix(Y, y_pred)
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)

def passFinder():
    X = load_pkl('./dataset/passfinder_context_test_data.pkl').reshape(-1)
    Y = load_pkl('./dataset/passfinder_context_test_label.pkl').reshape(-1)

    passFinderContextClassifier = PassFinderContextClassifier(padding_len=256)

    X, Y = passFinderContextClassifier.words2vec(X, Y, fit=False)
    passFinderContextClassifier.load_model('model/context/model_passfinder.h5')

    y_pred = passFinderContextClassifier.model.predict(X)

    Y = Y.argmax(axis=1)
    y_pred = y_pred.argmax(axis=1)

    matrix = confusion_matrix(Y, y_pred)
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)


if __name__ == '__main__':
    flowContextClassifier()


