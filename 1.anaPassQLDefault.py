from passwd.passTool import process_found_pass
from ql.analyzer import init_analyzer


def process_str(text):
    return text.replace('"','').replace(': String','')

if __name__ == '__main__':
    language = 'java'
    base = '/media/rain/data/e2e_java'
    analyzer = init_analyzer(language)
    # analyzer.get_hardcode_from_projects(base, threads=8, skip=False)
    data = analyzer.merge_csv(base, "hardcode")
    data['str'] = data['str'].apply(process_str)
    data.to_csv(f'csv/{language}/hardcode.csv')
    #
    # process_found_pass(f'csv/{language}', 'hardcode')