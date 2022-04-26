from ql.analyzer import init_analyzer

if __name__ == '__main__':
    language = 'javascript'
    base = '/media/rain/data/other/js'
    analyzer = init_analyzer(language)
    analyzer.get_str_from_projects(base, threads=8, skip=True)
    data = analyzer.merge_csv(base, "findString")
    data.to_csv(f'csv/{language}/string_test.csv')