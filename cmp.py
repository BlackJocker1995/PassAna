import numpy as np
import pandas as pd


def change_name(cad:pd.DataFrame, tpye):
    first = cad['first'].to_numpy()
    second = cad['second'].to_numpy()

    y_pred = np.minimum(first, second)
    cad.drop(labels=["first", "second", "line"], axis=1, inplace=True)
    cad[f"{tpye}_label"] = y_pred
    return cad


if __name__ == '__main__':
    checker = pd.read_csv('e2e/checker.csv')
    finder = pd.read_csv('e2e/finder.csv')

    checker = change_name(checker, 'checker')
    finder = change_name(finder, 'finder')

    merge_data = pd.merge(checker, finder, on=["var", "location"])
    merge_data.to_csv('e2e/merge.csv', index=False)