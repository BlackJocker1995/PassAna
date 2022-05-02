import hashlib
import logging
import sys
from abc import abstractmethod

import nltk
import numpy as np

from keras import metrics
from keras.layers import Dense, GlobalAveragePooling1D, Flatten, Conv2D, Conv1D, MaxPooling1D, GlobalMaxPooling1D, \
    Dropout
from keras.layers import Embedding
from keras.models import Sequential
from keras.preprocessing import sequence
from keras.utils.np_utils import to_categorical
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import text_to_word_sequence
from tensorflow import keras
from tqdm import tqdm
import pandas as pd

from passwd.pwdClassifier import PwdClassifier
from tokenizer.tool import MyTokenizer, train_valid_split, load_embedding

MAX_NB_WORDS = 100000


class PassFinderPassClassifier(PwdClassifier):
    def __init__(self, padding_len, class_num, embedding_dim=50, debug=False):
        super(PassFinderPassClassifier, self).__init__(padding_len, class_num, debug)
        self.embedding_dim = embedding_dim

    def create_model(self):
        """
        create keras model
        :return:
        """
        logging.info("Create Model...")
        model = Sequential()
        model.add(Conv1D(64, 32, activation='relu', padding="same", input_shape=(self.padding_len, 1)))
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

    def _processing_texts(self, texts):
        """
        Divide the texts to words
        :param texts:
        :return:
        """
        logging.info("pre-processing train data...")
        processed_docs_train = []
        for doc in tqdm(texts):
            doc = list(doc)
            processed_docs_train.append(doc)
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

    def words2vec(self, texts, labels=None, fit=True):
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
            self.tokenizer.save_tokenizer(f"tokenizer/PassFinder_token.pkl")
        else:
            self.tokenizer.load_tokenizer(f"tokenizer/PassFinder_token.pkl")
        logging.info(f"Dictionary size: {self.tokenizer.vocab_size()}")

        # words to vector
        texts = self._tokenizer_words(texts)

        # padding the cols to padding_len
        texts = sequence.pad_sequences(texts, maxlen=self.padding_len, padding='post', truncating='post')
        # trans label to label type
        if labels is not None:
            labels = to_categorical(labels)

        return texts, labels