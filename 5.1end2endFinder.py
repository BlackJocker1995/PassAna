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
    passFinderPassClassifier = PassFinderPassClassifier(padding_len=128, class_num=4)

    X, _ = passFinderPassClassifier.words2vec(X, fit=False)
    passFinderPassClassifier.load_model('model/pass/model_passfinder_3.h5')

    y_pred = passFinderPassClassifier.model.predict(X)

    return y_pred


def second_model(X):
    X = X['finder_context'].to_numpy().reshape(-1)
    passFinderContextClassifier = PassFinderContextClassifier(padding_len=256)

    X, _ = passFinderContextClassifier.words2vec(X, fit=False)
    passFinderContextClassifier.load_model('model/context/model_passfinder.h5')

    y_pred = passFinderContextClassifier.model.predict(X)

    return y_pred





def create():
    X = pd.read_csv('e2e/raw.csv')
    item = X[["var", 'str','location', 'raw_label']]
    item_credential = item[item['raw_label'] == 1]
    item_ordinary = item[item['raw_label'] == 0]

    credential = pd.read_csv('raw_dataset/passfindercontext_pass.csv').drop_duplicates()
    credential['line'] = credential['line'].astype(int)
    ordinary = pd.read_csv('raw_dataset/passfindercontext_str.csv').drop_duplicates()

    merge_credential = pd.merge(item_credential, credential, on=['var', 'location'])
    merge_ordinary = pd.merge(item_ordinary, ordinary, on=['var', 'location'])

    X = pd.concat([merge_credential, merge_ordinary])
    X.to_csv('e2e/raw_passfinder.csv', index=False)


if __name__ == '__main__':
    X = pd.read_csv('e2e/raw.csv')
    first_mark = first_model(X).argmax(axis=1)
    first_mark = np.minimum(np.ones(first_mark.shape), first_mark)

    second_mark = second_model(X)

    second_mark = second_mark.argmax(axis=1)

    X['first'] = first_mark
    X['second'] = second_mark
    X.to_csv('e2e/finder.csv', index=False)

