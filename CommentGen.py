import pyperclip


def comment_gen(add):
    comment = f' {input("Give comment >> ").upper()} '

    while len(comment) <= 116:
        comment = f'{add}{comment}{add}'
    pyperclip.copy(f'# {comment}')
    print('Comment copied to clipboard.\n')


while True:
    style = input('Give comment style >> ').strip()
    if style == '':
        comment_gen('=')
    else:
        comment_gen(style)
