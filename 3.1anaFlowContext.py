import pickle
import numpy as np
from sklearn.model_selection import train_test_split

from context.contextClassifier import CNNClassifierGlove
from context.passFinderContext import extract_context_passfinder_all
from tokenizer.tool import load_pkl

from context.contextTool import split_context_csv_by_project
from ql.analyzer import init_analyzer
import pandas as pd


def anaFlowContext():
    """
    Our flow context
    :return:
    """
    language = 'csharp'
    base = '/media/rain/data/csharp_zip'
    for str_label in ['pass', 'string']:
        analyzer = init_analyzer(language)
        if "string" in str_label:
            analyzer.get_context_for_strs(base, f'csv/{language}/{str_label}.csv', skip=False)
            context_to = analyzer.merge_csv(base, 'context_str')
        else:
            analyzer.get_context_for_passs(base, f'csv/{language}/{str_label}.csv', skip=False)
            context_to = analyzer.merge_csv(base, 'context_pass')
        context_to = context_to.drop(columns="project")
        source = pd.read_csv(f'csv/{language}/{str_label}.csv', index_col=0)
        try:
            out = split_context_csv_by_project(source, context_to)
        except Exception as e:
            print(f"error with {e}")
            continue
        if str_label == "string":
            out.to_csv(f'csv/{language}/mycontext_{str_label}.csv')
        else:
            out.to_csv(f'csv/{language}/mycontext_{str_label}.csv')


def anaFinderContext():
    """
    passFinder Context
    :return:
    """
    language = 'csharp'
    base = '/media/rain/data/csharp_zip'
    extract_context_passfinder_all(
        base,
        language,
        "pass"
    )
    extract_context_passfinder_all(
        base,
        language,
        "string"
    )

if __name__ == '__main__':
    anaFlowContext()

