import pickle
import nltk
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from context.contextClassifier import GAN


def generator(num, train=True):
    padding_len = 16
    if train:
        pass_context = pd.read_csv('raw_dataset/mycontext_pass.csv')["context"].dropna().to_numpy()
        str_context = pd.read_csv('raw_dataset/mycontext_str.csv')["context"].dropna()
        # str_context = str_context[str_context.str.len() >= 8].to_numpy()
        merge_context = np.r_[pass_context, str_context]

        gan = GAN(padding_len=padding_len)

        gan.words2vec_tokenizer(pass_context, fit=True)

        # to vector
        pass_context = gan.words2vec_text(pass_context)

        # str_context = gan.words2vec_text(str_context)

        # labels = np.r_[np.ones(pass_context.shape), np.zeros(str_context.shape)]

        gan.create_model()

        gan.train(pass_context, epochs=10000, batch_size=32, sample_interval=100)
        gan.save_generator()
        return gan.generator_texts(num)
    else:
        gan = GAN(padding_len=padding_len)
        gan.load_generator()
        return gan.generator_texts(num)


if __name__ == '__main__':
    """
    GAN generator data
    """
    gen_pass_context = generator(10000, True)
    gen_pass_context = pd.DataFrame(gen_pass_context, columns=['context'])
    gen_pass_context = gen_pass_context.dropna()
    gen_pass_context.to_csv('raw_dataset/mycontext_pass_gen.csv', index=False)

    gen_pass_context = pd.read_csv('raw_dataset/mycontext_pass_gen.csv').dropna()
    gen_pass_context.to_csv('raw_dataset/mycontext_pass_gen.csv', index=False)