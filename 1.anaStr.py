from ql.analyzer import init_analyzer

if __name__ == '__main__':
    language = 'cpp'
    base = '/media/rain/data/other/cpp'
    analyzer = init_analyzer(language)
    analyzer.get_str_from_projects(base, threads=8, skip=False)
    data = analyzer.merge_csv(base, "findString")
    data.to_csv(f'csv/{language}/string_test.csv')