import pickle
import numpy as np
from sklearn.model_selection import train_test_split

from context.contextClassifier import CNNClassifierGlove
from context.passFinderContext import PassFinderContextClassifier
from passwd.passFinderPass import PassFinderPassClassifier
from tokenizer.tool import load_pkl

if __name__ == '__main__':
    X = load_pkl('./dataset/passfinder_context_train_data.pkl').reshape(-1)
    Y = load_pkl('./dataset/passfinder_context_train_label.pkl').reshape(-1)

    passFinderClassifier = PassFinderContextClassifier(padding_len=256)

    X, Y = passFinderClassifier.words2vec(X, Y, fit=True)

    X, X_t, Y, Y_t = train_test_split(X, Y, stratify=Y, test_size=0.1)

    train_data, valid_data = [X, np.array(Y, dtype=int)], [X_t, np.array(Y_t, dtype=int)]

    passFinderClassifier.create_model()
    passFinderClassifier.run(train_data, valid_data, epochs=30, batch_size=256, imbalance=True)

    passFinderClassifier.save_model('model/context/model_passfinder.h5')