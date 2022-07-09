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

def parse_test_dir(sol_dir):
    solutions = {}
    test_names = sorted([f.name for f in sol_dir.iterdir() if not f.suffix])
    solutions['test_cases'] = [
        {
            'in': (sol_dir / name).read_text().rstrip(),
            'ans': (sol_dir / f'{name}.a').read_text().rstrip(),
        }
        for name in test_names
    ]
    return solutions


def parse_dir(test_dir: Path, lang: str) -> Tuple[Dict, Path]:
    # Load solutions from yaml
    sol_dir = test_dir / 'tests'
    if not (sol_dir).exists():
        raise click.FileError(str(sol_dir), f'Initialize tests in {test_dir}')

    solutions = parse_test_dir(sol_dir)

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
@click.option('--test-case', type=int, default=None)
@click.option('--suppress-output', is_flag=True, default=False)
def main(test_dir, lang, test_case, suppress_output):
    test_dir = Path(test_dir)
    solutions, code = parse_dir(test_dir, lang)

    if lang == 'rs':
        os.chdir(code)

    for i, case in enumerate(solutions['test_cases']):
        if test_case is not None and i + 1 != test_case:
            continue
        p = run_code(code, lang)
        p.stdin.write(case['in'].encode())
        p.stdin.close()
        computed = b''
        for line in p.stdout:
            computed += line.strip() + b'\n'
        # Remove just the final new line, keep those in the middle.
        computed = computed.decode().strip()

        if computed != case['ans'].strip():
            output = f'Test case {i + 1} failed'
            if not suppress_output:
                output += (f': computed ({computed}) '
                           f'!= ans ({case["ans"]})')
            click.echo(output, err=True)
            return
    click.echo('All test cases passed!')


if __name__ == '__main__':
    main()
