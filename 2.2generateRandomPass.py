from passwd.passTool import generate_random_pass, three_sigma_deduce

if __name__ == '__main__':
    """
    生成随机密码
    """
    generate_random_pass(1000000)
    three_sigma_deduce("raw_dataset/random_pass.csv")