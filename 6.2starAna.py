import pandas as pd

if __name__ == '__main__':
    data = pd.read_csv('metrics/project_star.csv')
    data['mark'] = data['mark'].fillna(0)
    test = data[data['test_label'] == 0 ]
    a = test[test['star'] <= 10]
    o = a.shape [0]/ test.shape[0]
    print(o)