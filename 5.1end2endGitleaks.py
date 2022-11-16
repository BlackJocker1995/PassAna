import os
import re
import subprocess
import ast
import numpy as np
import pexpect
from tqdm import tqdm
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
    try:
        # CMD to check using gitleaks
        task = pexpect.spawn("gitleaks detect -v", cwd=file_path, timeout=30, encoding='utf-8')
        result = task.readlines()[9:-2]
        result = "".join(result)
        if len(result) == 0:
            return None
        array = result.split("}\r\n{\r\n")

        array = [arr + "}" for arr in array if not arr.endswith("}\r\n")]
        array = ["{" + arr for arr in array if not arr.startswith("{")]
        dict_array = [ast.literal_eval(arr) for arr in array]
        pd_array = pd.DataFrame(dict_array)
        pd_array = pd_array[["StartLine", "Secret", "File"]]
        pd_array.columns = ["line", "context", "location"]
        pd_array["project"] = file_path.split("/")[-1]
    except Exception as e:
        print("No password leakage.")
        return None
    return pd_array


def check_files(base_path):
    dirs = tqdm(os.listdir(base_path))

    # list all dir
    for proj_dir in dirs:
        dirs.set_description(f"Processing: {proj_dir.ljust(50, ' ')}")
        # run the ql command
        if os.path.exists(f'{base_path}/{proj_dir}/gitleak.csv'):
            continue
        out = check_file(f'{base_path}/{proj_dir}')
        if out is None:
            continue
        out.to_csv(f'{base_path}/{proj_dir}/gitleak.csv', index=False)


def merge_files(base_path):
    dirs = tqdm(os.listdir(base_path))
    out = pd.DataFrame(columns=["line","str","location","project"])
    # list all dir
    for proj_dir in dirs:
        # run the ql command
        if not os.path.exists(f'{base_path}/{proj_dir}/gitleak.csv'):
            continue
        try:
            data = pd.read_csv(f'{base_path}/{proj_dir}/gitleak.csv')
            out = out.merge(data, how='outer')
        except Exception as e:
            continue
    out.to_csv(f'e2e/gitleak.csv', index=False)


def process_csv():
    data = pd.read_csv('e2e/gitleak.csv')
    s_list = ('.c', '.cpp.', '.js', '.py', 'java', '.h', '.cs')
    data = data[data['location'].str.endswith(s_list)]

    data["str"] = data["str"].str.replace("-","")

    data = data.drop_duplicates(keep='first')

    data.to_csv('e2e/gitleak.csv', index=False)


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
    gitleak = pd.read_csv('e2e/gitleak.csv')
    raw = pd.read_csv('e2e/raw.csv')
    tmp_yelp = gitleak
    tmp_raw = raw
    tmp_yelp['gitleak_label'] = np.ones(tmp_yelp.shape[0])

    tmp_raw['location'] = tmp_raw['location'].apply(str_match_my)
    merge = pd.merge(tmp_raw, tmp_yelp, on=['location','str'], how='outer')

    merge['gitleak_label'] = merge['gitleak_label'].fillna(0)
    merge['raw_label'] = merge['raw_label'].fillna(0)

    merge['gitleak_label'].astype(int)
    merge['raw_label'].astype(int)

    merge.to_csv('e2e/gitleaker.csv', index=False)
    
    # gitleak = pd.read_csv('e2e/gitleak.csv')
    # raw = pd.read_csv('e2e/raw.csv')
    # merge = pd.merge(gitleak, raw, on=['str', 'line'], how='outer')
    # 
    # merge['gitleak_label'] = merge['gitleak_label'].fillna(0)
    # merge['raw_label'] = merge['raw_label'].fillna(0)
    # 
    # merge['gitleak_label'].astype(int)
    # merge['raw_label'].astype(int)
    # 
    # merge.to_csv('e2e/gitleaker.csv', index=False)
    

if __name__ == '__main__':
    check_files("/media/rain/data/test/")
    # merge_files("/media/rain/data/test/")
    # process_csv()
    process_label()
