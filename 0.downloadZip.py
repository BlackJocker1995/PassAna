import time

from ql.remoteAnalyzer import RemoteAnalyzer

if __name__ == '__main__':
    remote = RemoteAnalyzer()
    for line in open('ql/test/csharp.txt', 'r'):
        repo_name = line.replace('\n', '')

        try:
            remote.download_dataset(repo_name, 'csharp',
                                    '/media/rain/data/other/csharp', threshold=100)
        except Exception as e:
            print('analyzer "{}" error as {}'.format(repo_name, e))
        # time.sleep(0.3)
    ##
    # repo_name = "zhuzhongshu/study_tars"
    # remote.download_dataset(repo_name, 'csharp', '/home/rain/program/test', threshold=100)