from passwd.passTool import three_sigma_deduce, generate_random_token

if __name__ == '__main__':
    """
    生成token密码
    """
    generate_random_token(100000)
    three_sigma_deduce("raw_dataset/tokens.csv")