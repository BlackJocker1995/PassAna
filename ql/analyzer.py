# coding: utf-8
import json
import logging
import os
import re

import pandas
import pandas as pd
import pexpect
import shutil
from tqdm import tqdm


class Analyzer(object):

    def __init__(self, debug=False):
        # Analyze task handle
        self._analyze_task = None
        # Ql select task handle
        self._ql_task: pexpect.spawn = None
        # Language Type
        self.language_type = None
        # default cmd
        self.cmd = 'cmd'
        # ql replace line about str candidates. Different languages have different value whose details are showed in
        # context_to.ql file
        self.ql_replace = 1

        if debug:
            logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                                level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                                level=logging.INFO)

    def set_cmd(self, cmd):
        """
        set which codeql command will execute
        :param cmd:
        :return:
        """
        if cmd not in ['context_pass', 'context_str', 'findString', 'findPass', 'hardcode']:
            logging.error(f'Not support {cmd}!')
            return
        self.cmd = cmd

    def database_create(self, src, external_cmd=None):
        """
        Create database for a project
        :param src: file path
        :param external_cmd: additional command. For instance, Cpp may use 'make' to build the project.
        :return: True or False
        """

        # If a file has been analyzed
        if os.path.exists(f"{src}/{self.language_type}_database"):
            if os.path.exists(f"{src}/{self.language_type}_database/src.zip"):
                logging.info(f'[{src}] has been analyzed.')
                return False

        # analyze command
        cmd = f"codeql database create " \
              f"{self.language_type}_database --language={self.language_type}"
        if external_cmd is not None:
            cmd.join(f" --command{external_cmd}")
        self._analyze_task = pexpect.spawn(cmd, cwd=src)

        # Start analyze
        while True:
            line = self._analyze_task.readline().decode()
            logging.debug(line)
            if line.startswith('Successfully created database'):
                logging.info(f'Successfully created database')
                return False
            if line.startswith('A fatal error'):
                logging.error(f'A fatal error')
                return False
        return True

    def run_ql_cmd(self, src, skip=False, threads=8):
        """
        Run Ql file to analyze the database
        :param skip:
        :param src: file path
        :param threads: thread for running (default=1)
        """

        if skip and os.path.exists(
                f"{src}/results/getting-started/codeql-extra-queries-{self.language_type}/{self.cmd}.bqrs"):
            logging.info(f' It has been analyzed.')
            return False

        # analyze ql command
        cmd = f"codeql database analyze  " \
              f"{src} ql/{self.language_type}/{self.cmd}.ql " \
              f"--format=csv --output={src}/result.csv --rerun --threads {threads}"

        # background running
        try:
            self._ql_task = pexpect.spawn(cmd, timeout=240)
            while True:
                if not self._ql_task.isalive():
                    logging.info(f"Timeout")
                    shutil.rmtree(src)
                    return False
                line = self._ql_task.readline().decode()
                logging.debug(line)
                if line.startswith('Interpreting results'):
                    logging.info(f'Interpreting results')

                    # Result of csharp named java? That is a fact. I think it is a bug.
                    if self.language_type == "csharp":
                        if not os.path.exists(f'{src}/results/getting-started/codeql-extra-queries-csharp'):
                            os.mkdir(f'{src}/results/getting-started/codeql-extra-queries-csharp')
                        if os.path.exists(f'{src}/results/getting-started/codeql-extra-queries-java'):
                            os.system(f'mv -f {src}/results/getting-started/codeql-extra-queries-java/* '
                                      f'{src}/results/getting-started/codeql-extra-queries-csharp/')
                            shutil.rmtree(f'{src}/results/getting-started/codeql-extra-queries-java')
                    return True
                if line.startswith('A fatal error'):
                    logging.error(f'A fatal error')
                    return False
                if line.startswith('Error: Can only run queries'):
                    logging.error(f'Error: Can only run queries')
                    return False

        except Exception as e:
            logging.info(f"Timeout with {e}")
            # shutil.rmtree(src)
            # logging.info(f"Remove dir {src}")
            return False

    def get_context_for_strs(self, projs_path: str, source_path: str, skip=True):
        """
        find flow context according to csv file (multiple item)
        :param projs_path: projects path
        :param source_path: string csv file
        :return:
        """
        self.set_cmd("context_str")
        csv_data = pandas.read_csv(source_path, index_col=0)
        # group by project
        csv_data_by_group = csv_data.groupby('project')

        # get context in group (project)
        for group, group_item in tqdm(csv_data_by_group):
            logging.info(f"Processing: {group.ljust(50, ' ')}")
            self.get_context_for_str(projs_path, group,
                                     (group_item['var'] + group_item['location']).tolist(),
                                     skip=skip)
            # decode results
            self.decode_bqrs2csv(f"{projs_path}/{group}")

    def get_context_for_passs(self, projs_path: str, source_path: str, skip=True):
        """
            find flow context according to csv file (multiple item)
            :param projs_path: projects path
            :param source_path: string csv file
            :return:
            """
        self.set_cmd("context_pass")
        csv_data = pandas.read_csv(source_path, index_col=0)
        # group by project
        csv_data_by_group = csv_data.groupby('project')

        # get context in group (project)
        for group, group_item in tqdm(csv_data_by_group):
            logging.info(f"Processing: {group.ljust(50, ' ')}")
            self.get_context_for_str(projs_path, group,
                                     (group_item['var'] + group_item['location']).tolist(),
                                     skip=skip)
            # decode results
            self.decode_bqrs2csv(f"{projs_path}/{group}")

    def get_context_for_str(self, proj_path: str, group: str, group_item: list, skip=True):
        """
        ind flow context
        :param proj_path: projs_path: projects path
        :param group: specific project
        :param group_item: all string of specific project
        :return:
        """
        complete_path = proj_path + '/' + group
        # read
        with open(f'ql/{self.language_type}/{self.cmd}.ql', 'r') as f:
            lines = f.readlines()
            ql_code = lines[self.ql_replace]

        # read the ql file to change the pattern that we want to match
        str_array = re.findall('\[.*\]', ql_code)[0]
        new_line = ql_code.replace(str_array, str(group_item).replace("'", '"'))
        lines[self.ql_replace] = new_line

        # replace candidates that we want to get context for
        with open(f'ql/{self.language_type}/{self.cmd}.ql', 'w') as f:
            f.writelines(lines)

        self.run_ql_cmd(complete_path, skip)

    def get_str_from_projects(self, base_path, skip=False, threads=8):
        """
        run ql for all dataset to find string
        :param base_path: dir path
        :param skip: skip if the dataset had been analyzed
        :param threads:
        :return:
        """
        self.set_cmd("findString")
        dirs = tqdm(os.listdir(base_path))

        # list all dir
        for proj_dir in dirs:
            dirs.set_description(f"Processing: {proj_dir.ljust(50, ' ')}")
            # run the ql command
            result = self.run_ql_cmd(f'{base_path}/{proj_dir}', skip=skip, threads=threads)
            # if succeed, decode the bqrs file
            if result:
                self.decode_bqrs2csv(f'{base_path}/{proj_dir}')

    def get_pass_from_projects(self, base_path, skip=False, threads=8):
        """
        run ql for all dataset to find passsword
        :param base_path: dir path
        :param skip: skip if the dataset had been analyzed
        :param threads:
        :return: None
        """
        self.set_cmd("findPass")
        dirs = tqdm(os.listdir(base_path))

        for proj_dir in dirs:
            dirs.set_description(f"Processing: {proj_dir.ljust(50, ' ')}")
            # run the ql command
            result = self.run_ql_cmd(f'{base_path}/{proj_dir}', skip=skip, threads=threads)
            # if succeed, decode the bqrs file
            if result:
                self.decode_bqrs2csv(f'{base_path}/{proj_dir}')

    def get_hardcode_from_projects(self, base_path, skip=False, threads=8):
        """
        run ql for all dataset to find passsword
        :param base_path: dir path
        :param skip: skip if the dataset had been analyzed
        :param threads:
        :return: None
        """
        self.set_cmd("hardcode")
        dirs = tqdm(os.listdir(base_path))

        for proj_dir in dirs:
            dirs.set_description(f"Processing: {proj_dir.ljust(50, ' ')}")
            # run the ql command
            result = self.run_ql_cmd(f'{base_path}/{proj_dir}', skip=skip, threads=threads)
            # if succeed, decode the bqrs file
            if result:
                self.decode_bqrs2csv(f'{base_path}/{proj_dir}')

    def decode_bqrs_all(self, base_path, cmd):
        """
        decode all bqrs in $base_path$
        :param base_path: path
        :param cmd:  kinds of ql command you want to decode e.g., result of [findString, findPass]
        :return:
        """
        self.set_cmd(cmd)
        for proj_dir in tqdm(os.listdir(base_path)):
            self.decode_bqrs2csv(f'{base_path}/{proj_dir}')

    def merge_csv(self, base_path, cmd):
        """
        merge all csv file in $project-home$
        :param base_path:
        :param cmd: kinds of ql command you want to decode e.g., result of [findString, findPass]
        :return:
        """
        # configuration
        self.set_cmd(cmd)
        out = None
        first = True
        dirs = os.listdir(base_path)

        # explore all dir
        for proj_dir in dirs:
            if not os.path.exists(f'{base_path}/{proj_dir}/{cmd}.csv'):
                continue
            # load csv about this project with command "cmd"
            data = Analyzer.load_project_csv(f'{base_path}/{proj_dir}', cmd)
            if self.cmd in ["findPass", "findString"]:
                data.columns = ["var", 'str', 'line', 'location']
            if self.cmd in ["hardcode"]:
                data.columns = ["str", 'location']
            if self.cmd in ["context_str", "context_pass"]:
                try:
                    data.columns = ["var", 'location', 'context']
                except Exception as e:
                    data.columns = ["var", 'location', 'other', 'context']
                    data = data[["var", 'location', 'context']]
            # add project name
            data['project'] = proj_dir

            if first:
                out = data
                first = False
            else:
                out = pd.concat([out, data], ignore_index=True)

        # drop nan
        out = out.dropna()
        out = out.drop_duplicates()

        # more data process according to language
        if self.cmd in ["findPass", "findString"]:
            out = self.external_process(out)

        return out

    def external_process(self, out):
        """
        if have more process
        :param out:
        :return:
        """
        return out

    def decode_bqrs2json(self, src):
        """
        Decode the .bqrs file to json
        :param src:
        :return: result
        """
        path = f"{src}/results/getting-started/codeql-extra-queries-{self.language_type}/{self.cmd}.bqrs"
        # analyze ql command
        cmd = f"codeql bqrs decode --format=json --output={src}/{self.cmd}.json {path}"
        os.system(cmd)

        with open(f'{src}/out.json', 'r') as f:
            out = json.load(f)
        return out

    def decode_bqrs2csv(self, src):
        """
        Decode the .bqrs file to csv
        :param src:
        :return: result
        """
        if self.language_type == "csharp":
            if not os.path.exists(f'{src}/results/getting-started/codeql-extra-queries-csharp'):
                os.mkdir(f'{src}/results/getting-started/codeql-extra-queries-csharp')
            if os.path.exists(f'{src}/results/getting-started/codeql-extra-queries-java'):
                os.system(f'mv -f {src}/results/getting-started/codeql-extra-queries-java/* '
                          f'{src}/results/getting-started/codeql-extra-queries-csharp/')
                shutil.rmtree(f'{src}/results/getting-started/codeql-extra-queries-java')

        path = f"{src}/results/" \
               f"getting-started/codeql-extra-queries-{self.language_type}/{self.cmd}.bqrs"
        if not os.path.exists(path):
            return

        # analyze ql command
        cmd = f"codeql bqrs decode --format=csv --output={src}/{self.cmd}.csv {path}"
        os.system(cmd)

    @staticmethod
    def load_project_csv(src, cmd):
        out = pd.read_csv(f'{src}/{cmd}.csv')
        return out

    @staticmethod
    def clear_csv_cache(base_path, cmd):
        for proj_dir in tqdm(os.listdir(base_path)):
            try:
                path = f'{base_path}/{proj_dir}'
                os.remove(f'{path}/{cmd}.csv')
            except Exception as e:
                continue


def init_analyzer(language, debug=False):
    """
    initializer for language analyzer
    :param language:
    :param debug:
    :return:
    """
    analyzer = {
        "java": JavaAnalyzer(debug),
        "python": PythonAnalyzer(debug),
        "cpp": CppAnalyzer(debug),
        "javascript": JavaScriptAnalyzer(debug),
        "csharp": CsharpAnalyzer(debug)
    }
    return analyzer.get(language)


class JavaAnalyzer(Analyzer):

    def __init__(self, debug):
        super(JavaAnalyzer, self).__init__(debug)
        self.language_type = "java"
        self.ql_replace = 19

    def external_process(self, out: pd.DataFrame):
        out = out[out['str'].str.contains('"')]
        out = out[out['str'].str.len() >= 6]
        out['str'] = out['str'].str.replace('"', '')
        return out


class CppAnalyzer(Analyzer):

    def __init__(self, debug):
        super(CppAnalyzer, self).__init__(debug)
        self.language_type = "cpp"
        self.ql_replace = 15


class PythonAnalyzer(Analyzer):

    def __init__(self, debug):
        super(PythonAnalyzer, self).__init__(debug)
        self.language_type = "python"
        self.ql_replace = 15


class JavaScriptAnalyzer(Analyzer):
    def __init__(self, debug):
        super(JavaScriptAnalyzer, self).__init__(debug)
        self.language_type = "javascript"
        self.ql_replace = 13


class CsharpAnalyzer(Analyzer):
    def __init__(self, debug):
        super(CsharpAnalyzer, self).__init__(debug)
        self.language_type = "csharp"
        self.ql_replace = 13
