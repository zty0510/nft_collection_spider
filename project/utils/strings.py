

def normalize_chinese(sentence):
    """
    全角转半角
    :param sentence:
    :return:
    """
    result = []
    for word in sentence:
        code_point = ord(word)
        if code_point == 12288:
            code_point = 32
        elif 65374 >= code_point >= 65281:
            code_point -= 65248
        result.append(code_point)
    return ''.join(map(chr, result))


