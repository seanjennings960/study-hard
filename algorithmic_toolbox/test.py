from typing import Dict, Tuple
from subprocess import Popen, PIPE
from pathlib import Path
import yaml
import click


def parse_dir(test_dir: Path) -> Tuple[Dict, Path]:
    # Load solutions from yaml
    sol_file =test_dir / 'solutions.yaml'
    if not (sol_file).exists():
        raise click.FileError(sol_file, f'Initialize solutions.txt in {test_dir}')
        # raise ValueError
    with open(sol_file, 'rb') as f:
        solutions = yaml.load(f, Loader=yaml.loader.BaseLoader)

    # Autoparse for python file.
    files = [f for f in test_dir.iterdir() if f.is_file()]
    files = list(filter(lambda f: f.suffix == '.py', files))
    if not files:
        raise click.UsageError(f'Could not find python file in dir {test_dir}')
    if len(files) != 1:
        raise click.UsageError(f'Found multiple python files in dir {test_dir}.')
    return solutions, files[0]

@click.command()
@click.argument('test-dir', type=click.Path(exists=True),
                required=True)
def main(test_dir):
    test_dir = Path(test_dir)
    solutions, code = parse_dir(test_dir)

    for i, case in enumerate(solutions['test_cases']):
        p = Popen(['python3', code], stdin=PIPE, stdout=PIPE)
        p.stdin.write(case['in'].encode())
        p.stdin.close()
        computed = b''
        for line in p.stdout:
            computed += line.strip() + b'\n'
        # Remove just the final new line, keep those in the middle.
        computed = computed.decode().strip()

        if computed != case['ans'].strip():
            click.echo(f'Test case {i} failed: computed ({computed}) '
                       f'!= ans ({case["ans"]})', err=True)
            return
    click.echo('All test cases passed!')


if __name__ == '__main__':
    main()
