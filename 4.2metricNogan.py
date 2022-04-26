import pickle

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

from context.contextClassifier import CNNClassifierGlove
from passwd.pwdClassifier import NgramPwdClassifier
import numpy as np

from tokenizer.tool import load_pkl


def draw_map(cf_matrix, label):
    ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True,
                     fmt='.2%', cmap='Blues')

    ax.set_xlabel('Predicted Label',fontsize=16)
    ax.set_ylabel('True Label',fontsize=16)

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(label)
    ax.yaxis.set_ticklabels(label)

    ## Display the visualization of the Confusion Matrix.
    # plt.show()

if __name__ == '__main__':
    X = load_pkl('./dataset/nogan_test_data.pkl').reshape(-1)
    raw_X = X
    Y = load_pkl('./dataset/nogan_test_label.pkl').reshape(-1)

    # pass_context = pd.read_csv('raw_dataset/mycontext_pass.csv')["context"]
    # str_context = pd.read_csv('raw_dataset/mycontext_str.csv')["context"].sample(1000)
    # X = []
    # Y = []
    # for i, p in enumerate([str_context, pass_context]):
    #     p = p.dropna()
    #     p = p.to_numpy().reshape(-1).tolist()
    #     Y.extend(np.zeros(len(p), dtype=int) + i)
    #     X.extend(p)
    # X = pd.DataFrame(X, dtype=str).to_numpy().reshape(-1)
    # Y = pd.DataFrame(Y, dtype=int).to_numpy().reshape(-1)

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
    # draw_map(matrix, ['Ordinary', 'Password'])
    # plt.show()
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)
