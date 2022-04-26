from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
from context.contextClassifier import CNNClassifierGlove
from context.passFinderContext import PassFinderContextClassifier
from passwd.passFinderPass import PassFinderPassClassifier
from passwd.pwdClassifier import NgramPwdClassifier
import pandas as pd
import numpy as np


def first_model(X):
    X = X['str'].to_numpy().reshape(-1)
    ngramPwdClassifier = NgramPwdClassifier(padding_len=512, class_num=4)
    X, _ = ngramPwdClassifier.words2vec(X, n=3, fit=False)
    ngramPwdClassifier.load_model('model/pass/model_my_glove_4.h5')

    y_pred = ngramPwdClassifier.model.predict(X)
    return y_pred

def second_model(X):
    X = X['context'].to_numpy().reshape(-1)
    cnnContextClassifier = CNNClassifierGlove(padding_len=256)

    X, _ = cnnContextClassifier.words2vec(X, fit=False)
    cnnContextClassifier.load_model('model/context/model_my.h5')

    y_pred = cnnContextClassifier.model.predict(X)

    return y_pred

def draw_map(cf_matrix, label):
    ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True,
                     fmt='.2%', cmap='Blues')

    ax.set_xlabel('Predicted Label',fontsize=16)
    ax.set_ylabel('True Label',fontsize=16)

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(label)
    ax.yaxis.set_ticklabels(label)


def create():
    ordinary_finder = pd.read_csv('raw_dataset/mycontext_str_test.csv').drop_duplicates().dropna()
    # ordinary_finder = ordinary_finder[ordinary_finder['line'].str.isdecimal()]
    ordinary_finder['line'] = ordinary_finder['line'].astype(int, errors='ignore')

    X = ordinary_finder
    X.to_csv('e2e/raw_test.csv', index=False)


if __name__ == '__main__':
    # create()
    X = pd.read_csv('e2e/raw_test.csv')
    first_mark = first_model(X).argmax(axis=1)
    first_mark = np.minimum(np.ones(first_mark.shape), first_mark)

    second_mark = second_model(X)

    second_mark = second_mark.argmax(axis=1)

    X['first'] = first_mark
    X['second'] = second_mark
    X = X[(X['first'] == 1) & (X['second'] == 1)]
    X.to_csv('e2e/checker_test.csv', index=False)

