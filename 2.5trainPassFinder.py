import pickle
import numpy as np
from sklearn.model_selection import train_test_split

from passwd.passFinderPass import PassFinderPassClassifier


def load_pkl(src):
    with open(src,'rb') as f:
        data = pickle.load(f)
    return data


if __name__ == '__main__':
    X = load_pkl('./dataset/pwd_train_data.pkl').reshape(-1)
    Y = load_pkl('./dataset/pwd_train_label.pkl').reshape(-1)

    passFinderClassifier = PassFinderPassClassifier(padding_len=128, class_num=3)

    X, Y = passFinderClassifier.words2vec(X, Y, fit=True)

    X, X_t, Y, Y_t = train_test_split(X, Y, stratify=Y, test_size=0.1)

    train_data, valid_data = [X, np.array(Y, dtype=int)], [X_t, np.array(Y_t, dtype=int)]

    passFinderClassifier.create_model()
    passFinderClassifier.run(train_data, valid_data, epochs=50, batch_size=256)
    passFinderClassifier.save_model('model/pass/model_passfinder_3.h5')
