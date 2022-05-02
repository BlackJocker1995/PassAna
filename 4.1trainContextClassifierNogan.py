import pickle
import numpy as np
from sklearn.model_selection import train_test_split

from context.contextClassifier import CNNClassifierGlove
from tokenizer.tool import load_pkl

if __name__ == '__main__':
    X = load_pkl('./dataset/nogan_train_data.pkl').reshape(-1)
    Y = load_pkl('./dataset/nogan_train_label.pkl').reshape(-1)

    cnnContextClassifier = CNNClassifierGlove(padding_len=256, glove_dim=100)

    X, Y = cnnContextClassifier.words2vec(X, Y, fit=False)

    X, X_t, Y, Y_t = train_test_split(X, Y, stratify=Y, test_size=0.1)

    cnnContextClassifier.get_matrix_6b(f"/home/rain/glove")

    train_data, valid_data = [X, np.array(Y, dtype=int)], [X_t, np.array(Y_t, dtype=int)]

    cnnContextClassifier.create_model()
    cnnContextClassifier.run(train_data, valid_data, epochs=50, batch_size=512, imbalance=True)

    cnnContextClassifier.save_model('model/context/model_nogan.h5')