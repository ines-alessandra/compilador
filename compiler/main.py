from lexer import Lexer
# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    with open('test.kt', 'r') as file:
        code = file.read()

    lexer = Lexer(code)
    lexer.tokenize()
    for token in lexer.list_tokens:
        print(token)

