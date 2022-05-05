import pickle

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from passwd.passFinderPass import PassFinderPassClassifier
from passwd.pwdClassifier import HASHPwdClassifier, NgramPwdClassifier, FastTextPwdClassifier
from tokenizer.tool import train_valid_split, load_pkl


def pwdNgram():
    """
    train our credential classifier with n-gram
    :return:
    """
    X = load_pkl('./dataset/pwd_train_data.pkl').reshape(-1)
    Y = load_pkl('./dataset/pwd_train_label.pkl').reshape(-1)

    ngramPwdClassifier = NgramPwdClassifier(padding_len=512, class_num=3, glove_dim=100)

    X, Y = ngramPwdClassifier.words2vec(X, Y, n=3, fit=False)
    # X, X_t, Y, Y_t = train_test_split(X, Y, stratify=Y, test_size=0.2)

    # ngramPwdClassifier.get_matrix_6b(f"/home/rain/glove")

    # test_data = [X_t, np.array(Y_t, dtype=int)]

    train_data, valid_data = train_valid_split(X, Y)

    ngramPwdClassifier.create_model()
    ngramPwdClassifier.run(train_data, valid_data, epochs=50, batch_size=256)

    ngramPwdClassifier.save_model('model/pass/model_my_glove_3.h5')


def passFinder():
    """
    train model in passFinder
    :return:
    """
    X = load_pkl('./dataset/pwd_train_data.pkl').reshape(-1)
    Y = load_pkl('./dataset/pwd_train_label.pkl').reshape(-1)

    passFinderClassifier = PassFinderPassClassifier(padding_len=128, class_num=3)

    X, Y = passFinderClassifier.words2vec(X, Y, fit=True)

    X, X_t, Y, Y_t = train_test_split(X, Y, stratify=Y, test_size=0.1)

    train_data, valid_data = [X, np.array(Y, dtype=int)], [X_t, np.array(Y_t, dtype=int)]

    passFinderClassifier.create_model()
    passFinderClassifier.run(train_data, valid_data, epochs=50, batch_size=256)
    passFinderClassifier.save_model('model/pass/model_passfinder_3.h5')


if __name__ == '__main__':

    pwdNgram()



