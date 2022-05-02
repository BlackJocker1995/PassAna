import hashlib
import logging
import os.path
import re

import zipfile
from keras.layers import Dense, GlobalAveragePooling1D, Flatten, Conv2D, Conv1D, MaxPooling1D, GlobalMaxPooling1D, \
    Dropout, Embedding
from keras.models import Sequential
from keras.preprocessing import sequence
from keras.utils.np_utils import to_categorical
from tensorflow import keras
from tqdm import tqdm
import pandas as pd

from passwd.pwdClassifier import PwdClassifier
from tokenizer.tool import MyTokenizer, train_valid_split, load_embedding

MAX_NB_WORDS = 100000


class PassFinderContextClassifier(PwdClassifier):
    def __init__(self, padding_len, embedding_dim=100, debug=False):
        super(PassFinderContextClassifier, self).__init__(padding_len, debug)
        self.embedding_dim = embedding_dim

    def create_model(self):
        """
        create keras model
        :return:
        """
        logging.info("Create Model...")
        model = Sequential()
        # model.add(Embedding(self.tokenizer.vocab_size() + 1, self.embedding_dim, input_shape=(self.padding_len, 1)))
        model.add(Conv1D(16, 9, activation='relu', padding="same",input_shape=(self.padding_len, 1)))
        # model.add(Conv1D(32, 16, activation='relu', padding="same"))
        model.add(Dense(64, activation='relu'))
        model.add(Conv1D(8, 9, activation='relu', padding="same"))
        model.add(Dense(64, activation='relu'))
        model.add(Conv1D(4, 9, activation='relu', padding="same"))
        model.add(Flatten())
        model.add(Dense(2, activation='softmax'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=["acc"])
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
        stop = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        for doc in tqdm(texts):
            tmp_text = re.sub(stop, ' ', doc)
            doc = list(tmp_text)
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
            self.tokenizer.save_tokenizer(f"tokenizer/PassFinder_context_token.pkl")
        else:
            self.tokenizer.load_tokenizer(f"tokenizer/PassFinder_context_token.pkl")
        logging.info(f"Dictionary size: {self.tokenizer.vocab_size()}")

        # words to vector
        texts = self._tokenizer_words(texts)

        # padding the cols to padding_len
        texts = sequence.pad_sequences(texts, maxlen=self.padding_len, padding='post', truncating='post')
        # trans label to label type
        if labels is not None:
            labels = to_categorical(labels)

        return texts, labels


def merge_passfinder_context(src, passorstr):
    dirs = os.listdir(src)

    merge_out = pd.DataFrame(columns=["var","str","line","location","project","context"])
    # explore all dir
    for proj_dir in dirs:
        if not os.path.exists(f'{src}/{proj_dir}/passFindercontext_{passorstr}.csv'):
            continue
        try:
            data = pd.read_csv(f'{src}/{proj_dir}/passFindercontext_{passorstr}.csv', index_col=0,encoding = "ISO-8859-1")
        except Exception as e:
            print(e)
        data = _process_text(data)
        merge_out = pd.concat([merge_out, data])
    return merge_out


def _process_text(data: pd.DataFrame):
    data = data.dropna()
    data["context"] = data["context"].apply(_reduce_space)
    return data


def _reduce_space(text):
    try:
        cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z]")
        tmp_text = cop.sub(" ", text)
        out_text = " ".join(tmp_text.split())
    except Exception as e:
        print()
    return out_text


def pass_finder_context(projs_path: str, source_path: str, out_path):
    csv_data = pd.read_csv(source_path, index_col=0)
    # group by project
    csv_data_by_group = csv_data.groupby('project')

    contexts = []
    # get context in group (project)
    for group, group_item in tqdm(csv_data_by_group):
        project = f"{projs_path}/{group}"
        locations = group_item['location'].tolist()
        lines = group_item['line'].tolist()

        if not os.path.exists(f'{project}/src.zip'):
            logging.info(f"{project} not esixt")
            continue

        archive = zipfile.ZipFile(f'{project}/src.zip', 'r')
        for line, location in zip(lines, locations):
            # find text
            local_location = location.replace("file://", "").split(":")[0][1:]
            try:
                texts = archive.read(local_location)
                texts = texts.decode("utf-8").split('\n')
            except Exception as e:
                logging.error(f"Error with read {local_location} : {e}")
                continue
            # set index
            mid_line = int(line) - 1
            max_line = len(texts)
            button_line = max(mid_line - 6, 0)
            top_line = min(mid_line + 6, max_line)
            # context
            local_context = texts[button_line:top_line]
            local_context = ''.join(local_context)
            local_context = local_context.replace("\r"," ")

            contexts.append([line, location, local_context])
    contexts = pd.DataFrame(contexts, columns=["line", "location", "context"])
    # merge context
    source_csv = pd.read_csv(source_path, index_col=0)
    out_csv = pd.merge(source_csv,contexts, on=["line", "location"])
    out_csv.to_csv(out_path)


def extract_context_passfinder_all(project_path, language, passorstr):
    pass_finder_context(
        project_path,
        f"csv/{language}/{passorstr}.csv",
        f"csv/{language}/passFindercontext_{passorstr}.csv"
    )

if __name__ == '__main__':
    # pass_finder_context(
    #     '/home/rain/program/python',
    #     '/home/rain/program/python/pass.csv',
    #     "/home/rain/PassAna/csv/python/passFinder_pass_context.csv"
    # )

    # java
    # pass_finder_context(
    #     '/home/rain/program/tmp',
    #     '/home/rain/program/tmp/pass.csv',
    #     "/home/rain/PassAna/csv/java/passFinder_pass_context.csv"
    # )
    # cpp
    # pass_finder_context(
    #     '/home/rain/program/cpp',
    #     '/home/rain/program/cpp/pass.csv',
    #     "/home/rain/PassAna/csv/cpp/passFinder_pass_context.csv"
    # )
    pass_finder_context(
        '/home/rain/program/csharp',
        '/home/rain/program/csharp/string.csv',
        "/home/rain/PassAna/csv/csharp/passFinder_str_context.csv"
    )