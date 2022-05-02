import logging
import pickle
import re
from abc import abstractmethod, ABC
from re import finditer

from sklearn.utils import compute_class_weight
import gensim
import nltk
import numpy as np
from gensim.models import Doc2Vec
from keras import Input
from keras.layers import Dense, Conv1D, GlobalMaxPooling1D, MaxPooling1D, Dropout, Flatten, BatchNormalization, LSTM, \
    LeakyReLU
from keras.layers import Embedding
from keras.models import Sequential, Model, load_model
from keras.utils.np_utils import to_categorical
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import text_to_word_sequence
import spacy
from nltk import word_tokenize
from sklearn.neighbors import KNeighborsClassifier

from tokenizer.tool import MyTokenizer, train_valid_split, load_embedding, save_pkl, load_pkl

MAX_NB_WORDS = 10000



def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


class ContextClassifier:
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

    def run(self, train, valid, epochs, batch_size, imbalance=False):
        if self.model is None:
            logging.error('Model is None')
            raise ValueError('Create model at first!')
        logging.info(f"X: {train[0].shape} Y:{train[1].shape}")

        # if sample imbalance
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

    def sklearn_run(self, train):
        self.model.fit(train[0], train[1])

    def words2vec(self, texts, labels=None, fit=True):
        """
        Map raw texts to int vector
        :param texts: [ [], [],..., [] ]
        :param labels:[]
        :param fit: Whether refit the tokenizer
        :return: texts, labels
        """
        logging.info("pre-processing train data...")
        stop = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'

        for i in range(len(texts)):
            tmp_text = re.sub(stop, ' ', texts[i])
            tmp_text = camel_case_split(tmp_text)
            tmp_text = " ".join(tmp_text).lower()
            texts[i] = tmp_text

        if fit:
            self.tokenizer.fit_on_texts(texts)
            self.tokenizer.save_tokenizer("tokenizer/context.pkl")
        else:
            self.tokenizer.load_tokenizer("tokenizer/context.pkl")
        logging.info(f"Dictionary size: {self.tokenizer.vocab_size()}")

        # integer encode the documents
        encoded_docs = self.tokenizer.texts_to_sequences(texts)
        # pad documents to a max length of padding_len words
        texts = pad_sequences(encoded_docs, maxlen=self.padding_len, padding='post', truncating='post')
        # trans label to label type
        if labels is not None:
            labels = to_categorical(labels)

        return texts, labels

    def words2vec_text(self, texts):
        # integer encode the documents
        encoded_docs = self.tokenizer.texts_to_sequences(texts)
        # pad documents to a max length of 128 words
        texts = pad_sequences(encoded_docs, maxlen=self.padding_len, padding='post', truncating='post')

        return texts

    def words2vec_tokenizer(self, texts, fit=True):
        """
        Map raw texts to int vector
        :param texts: [ [], [],..., [] ]
        :param fit: Whether refit the tokenizer
        :return: texts, labels
        """
        logging.info("pre-processing train data...")
        stop = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'

        for i in range(len(texts)):
            tmp_text = re.sub(stop, ' ', texts[i])
            tmp_text = camel_case_split(tmp_text)
            tmp_text = " ".join(tmp_text).lower()
            texts[i] = tmp_text

        if fit:
            self.tokenizer.fit_on_texts(texts)
            self.tokenizer.save_tokenizer("tokenizer/generator.pkl")
        else:
            self.tokenizer.load_tokenizer("tokenizer/generator.pkl")
        logging.info(f"Dictionary size: {self.tokenizer.vocab_size()}")

    def save_model(self, src):
        if isinstance(self.model, KNeighborsClassifier):
            with open(src, 'wb') as f:
                pickle.dump(self.model, f)
        else:
            self.model.save(f"{src}")

    def load_model(self, src):
        if isinstance(self.model, KNeighborsClassifier):
            with open(src, 'rb') as f:
                self.model = pickle.load(f)
        else:
            self.model = load_model(f"{src}")


class CNNClassifierGlove(ContextClassifier, ABC):
    def __init__(self, padding_len, glove_dim=50, debug=False):
        super(CNNClassifierGlove, self).__init__(padding_len, debug)
        if glove_dim not in [50, 100, 200, 300]:
            logging.error(f'Not support this glove_dim -- {glove_dim}, which must in [50, 100, 200, 300]')
            raise ValueError(f'Not support this glove_dim -- {glove_dim}, which must in [50, 100, 200, 300]')

        self.glove_dim = glove_dim
        self.embedding_matrix = None

    def create_model(self):
        """
        create keras model
        :return:
        """

        if self.embedding_matrix is None:
            logging.warning("Get glove 6B matrix at first")
            raise ValueError("Get glove 6B matrix at first")

        logging.info("Create Model...")
        model = Sequential()
        model.add(Embedding(self.tokenizer.vocab_size(), self.glove_dim,
                            weights=[self.embedding_matrix], input_length=self.padding_len, trainable=False))
        model.add(Conv1D(16, 7, activation='relu', padding='same'))
        model.add(MaxPooling1D(2))
        model.add(Conv1D(16, 7, activation='relu', padding='same'))
        model.add(GlobalMaxPooling1D())
        model.add(Dropout(0.2))
        model.add(Dense(2, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.summary()
        self.model = model

    def get_matrix_6b(self, src):
        """
        get embedding_matrix from src
        :param src:
        :param length:
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


class KNNClassifier(ContextClassifier, ABC):
    def __init__(self, padding_len, glove_dim=50, debug=False):
        super(KNNClassifier, self).__init__(padding_len, debug)
        if glove_dim not in [50, 100, 200, 300]:
            logging.error(f'Not support this glove_dim -- {glove_dim}, which must in [50, 100, 200, 300]')
            raise ValueError(f'Not support this glove_dim -- {glove_dim}, which must in [50, 100, 200, 300]')

        self.glove_dim = glove_dim
        self.embedding_matrix = None

    def create_model(self):
        """
        create keras model
        :return:
        """
        self.model = KNeighborsClassifier()

    def get_matrix_6b(self, src):
        """
        get embedding_matrix from src
        :param src:
        :param length:
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


class GAN(ContextClassifier):
    def __init__(self, padding_len, glove_dim=50, debug=False):
        super(GAN, self).__init__(padding_len, debug)
        self.glove_dim = glove_dim
        self.embedding_matrix = None
        self.latent_dim = 200
        self.generator = None
        self.discriminator: Sequential = None
        self.combined: Sequential = None
        self.half_size: Sequential = None

    def create_model(self):
        # Build and compile the discriminator
        self.discriminator = self.build_discriminator()
        self.discriminator.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        # Build the generator
        self.generator = self.build_generator()

        # The generator takes noise as input and generates imgs
        z = Input(shape=(self.latent_dim, 1))
        vector = self.generator(z)

        # For the combined model we will only train the generator
        self.discriminator.trainable = False

        # The discriminator takes generated images as input and determines validity
        validity = self.discriminator(vector)

        # The combined model  (stacked generator and discriminator)
        # Trains the generator to fool the discriminator

        self.combined = Model(z, validity)
        self.combined.compile(loss='binary_crossentropy', optimizer='adam')

    def build_generator(self):
        noise_shape = (self.latent_dim, 1)

        model = Sequential()
        model.add(LSTM(256, input_shape=noise_shape))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(1024))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(self.padding_len, activation='tanh'))

        model.summary()
        noise = Input(shape=noise_shape)
        vector = model(noise)

        return Model(noise, vector)

    def build_discriminator(self):
        model = Sequential()
        model.add(Conv1D(32, 9, padding="same", input_shape=(self.padding_len, 1)))
        model.add(Conv1D(16, 9, padding='same'))
        model.add(MaxPooling1D(3, 3, padding='same'))
        model.add(Conv1D(8, 9, padding='same'))
        model.add(MaxPooling1D(3, 3, padding='same'))
        model.add(Conv1D(2, 9, padding='same'))
        model.add(Flatten())
        model.add(Dropout(0.1))
        model.add(BatchNormalization())  # (批)规范化层
        model.add(Dense(1, activation='sigmoid'))
        model.summary()

        vector = Input(shape=(self.padding_len,))
        validity = model(vector)

        return Model(vector, validity)

    def train(self, pass_data, epochs, batch_size=128, sample_interval=100):
        self.half_size = self.tokenizer.vocab_size() / 2
        # Rescale -1 to 1
        pass_data = (pass_data.astype(np.float32) - self.half_size) / self.half_size
        # str_context = (str_context.astype(np.float32) - self.half_size) / self.half_size

        # Adversarial ground truths
        fake = np.zeros((batch_size, 1))
        valid = np.ones((batch_size, 1))
        # batch_size_p = (batch_size // 4) * 3
        # batch_size_s = (batch_size // 4) * 1
        for epoch in range(epochs):

            # ---------------------
            #  Train Discriminator
            # ---------------------

            # Select a random batch of text
            # idx = np.random.randint(0, pass_data.shape[0], batch_size_p)
            # vectors_1 = pass_data[idx]
            # idx = np.random.randint(0, str_context.shape[0], batch_size_s)
            # vectors_2 = str_context[idx]
            idx = np.random.randint(0, pass_data.shape[0], batch_size)
            vectors = pass_data[idx]

            # merge
            # vectors = np.r_[vectors_1, vectors_2]
            # valid = np.r_[np.ones(batch_size_p), np.zeros(batch_size_s)]

            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))

            # Generate a batch of new texts
            gen_txts = self.generator.predict(noise)
            gen_txts = np.expand_dims(gen_txts, axis=2)

            # Train the discriminator
            d_loss_real = self.discriminator.train_on_batch(vectors, valid)
            d_loss_fake = self.discriminator.train_on_batch(gen_txts, fake)
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

            # ---------------------
            #  Train Generator
            # ---------------------

            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))

            # Train the generator (to have the discriminator label samples as valid)

            g_loss = self.combined.train_on_batch(noise, valid)

            # If at save interval => save generated image samples
            if epoch % sample_interval == 0:
                print("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100 * d_loss[1], g_loss))
                self.print_text()

    def print_text(self):
        r = 10
        noise = np.random.normal(0, 1, (r, self.latent_dim))
        gen_txts = self.generator.predict(noise)
        gen_txts = np.expand_dims(gen_txts, axis=2)

        # Rescale text 0 - 4011
        gen_txts = self.half_size * gen_txts + self.half_size
        gen_txts = np.round(gen_txts)
        gen_txts = gen_txts.astype(int)
        gen_txts = gen_txts.reshape((r, -1))
        text = self.tokenizer.decode_vectors(gen_txts)
        print(text)

    def save_generator(self):
        self.generator.save('model/context/generator.h5')
        save_pkl('model/context/half_size', self.half_size)

    def load_generator(self):
        self.generator = load_model('model/context/generator.h5')
        self.half_size = load_pkl('model/context/half_size')
        self.tokenizer.load_tokenizer("tokenizer/generator.pkl")

    def generator_texts(self, num):
        if self.generator is None:
            raise ValueError("train or load model as first")
        noise = np.random.normal(0, 1, (num, self.latent_dim))
        gen_txts = self.generator.predict(noise)
        gen_txts = np.expand_dims(gen_txts, axis=2)

        # Rescale text
        gen_txts = self.half_size * gen_txts + self.half_size
        gen_txts = np.round(gen_txts)
        gen_txts = gen_txts.astype(int)
        gen_txts = gen_txts.reshape((num, -1))
        text = self.tokenizer.decode_vectors(gen_txts)

        return text
