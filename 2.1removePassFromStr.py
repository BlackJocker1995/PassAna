import os

import pandas as pd

from passwd.passTool import remove_pass_from_string
"""
从string数据中把password数据删除
"""

if __name__ == '__main__':
    src = "/home/rain/PassAna/csv"
    dirs = os.listdir(src)
    # list all dir
    remove_pass_from_string(f"{src}/csharp")