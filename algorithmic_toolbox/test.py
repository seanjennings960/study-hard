import os
from typing import Dict, Tuple
from subprocess import Popen, PIPE
from pathlib import Path
import yaml
import click


def verify_unique(files, test_dir, msg):
    if not files:
        raise click.UsageError(f'Could not find {msg} in dir {test_dir}')
    if len(files) != 1:
        raise click.UsageError(f'Found multiple {msg}s in dir {test_dir}.')

def detect_py(test_dir):
    files = [f for f in test_dir.iterdir() if f.is_file()]
    files = list(filter(lambda f: f.suffix == '.py', files))
    verify_unique(files, test_dir, 'python files')
    return files[0]

def detect_rs(test_dir):
    dirs = [d for d in test_dir.iterdir() if d.is_dir()]
    dirs = list(filter(lambda d: (d / 'Cargo.toml').exists(), dirs))
    verify_unique(dirs, test_dir, 'rust project')
    return dirs[0]

def parse_dir(test_dir: Path, lang: str) -> Tuple[Dict, Path]:
    # Load solutions from yaml
    sol_file =test_dir / 'solutions.yaml'
    if not (sol_file).exists():
        raise click.FileError(sol_file, f'Initialize solutions.txt in {test_dir}')
        # raise ValueError
    with open(sol_file, 'rb') as f:
        solutions = yaml.load(f, Loader=yaml.loader.BaseLoader)

    if lang == 'py':
        code = detect_py(test_dir)
    elif lang == 'rs':
        code = detect_rs(test_dir)

    # Autoparse for python file.
    return solutions, code

def run_code(code, lang):
    kwargs = {'stdin': PIPE, 'stdout': PIPE}
    if lang == 'py':
        return Popen(['python3', code], **kwargs)
    elif lang == 'rs':
        return Popen(['cargo', 'run'], **kwargs)
    raise ValueError


@click.command()
@click.argument('test-dir', type=click.Path(exists=True),
                required=True)
@click.option('--lang', type=click.Choice(['py', 'rs']), default='py')
def main(test_dir, lang):
    test_dir = Path(test_dir)
    solutions, code = parse_dir(test_dir, lang)

    if lang == 'rs':
        os.chdir(code)

    for i, case in enumerate(solutions['test_cases']):
        p = run_code(code, lang)
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
