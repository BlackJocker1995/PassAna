import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report


def draw_map(cf_matrix, label):
    ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True,
                     fmt='.2%', cmap='Blues')

    ax.set_xlabel('Predicted Label',fontsize=16)
    ax.set_ylabel('True Label',fontsize=16)

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(label)
    ax.yaxis.set_ticklabels(label)

def metric(approach):
    cad = pd.read_csv(f'e2e/{approach}.csv')

    first = cad['first'].to_numpy()
    second = cad['second'].to_numpy()

    Y = cad['raw_label'].to_numpy()
    y_pred = np.minimum(first, second)

    matrix = confusion_matrix(Y, y_pred)
    # draw_map(matrix, ['Ordinary', 'Password'])
    # plt.show()
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)


def metric_yelp():
    cad = pd.read_csv(f'e2e/yelper.csv')

    Y = cad['raw_label'].to_numpy()
    y_pred = cad['yelp_label'].to_numpy()

    matrix = confusion_matrix(Y, y_pred)
    #draw_map(matrix, ['Ordinary', 'Password'])
    #plt.show()
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)


def metric_codeql():
    cad = pd.read_csv(f'e2e/codeql.csv')

    Y = cad['raw_label'].to_numpy()
    y_pred = cad['codeql'].to_numpy()

    matrix = confusion_matrix(Y, y_pred)
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)


def metric_java():
    cad = pd.read_csv(f'e2e/raw_language.csv')
    cad = cad[cad['language'] == 'java']
    first = cad['first'].to_numpy()
    second = cad['second'].to_numpy()

    Y = cad['raw_label'].to_numpy()
    y_pred = np.minimum(first, second)

    matrix = confusion_matrix(Y, y_pred)
    # draw_map(matrix, ['Ordinary', 'Password'])
    # plt.show()
    print(matrix)

    m = classification_report(Y, y_pred, digits=4)
    print(m)


if __name__ == '__main__':

    # metric('checker')
    # metric('finder')
    # metric_yelp()
    metric_codeql()
    # metric_java()
