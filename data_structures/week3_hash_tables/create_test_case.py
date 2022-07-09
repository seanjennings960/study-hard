import click

@click.command()
@click.option('-t', '--test-case', type=click.Path(exists=False),
               required=True)
@click.option('-a', '--answer-file', type=click.Path(exists=False),
               required=True)
def main(test_case, answer_file):
    garbage1 = 'asdfqwerasdf' * 100
    garbage2 = 'poiupoiupoiupoiulkjlkjlkjlkjpoiupoiu' * 200
    answer_str = 'hellohowareyoudoingimprettylegit'
    s = garbage1 + answer_str + (garbage1 * 2)
    t = garbage2 + answer_str + (garbage2 * 10)

    answer = ' '.join(map(str, [len(garbage1), len(garbage2), len(answer_str)]))

    with open(test_case, 'w') as f:
        f.write(' '.join([s, t]))

    with open(answer_file, 'w') as f:
        f.write(answer)

if __name__ == '__main__':
    main()
