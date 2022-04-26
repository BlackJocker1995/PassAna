import operator

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split
from spacy import tokenizer

from context.contextClassifier import CNNClassifierGlove
from tokenizer.tool import load_pkl, MyTokenizer


def word_token():
    X = pd.read_csv('raw_dataset/mycontext_pass.csv')["context"].dropna().to_numpy().reshape(-1)
    Y = np.ones(X.shape[0])
    cnnContextClassifier = CNNClassifierGlove(padding_len=256)
    X, _ = cnnContextClassifier.words2vec(X, fit=False)

    get_top_n_words(X)


def get_top_n_words(corpus, n=20):
    # vec = CountVectorizer().fit(corpus)
    token = MyTokenizer()
    token.load_tokenizer("tokenizer/context.pkl")
    feq_token = token.tokenizer.word_counts
    sort_feq_token = sorted(feq_token.items(), key=operator.itemgetter(1), reverse=True)
    df1 = pd.DataFrame(sort_feq_token, columns=['text', 'count'])
    text = df1['text'].tolist()[:n]
    count = df1['count'].tolist()[:n]

    params = {
        'figure.figsize': '8, 4'
    }
    plt.rcParams.update(params)

    plt.barh(text, count)
    plt.yticks(fontsize=12)
    plt.grid(axis='x')
    plt.show()

def TSNE_Plot(vectors, label):
    tsne_model = TSNE(n_components=2, init="pca")
    X_tsne =tsne_model.fit_transform(vectors)
    plt.scatter(X_tsne[:, 0], X_tsne[:, 1])
    for i in len(label):
        plt.annotate(label[i],
                     xy=(X_tsne[i, 0], X_tsne[i, 1]),
                     textcoords="offset points",
                     xytext=(5, 2),
                     ha="right",
                     va="bottom")
    plt.show()


if __name__ == '__main__':
    word_token()