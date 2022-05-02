import hashlib
import logging
import sys
from abc import abstractmethod

import nltk
import numpy as np
from keras.layers import Dense, GlobalAveragePooling1D, Flatten, Conv2D, Conv1D, MaxPooling1D, GlobalMaxPooling1D, \
    Dropout
from keras.layers import Embedding
from keras.models import Sequential, load_model
from keras.preprocessing import sequence
from keras.utils.np_utils import to_categorical
from keras_preprocessing.sequence import pad_sequences
from sklearn.utils import compute_class_weight
from tqdm import tqdm
import pandas as pd
from tokenizer.tool import MyTokenizer, train_valid_split, load_embedding

MAX_NB_WORDS = 10000


class PwdClassifier:
    def __init__(self, padding_len, class_num, debug=False):
        self.padding_len: int = padding_len
        self.class_num = class_num

        self.model: Sequential = None
        self.tokenizer: MyTokenizer = MyTokenizer()

        if debug:
            logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - '
                                       '%(levelname)s: %(message)s',
                                level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - '
                                       '%(levelname)s: %(message)s',
                                level=logging.INFO)

    @abstractmethod
    def create_model(self):
        pass

    def run(self, train, valid, epochs, batch_size, imbalance):
        if self.model is None:
            logging.error('Model is None')
            raise ValueError('Create model at first!')

        if imbalance:
            tmp_y = np.argmax(train[1], axis=1)
            weights = compute_class_weight(class_weight='balanced', classes=[0, 1], y=tmp_y)
            self.model.fit(train[0], train[1],
                           epochs=epochs, batch_size=batch_size,
                           validation_data=(valid[0], valid[1]),
                           class_weight={0: weights[0], 1: weights[1]},
                           shuffle=True)
        else:
            self.model.fit(train[0], train[1],
                           epochs=epochs, batch_size=batch_size,
                           validation_data=(valid[0], valid[1]),
                           shuffle=True)
        print(f"X: {train[0].shape} Y:{train[1].shape}")

    def save_model(self, src):
        self.model.save(f"{src}")

    def load_model(self, src):
        self.model = load_model(f"{src}")


class FastTextPwdClassifier(PwdClassifier):
    """
    Work bad
    """

    def __init__(self, padding_len, class_num, embedding_dim=50, debug=False):
        super(FastTextPwdClassifier, self).__init__(padding_len, class_num, debug)
        self.embedding_dim = embedding_dim

    def create_model(self):
        """
        create keras model
        :return:
        """
        logging.info("Create Model...")
        model = Sequential()
        model.add(Embedding(self.tokenizer.vocab_size(), self.embedding_dim, input_length=self.padding_len))
        model.add(GlobalAveragePooling1D())
        model.add(Dense(self.class_num, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.summary()
        self.model = model

    def _processing_texts(self, texts):
        """
        Divide the texts to words
        :param texts:
        :return:
        """
        logging.info("pre-processing train data...")
        processed_docs_train = []
        tokenizer = nltk.SyllableTokenizer()
        for doc in tqdm(texts):
            # Remove Space
            doc = doc.replace(' ', '')
            tokens = tokenizer.tokenize(doc)
            processed_docs_train.append(" ".join(tokens))
        return processed_docs_train

    def _fit_words_dict(self, processed_docs_train):
        logging.info("Tokenizing input data...")
        tokenizer = MyTokenizer(num_words=MAX_NB_WORDS, lower=False, char_level=False)
        tokenizer.fit_on_texts(processed_docs_train)
        self.tokenizer = tokenizer

    def _tokenizer_words(self, processed_docs_train):
        """
        Leverage tokenizer to map texts
        :param processed_docs_train: texts
        :return:
        """
        if self.tokenizer is None:
            logging.error('Load or fit tokenizer at first!')
            raise ValueError('Load or fit tokenizer at first!')

        # Process
        word_seq_train = self.tokenizer.texts_to_sequences(processed_docs_train)

        return word_seq_train

    def words2vec(self, texts, labels, fit=True):
        """
        Map raw texts to int vector
        :param texts: [ [], [],..., [] ]
        :param labels:[]
        :param fit: Whether refit the tokenizer
        :return: texts, labels
        """

        # process to word
        texts = self._processing_texts(texts)

        # Load or fit dict()
        if fit:
            self._fit_words_dict(texts)
            self.tokenizer.save_tokenizer(f"D:\\program\\PassAna\\tokenizer\\pwd.pkl")
        else:
            self.tokenizer.load_tokenizer(f"D:\\program\\PassAna\\tokenizer\\pwd.pkl")
        logging.info(f"Dictionary size: {self.tokenizer.vocab_size()}")

        # words to vector
        texts = self._tokenizer_words(texts)

        # padding the cols to padding_len
        texts = sequence.pad_sequences(texts, maxlen=self.padding_len)
        # trans label to label type
        labels = to_categorical(labels)

        return texts, labels


class HASHPwdClassifier(PwdClassifier):
    """
    Work Bad, hash method can not classifier the password and random string.
    """

    def __init__(self, padding_len, class_num, debug=False):
        super(HASHPwdClassifier, self).__init__(padding_len, class_num, debug)

    def create_model(self):
        model = Sequential()
        #
        # model.add(Conv1D(9, 6, padding="same", activation="relu",
        #                  input_shape=(16,1),
        #                  name="conv1"))
        # model.add(Conv1D(5, 4, padding="same", activation="relu",
        #                  name="conv2"))
        # model.add(Flatten())
        # model.add(Dense(256, activation="relu", name="fc1"))
        # model.add(Dense(self.class_num, activation="softmax", name="fc2"))
        #
        # model.compile(loss="mean_squared_error",
        #               optimizer="Adam", metrics=["accuracy", "mse"])  # 配置
        # self.model = model
        model.add(Dense(128, input_dim=32, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(self.class_num, activation="softmax", name="fc2"))

        model.summary()
        model.compile(loss="categorical_crossentropy",
                      optimizer="Adam", metrics=["accuracy"])  # 配置
        self.model = model

    def words2vec(self, texts, labels, hash="SHA256"):
        """
        Transform the password str to vector by hash method. It encode those strings to bit codes and re-decode
        to int number.
        :param texts: Text list or numpy array
        :param labels:
        :param hash: hash methods selected. Now, it supports MD5 and SHA256
        :return:
        """
        if not hash in ['MD5', 'SHA256']:
            logging.error(f"This hash method not support -- {hash}")
            raise ValueError(f"This hash method not support -- {hash}")

        # process to hash
        # 8 bit as an int number
        step = 1
        # for normalize
        base = 2 ** 8
        if hash == 'MD5':
            texts = [hashlib.md5(str.encode(str(i))).digest() for i in texts]

        elif hash == "SHA256":
            texts = [hashlib.sha256(str.encode(str(i))).digest() for i in texts]

        # to vector
        vectors = []
        for text in tqdm(texts):
            # No matter hash method, we decode all of them to 32 length.
            # MD5 has 16 and SHA256 has 32
            vector = np.zeros(32)
            for index, i in enumerate(np.arange(len(text), step=step)):
                vector[index] = int.from_bytes(text[i:i + step], byteorder=sys.byteorder)
            vectors.append(vector)

        # to numpy matrix
        vectors = np.array(vectors) / base
        logging.debug(f'Matrix shape : {vectors.shape}')
        # trans label to label type
        labels = to_categorical(labels)

        return vectors, labels

    @staticmethod
    def data2NNform(X):
        """
        If the training model use the 1D CNN, the form of the X should covert 2D to 3D.
        Like [sample, 32] to [sample, 32, 1]
        :param X:
        :return:
        """
        return X.reshape((X.shape[0], 32, 1))


class NgramPwdClassifier(PwdClassifier):
    def __init__(self, padding_len, class_num, glove_dim=50, debug=False):
        super(NgramPwdClassifier, self).__init__(padding_len, class_num, debug)
        self.tokenizer: MyTokenizer = MyTokenizer(filters='')
        if glove_dim not in [50, 100, 200, 300]:
            logging.error(f'Not support this glove_dim -- {glove_dim}, which must in [50, 100, 200, 300]')
            raise ValueError(f'Not support this glove_dim -- {glove_dim}, which must in [50, 100, 200, 300]')

        self.glove_dim = glove_dim
        self.embedding_matrix = None

    def create_model(self):

        logging.info("Create Model...")
        model = Sequential()
        # model.add(Embedding(self.tokenizer.vocab_size(), self.glove_dim,
        #                     weights=[self.embedding_matrix], input_length=self.padding_len, trainable=False))
        model.add(Conv1D(64, 16, activation='relu', padding="same", input_shape=(self.padding_len, 1)))
        model.add(Dense(64, activation='relu'))
        model.add(Conv1D(32, 16, activation='relu', padding="same"))
        model.add(Dense(64, activation='relu'))
        model.add(Conv1D(16, 8, activation='relu', padding="same"))
        model.add(Flatten())
        model.add(Dense(self.class_num, activation='softmax'))
        model.compile(loss="categorical_crossentropy",
                      optimizer="Adam", metrics=["accuracy"])
        model.summary()
        self.model = model

    def _fit_words_dict(self, processed_docs_train):
        logging.info("Tokenizing input data...")
        tokenizer = MyTokenizer(num_words=MAX_NB_WORDS, lower=False, char_level=False)
        tokenizer.fit_on_texts(processed_docs_train)
        self.tokenizer = tokenizer

    def words2vec(self, texts, labels=None, n=4, fit=True):
        """
        Transform the password and str to vector by n-gran + tokenizer method.
        to int number
        :param texts:
        :param labels:
        :param n: n-gram number, default is 4
        :param fit: if fit the tokenizer. The first time running must set as True.
        :return:
        """
        # to vector
        words = []
        for text in tqdm(texts):
            try:
                text = text.lower().replace("-", '')
                tmp = [text[x:x + y] for y in range(1, n) for x in range(0, len(text))]
                words.append(list(tmp))
            except Exception as e:
                logging.error(f"'{text}' error with {e}")
        texts = words

        # Fit the tokenizer
        if fit:
            self._fit_words_dict(words)
            self.tokenizer.save_tokenizer(f"./tokenizer/pwd.pkl")
        else:
            self.tokenizer.load_tokenizer(f"./tokenizer/pwd.pkl")
        logging.info(f"Dictionary size: {self.tokenizer.vocab_size()}")

        # integer encode the documents
        encoded_docs = self.tokenizer.texts_to_sequences(texts)
        # pad documents to a max length of 4 words
        texts = pad_sequences(encoded_docs, maxlen=self.padding_len, padding='post', truncating='post')
        # trans label to label type
        if labels is not None:
            labels = to_categorical(labels)

        return texts, labels

    def get_matrix_6b(self, src):
        """
        get embedding_matrix from src
        :param src:
        :return:
        """
        # Certain the glove_dim
        path = f"{src}/glove.6B.{self.glove_dim}d.txt"

        # Load glve 6B
        embeddings_index = load_embedding(path)
        # create a weight matrix for words in training docs
        embedding_matrix = np.zeros((self.tokenizer.vocab_size(), self.glove_dim))

        for word, i in self.tokenizer.word_index().items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector
        self.embedding_matrix = embedding_matrix
