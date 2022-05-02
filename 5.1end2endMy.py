from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
from context.contextClassifier import CNNClassifierGlove
from context.passFinderContext import PassFinderContextClassifier
from passwd.passFinderPass import PassFinderPassClassifier
from passwd.pwdClassifier import NgramPwdClassifier
import pandas as pd
import numpy as np


def wtestX(X):
    ngramPwdClassifier = NgramPwdClassifier(padding_len=512, class_num=3, glove_dim=100)
    X, _ = ngramPwdClassifier.words2vec(X, n=3, fit=False)
    ngramPwdClassifier.load_model('model/pass/model_my_glove_3.h5')

    y_pred = ngramPwdClassifier.model.predict(X)
    return y_pred

def first_model(X):
    X = X['str'].to_numpy().reshape(-1)
    ngramPwdClassifier = NgramPwdClassifier(padding_len=512, class_num=3)
    X, _ = ngramPwdClassifier.words2vec(X, n=3, fit=False)
    ngramPwdClassifier.load_model('model/pass/model_my_glove_3.h5')

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
    ax.set_ylabel('True Label', fontsize=16)

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(label)
    ax.yaxis.set_ticklabels(label)


def create():
    credential_my = pd.read_csv('raw_dataset/mycontext_pass.csv').dropna()
    credential_my['line'] = credential_my['line'].astype(int)
    ordinary_my = pd.read_csv('raw_dataset/mycontext_str.csv')
    ordinary_my['line'] = ordinary_my['line'].astype(int)

    credential_finder = pd.read_csv('raw_dataset/passfindercontext_pass.csv').drop_duplicates().rename(columns={'context':'finder_context'})
    credential_finder['line'] = credential_finder['line'].astype(int)
    ordinary_finder = pd.read_csv('raw_dataset/passfindercontext_str.csv').drop_duplicates().rename(columns={'context':'finder_context'}).dropna()
    ordinary_finder = ordinary_finder[ordinary_finder['line'].str.isdecimal()]
    ordinary_finder['line'] = ordinary_finder['line'].astype(int, errors='ignore')

    credential = pd.merge(credential_my, credential_finder, on=['var', 'str', 'location', 'line', 'project']).sample(200)
    ordinary = pd.merge(ordinary_my, ordinary_finder, on=['var', 'str', 'location', 'line', 'project']).sample(500)
    X = pd.concat([credential, ordinary])
    Y = np.r_[np.ones(credential.shape[0]), np.zeros(ordinary.shape[0])]
    X['raw_label'] = Y
    X.to_csv('e2e/raw.csv', index=False)


if __name__ == '__main__':
    # create()
    X = pd.read_csv('e2e/raw.csv')
    first_mark = first_model(X).argmax(axis=1)
    first_mark = np.minimum(np.ones(first_mark.shape), first_mark)

    second_mark = second_model(X)

    second_mark = second_mark.argmax(axis=1)

    X['first'] = first_mark
    X['second'] = second_mark
    X.to_csv('e2e/checker.csv', index=False)

    # first_mark = wtestX(['e5c9ee274ae87bc031adda32e27fa98b9290da83']).argmax(axis=1)
    # print(first_mark)

