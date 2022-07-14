import click
import pathlib


def _right_nodes(n):
    lines = [f'{i} -1 {i + 1}' for i in range(n - 1)]
    return lines + [f'{n} -1 -1']


def test_case_1():
    n = 100000
    lines = [str(n)]
    lines += _right_nodes(n)
    return '\n'.join(lines), 'CORRECT'


def test_case_2():
    n = 100000
    lines = [str(n)]
    lines += _right_nodes(n)
    lines[10001] = '0 -1 10001'
    return '\n'.join(lines), 'INCORRECT'


def test_case_3():
    n = 100000
    lines = [str(n)]
    lines += _right_nodes(n)
    # Node 10000
    lines[10001] = '9999 -1 10001'
    return '\n'.join(lines), 'CORRECT'


def test_case_4():
    n = 100000
    lines = [str(n)]
    lines += _right_nodes(n - 1)
    # Node 10000
    lines[10001] = f'9999 {n - 1} 10001'
    # Add equal value in left node
    lines += [f'9999 -1 -1']
    return '\n'.join(lines), 'INCORRECT'


TEST_CASES = [test_case_1, test_case_2, test_case_3, test_case_4]

@click.command()
@click.option('-f', '--filename', type=click.Path(),
              required=True)
@click.option('-t', '--test-case', type=click.IntRange(0, len(TEST_CASES) - 1),
              default=0)
def main(filename, test_case):
    if pathlib.Path(filename).exists():
        raise ValueError(f'Path {filename} already exists. Please delete.')
    out, ans = TEST_CASES[test_case]()
    with open(filename, 'w') as f:
        f.write(out)
    with open(filename + '.a', 'w') as f:
        f.write(ans)

    click.echo(f'Successfully wrote test case {filename}, '
               f'answer {filename}.a')

if __name__ == '__main__':
    main()
