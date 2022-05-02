import pickle

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from passwd.pwdClassifier import HASHPwdClassifier, NgramPwdClassifier, FastTextPwdClassifier
from tokenizer.tool import train_valid_split, load_pkl


def pwdNgram():
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

def pwdNlp():
    dataset = pd.read_csv('raw_dataset/rockyou.txt',
                          delimiter="\n",
                          header=None,
                          names=["Passwords"],
                          encoding="ISO-8859-1",
                          nrows=1000
                          )

    X = dataset.to_numpy().reshape(-1).tolist()
    Y = np.ones(len(dataset))

    fastTextPredictor = FastTextPwdClassifier(padding_len=128, class_num=3)
    X, Y = fastTextPredictor.words2vec(X, Y, False)
    train_data, valid_data = train_valid_split(X, Y)

    fastTextPredictor.create_model()
    fastTextPredictor.run(train_data, valid_data, epochs=25, batch_size=64)




if __name__ == '__main__':

    pwdNgram()



