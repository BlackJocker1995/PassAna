import pickle
import time

import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

from passwd.pwdClassifier import NgramPwdClassifier
import numpy as np


def load_pkl(src):
    with open(src, 'rb') as f:
        data = pickle.load(f)
    return data


def save_pkl(src, obj):
    with open(src, 'wb') as f:
        pickle.dump(obj, f)


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
    X = load_pkl('./dataset/pwd_test_data.pkl').reshape(-1)
    r_x = X
    Y = load_pkl('./dataset/pwd_test_label.pkl').reshape(-1)

    ngramPwdClassifier = NgramPwdClassifier(padding_len=512, class_num=3)
    X, Y = ngramPwdClassifier.words2vec(X, Y, n=3, fit=False)
    ngramPwdClassifier.load_model('model/pass/model_my_glove_3.h5')

    a = time.time()
    y_pred = ngramPwdClassifier.model.predict(X)
    b = time.time()
    print(b-a)


    Y = Y.argmax(axis=1)
    y_pred = y_pred.argmax(axis=1)

    matrix = confusion_matrix(Y, y_pred)
    draw_map(matrix, ['Ordinary', 'Password', 'Security Token'])
    # plt.show()
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)

    b_Y = np.minimum(np.ones(Y.shape), Y)
    b_y_pred = np.minimum(np.ones(Y.shape), y_pred)

    m = classification_report(b_Y, b_y_pred, digits=4)
    print(m)

    index1 = b_Y == 0
    index2 = b_y_pred == 1
    out_index = index1 * index2
    #print(r_x[out_index])

    # matrix = confusion_matrix(b_Y, b_y_pred)
    # draw_map(matrix, ['Ordinary', 'Security Credential'])
    # plt.savefig('metrics/my_confusion_matrix_2.pdf')