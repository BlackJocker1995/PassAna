import os
import re

import numpy as np
from datasets import tqdm
from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings
import json
import pandas as pd

def get_filelist(path):
    Filelist = []
    for home, dirs, files in os.walk(path):
        for filename in files:
            # 文件名列表，包含完整路径
            Filelist.append(os.path.join(home, filename))
            # # 文件名列表，只包含文件名
    return Filelist


def check_file(file_path):
    file_list = get_filelist(file_path)
    # for file in file_list:
    secrets = SecretsCollection()
    with default_settings():
        secrets.scan_files(*file_list, num_processors=8)
    json_result = secrets.json()

    out_result = []
    out_result.extend(json_result.values())
    out_result = [it[0] for it in out_result]
    return out_result


def check_files(base_path):
    dirs = tqdm(os.listdir(base_path))

    # list all dir
    for proj_dir in dirs:
        dirs.set_description(f"Processing: {proj_dir.ljust(50, ' ')}")
        # run the ql command
        if os.path.exists(f'{base_path}/{proj_dir}/yelp.csv'):
            continue
        out = check_file(f'{base_path}/{proj_dir}')
        out = pd.DataFrame(out)
        out.to_csv(f'{base_path}/{proj_dir}/yelp.csv', index=False)


def merge_files(base_path):
    dirs = tqdm(os.listdir(base_path))
    out = pd.DataFrame(columns=["type", "filename", "hashed_secret", "is_verified", "line_number"])
    # list all dir
    for proj_dir in dirs:
        # run the ql command
        if not os.path.exists(f'{base_path}/{proj_dir}/yelp.csv'):
            continue
        try:
            data = pd.read_csv(f'{base_path}/{proj_dir}/yelp.csv')
            out = out.merge(data, how='outer')
        except Exception as e:
            continue
    out.to_csv(f'e2e/yelp.csv', index=False)


def process_csv():
    data = pd.read_csv('e2e/yelp.csv')
    s_list = ('.c','.cpp.','.js','.py','java','.h','.cs')
    data = data[data['filename'].str.endswith(s_list)]
    data.to_csv('e2e/yelp.csv', index=False)


def str_match_yelp(str_name):
    out = re.findall('/media/rain/data/test/(.*)', str_name)[0]
    outsplit = out.split('/')[1:]
    out = '/'.join(outsplit)
    return out


def str_match_my(str_name):
    try:
        out = re.findall('.*opt/src/(.*\.\w+)', str_name)
        if len(out) == 0:
            out = re.findall('.*opt/(.*\.\w+)', str_name)
        out = out[0]
    except:
        out = str_name
    return out


def process_label():
    yelp = pd.read_csv('e2e/yelp.csv')
    raw = pd.read_csv('e2e/raw.csv')
    tmp_yelp = yelp
    tmp_raw = raw
    tmp_yelp['filename'] = tmp_yelp['filename'].apply(str_match_yelp)
    tmp_yelp = tmp_yelp.rename(columns={'filename': 'location'})
    tmp_yelp['yelp_label'] = np.ones(tmp_yelp.shape[0])

    tmp_raw['location'] = tmp_raw['location'].apply(str_match_my)
    merge = pd.merge(tmp_raw, tmp_yelp, on='location', how='outer')

    merge['yelp_label'] = merge['yelp_label'].fillna(0)
    merge['raw_label'] = merge['raw_label'].fillna(0)

    merge['yelp_label'].astype(int)
    merge['raw_label'].astype(int)

    merge.to_csv('e2e/yelper.csv', index=False)

if __name__ == '__main__':
    check_files("/media/rain/data/test/")
    process_csv()
    process_label()
