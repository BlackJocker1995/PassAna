import time

import pandas as pd
import requests


def get_stars_count(repo_name):
    # repo_name = 'ZzzzzZXxxX/yolo3_keras_Flag_Detection'
    url = f'https://api.github.com/search/repositories?q=repo:{repo_name}'
    try:
        r = requests.get(url)
        stargazers_count = ''
        if r.status_code == 200:
            response_dict = r.json()
            if response_dict['total_count'] == 1:
                repo_dicts = response_dict['items']
                stargazers_count = repo_dicts[0]['stargazers_count']
            else:
                stargazers_count = f"{repo_name} is not unique!"
        else:
            print(f'Error with {repo_name} as {r.status_code}')
    except:
        return None
    return stargazers_count

def change_project_name(name):
    split_name = name.split('_')
    last = split_name[-1]
    project_name = name.replace(f"_{last}", '')
    project_name = project_name.replace('_','/',1)
    return project_name

def get_star():
    data = pd.read_csv('raw_dataset/mycontext_pass.csv')
    group_data = data.groupby('project')

    names = []
    for item in group_data:
        project_name = item[0]
        split_name = project_name.split('_')
        last = split_name[-1]
        project_name = project_name.replace(f"_{last}", '')
        project_name = project_name.replace('_','/',1)
        names.append(project_name)

    stars = []
    for name in names:
        stargazers_count = get_stars_count(name)
        if stargazers_count is None:
            continue
        print(f'{name} : {stargazers_count}')
        stars.append(stargazers_count)
        time.sleep(11)
    out = pd.DataFrame(columns=['project','star'])
    out['project'] = names
    out['star'] = stars

    out.to_csv('metrics/star.csv', index=False)


def _concat_context(data):
    """
    merge all context as one array split by the ";"
    :param data:
    :return:
    """
    return pd.DataFrame([{
        "location": ";".join(data["location"].unique()),
        "str": ";".join(data["str"])
    }])


def _contain_text(text):
    text = text.lower()
    if 'test' in text or 'example' in text:
        return 1
    else:
        return 0


def statistics():
    data = pd.read_csv('raw_dataset/mycontext_pass.csv')
    star = pd.read_csv('metrics/star.csv')

    data['project'] = data['project'].apply(change_project_name)

    csv_data_by_group = data.groupby(["project"]).apply(_concat_context).reset_index()

    merge_csv = pd.merge(csv_data_by_group, star, on=['project'])

    merge_csv = merge_csv.dropna()

    test_label = merge_csv['location'].apply(_contain_text)

    merge_csv['test_label'] = test_label

    merge_csv.to_csv('metrics/project_star.csv', index=False)


def dis():

if __name__ == '__main__':
    dis

