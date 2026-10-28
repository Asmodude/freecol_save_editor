"""Opt-in read-only FreeCol production probe runner.

Usage:
 py tools/run_hammer_probe.py --jar "C:\\path\\to\\freecol.jar" --save "C:\\path\\to\\Morten.fsg"

Requires javac/java in PATH. Invokes a separate Java process with a temporary
COPY of the save; original file is SHA-256 verified before and after.
Never changes Qt state or exports a save.
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def run(jar, source, timeout=90):
    jar, source = Path(jar).resolve(), Path(source).resolve()
    if not jar.is_file() or not source.is_file():
        raise ValueError('FreeCol JAR and .fsg save must both exist')
    project = Path(__file__).resolve().parents[1]
    java_source = project / 'tools' / 'java' / 'HammerProductionProbe.java'
    if not java_source.is_file():
        raise ValueError('Java probe source not found')
    before = sha256(source)
    with tempfile.TemporaryDirectory(prefix='freecol-hammers-') as tmp:
        temporary = Path(tmp)
        copied = temporary / 'probe.fsg'
        shutil.copy2(source, copied)
        classpath = str(jar) + __import__('os').pathsep + str(jar.parent / 'lib' / '*')
        compile_result = subprocess.run(
            ['javac', '-cp', classpath, '-d', str(temporary), str(java_source)],
            capture_output=True, text=True, timeout=timeout, check=False)
        if compile_result.returncode:
            raise RuntimeError('FreeCol bridge compilation failed:\n' + compile_result.stderr)
        java_result = subprocess.run(
            ['java', '-cp', str(temporary) + __import__('os').pathsep + classpath,
             'HammerProductionProbe', str(copied)],
            capture_output=True, text=True, timeout=timeout, check=False)
        if java_result.returncode:
            raise RuntimeError('FreeCol bridge execution failed:\n' + java_result.stderr)
        if sha256(copied) != before:
            raise RuntimeError('The probe changed its temporary save copy')
        if sha256(source) != before:
            raise RuntimeError('The original save changed during the probe')
        return java_result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', required=True, help='Matching FreeCol freecol.jar')
    parser.add_argument('--save', required=True, help='Original .fsg save (read-only)')
    parser.add_argument('--timeout', type=int, default=90)
    args = parser.parse_args()
    try:
        output = run(args.jar, args.save, args.timeout)
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print('Hammers probe unavailable:', exc, file=sys.stderr)
        return 1
    print(output, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
