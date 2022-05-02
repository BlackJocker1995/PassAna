import collections
import math
import os
import pickle
import random
import string

import numpy as np
import scipy
from scipy import stats
from tqdm import tqdm
import pandas as pd
from password_generator import PasswordGenerator

class RandomPasGeneratorLocal(object):
    def __init__(self):
        self.pwo = PasswordGenerator()
        self.pwo.maxlen=50

    def generate(self):
        return self.pwo.generate()

    def generate_muil(self, num):
        passwords = []
        for i in tqdm(range(num)):
            passwords.append(self.generate())
        return pd.DataFrame(passwords)


def _cal_entropy(text):
    counter_char = collections.Counter(text)
    entropy = 0
    for c, ctn in counter_char.items():
        _p = float(ctn)/len(text)
        entropy += -1 * _p * math.log(_p, 2)
    return entropy


def get_entropy(data_df):
    str_data = data_df
    str_data.columns = ['str']
    str_ent = str_data['str'].apply(lambda x: _cal_entropy(x))
    return str_ent


def three_sigma_deduce(src):
    data = pd.read_csv(src)
    str_ent = get_entropy(data)
    data = data[np.abs(stats.zscore(str_ent)) < 3]
    data.to_csv(src, index=False)


def process_found_pass(src, name='pass'):
    """
    remove some str that are not password from pass.csv
    :param src:
    :return:
    """
    data = pd.read_csv(f"{src}/{name}.csv",
                       # on_bad_lines='skip',
                       index_col=0)
    # which has " "(space)
    data = data[(data['str'].str.find(' ') == -1)]
    # which si smaller that 6
    data = data[data['str'].str.len() >= 6]
    # which var name is equaled with its str text
    data = data[~(data['var'].str.lower() == data['str'].str.lower())]

    # process
    data.reset_index(inplace=True)
    data = data.drop(columns='index')
    data = data.drop_duplicates()
    # save
    data.to_csv(f"{src}/{name}.csv")


def generate_random_pass(num):
    """
    generate random password
    :return:
    """
    passwords = []
    pwo = PasswordGenerator()
    pwo.maxlen = 20
    for i in tqdm(range(num)):
        passwords.append(pwo.generate())
    passwords = pd.DataFrame(passwords)
    passwords.to_csv("raw_dataset/random_pass.csv", index=False)


def generate_random_token(num):
    tokens = []
    tmp_char = " ".join(string.ascii_letters + string.digits).split(' ')
    for count in range(32, 64, 2):
        for i in range(num):
            tmp = np.random.choice(tmp_char, size=count, replace=True)
            token = ''.join(tmp)
            tokens.append(token)
    tokens = pd.DataFrame(tokens)
    tokens.to_csv('raw_dataset/tokens.csv', index=False)


def remove_pass_from_string(src):
    """
    clear password in string.csv
    :param src:
    :return:
    """
    # string.csv
    str_text = pd.read_csv(f"{src}/string.csv", index_col=0)
    str_text.columns = ["var", 'str', 'line', 'location', 'project']
    # pass.csv
    pass_text = pd.read_csv(f"{src}/pass.csv", index_col=0)
    pass_text.columns = ["var", 'str', 'line', 'location', 'project']
    # remove the str has same value
    code_list = pass_text['location'].tolist()
    str_text = str_text[~str_text['location'].isin(code_list)]
    # Save
    str_text.to_csv(f"{src}/string.csv")


def merge_and_label():
    nopass_str = pd.read_csv('raw_dataset/nopass_str.csv')
    randowm_pass = pd.read_csv('raw_dataset/random_pass.csv').sample(100000)#, chunksize=100000).get_chunk(100000)
    user_pass = pd.read_csv('raw_dataset/password.csv').sample(100000)#, chunksize=100000).get_chunk(100000)
    tokens = pd.read_csv('raw_dataset/tokens.csv')#.sample(300000)# .sample(00000)#, chunksize=100000).get_chunk(100000)


    data = []
    label = []
    for i, p in zip([0, 1, 1, 2],[nopass_str, randowm_pass, user_pass, tokens]):
        p = p.dropna()
        p = p.to_numpy().reshape(-1).tolist()
        label.extend(np.zeros(len(p), dtype=int) + i)
        data.extend(p)
    data = pd.DataFrame(data, dtype=str)
    label = pd.DataFrame(label, dtype=int)
    with open('dataset/pwd_data.pkl', 'wb') as f:
        pickle.dump(data, f)
    with open('dataset/pwd_label.pkl', 'wb') as f:
        pickle.dump(label, f)


if __name__ == '__main__':
    three_sigma_deduce("../raw_dataset/password.csv")

