# coding: utf-8
import gzip
import http.client
import io
import json
import os

import ssl
import string
import urllib.parse
from urllib.request import urlopen

import requests
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context


class RemoteAnalyzer(object):
    def __init__(self, bearer=''):
        self.bearer = bearer

    def get_download(self, project_id, language, file_path, threshold=None):
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer}"}

            url = f'https://lgtm.com/api/v1.0/snapshots/{project_id}/{language}'

            file_size = int(urlopen(url).info().get('Content-Length', -1))

            # return if the size over the threshold
            mb_size = file_size / (1024 * 1024)
            if threshold is not None:
                if mb_size > threshold:
                    return

            if os.path.exists(file_path):
                first_byte = os.path.getsize(file_path)  # (3)
            else:
                first_byte = 0
            if first_byte >= file_size: # (4)
                return file_size

            pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=file_path.split('/')[-1])

            req = requests.get(url, headers=headers, stream=True)

            with open(file_path, 'ab') as f:
                for chunk in req.iter_content(chunk_size=1024):     # (6)
                    if chunk:
                        f.write(chunk)
                        pbar.update(1024)

            pbar.close()
        except Exception as e:
            print(e)

    def get_project(self, project):
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.bearer}"}
            conn = http.client.HTTPSConnection("lgtm.com")
            conn.request('GET', f'/api/v1.0/projects/g/{project}', headers=headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode('utf-8'))
            conn.close()
        except Exception as e:
            pass
            conn.close()

        return data['id']

    def get_project_language(self, project):
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.bearer}"}
            conn = http.client.HTTPSConnection("lgtm.com")
            conn.request('GET', f'/api/v1.0/projects/g/{project}', headers=headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode('utf-8'))
            conn.close()
        except Exception as e:
            pass
            conn.close()

        return data['languages']

    def download_dataset(self, filename: str, language, path: str, threshold=None):
        name = filename.split('/')[1]

        if os.path.exists(f'{path}/{name}_{language}.zip'):
            print(f'Skip {filename}')
            return

        project_id = self.get_project(filename)
        self.get_download(project_id, language, f'{path}/{name}_{language}.zip', threshold)



