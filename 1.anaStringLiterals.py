from passwd.passTool import process_found_pass
from ql.analyzer import init_analyzer


def _process_str(text):
    return text.replace('"','').replace(': String','')


def anaPass():
    """
    analyze variable whose name is related to password
    :return:
    """
    language = 'csharp'
    base = '/media/rain/data/csharp_zip'
    analyzer = init_analyzer(language)
    analyzer.get_pass_from_projects(base, threads=8, skip=False)
    data = analyzer.merge_csv(base, "findPass")

    data.to_csv(f'csv/{language}/pass.csv')

    process_found_pass(f'csv/{language}', 'pass')


def anaStr():
    """
    analyze all string literals
    :return:
    """
    language = 'cpp'
    base = '/media/rain/data/other/cpp'
    analyzer = init_analyzer(language)
    analyzer.get_str_from_projects(base, threads=8, skip=False)
    data = analyzer.merge_csv(base, "findString")
    data.to_csv(f'csv/{language}/string_test.csv')


def anaCodeQLDefault():
    """
    analyze hard-coded credentials through Script provided by CodeQL
    :return:
    """
    language = 'java'
    base = '/media/rain/data/e2e_java'
    analyzer = init_analyzer(language)
    analyzer.get_hardcode_from_projects(base, threads=8, skip=False)
    data = analyzer.merge_csv(base, "hardcode")
    data['str'] = data['str'].apply(_process_str)
    data.to_csv(f'csv/{language}/hardcode.csv')


if __name__ == '__main__':
    anaPass()