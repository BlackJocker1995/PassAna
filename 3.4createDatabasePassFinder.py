from sklearn.model_selection import train_test_split

from context.contextTool import merge_and_label
from tokenizer.tool import load_pkl, save_pkl


def split_train_and_test():
    X = load_pkl('./dataset/passfinder_context_data.pkl').to_numpy().reshape(-1)
    Y = load_pkl('./dataset/passfinder_context_label.pkl').to_numpy().reshape(-1)

    X, X_t, Y, Y_t = train_test_split(X, Y, stratify=Y, test_size=0.1)

    save_pkl('./dataset/passfinder_context_train_data.pkl', X)
    save_pkl('./dataset/passfinder_context_train_label.pkl', Y)

    save_pkl('./dataset/passfinder_context_test_data.pkl', X_t)
    save_pkl('./dataset/passfinder_context_test_label.pkl', Y_t)

if __name__ == '__main__':
    merge_and_label('passfinder')
    split_train_and_test()