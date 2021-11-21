import io
import sys
from unittest import mock

import pytest

from double_indent import main


def test_main_noop(tmpdir):
    test_input = 'def f(a, b): pass\n'
    test_file = tmpdir.join('test.py')
    test_file.write(test_input)
    assert main([str(test_file)]) == 0
    assert test_file.read() == test_input


def test_main_noop_stdin(tmpdir, capsys):
    test_input = io.TextIOWrapper(io.BytesIO(b'def f(a, b): pass\n'), 'UTF-8')
    with mock.patch.object(sys, 'stdin', test_input):
        assert main(['-']) == 0
    out, _ = capsys.readouterr()
    assert out == 'def f(a, b): pass\n'


def test_main_fixes(tmpdir, capsys):
    test_input = (
        'def f(\n'
        '    a,\n'
        '    b,\n'
        '):\n'
        '    pass\n'
    )
    expected = (
        'def f(\n'
        '        a,\n'
        '        b,\n'
        '):\n'
        '    pass\n'
    )
    test_file = tmpdir.join('test.py')
    test_file.write(test_input)
    main([str(test_file)]) == 1
    _, err = capsys.readouterr()
    assert err == f'Rewriting {test_file}\n'
    assert test_file.read() == expected


def test_main_fixes_stdin(tmpdir, capsys):
    test_input_str = (
        b'def f(\n'
        b'    a,\n'
        b'    b,\n'
        b'):\n'
        b'    pass\n'
    )
    expected = (
        'def f(\n'
        '        a,\n'
        '        b,\n'
        '):\n'
        '    pass\n'
    )
    test_input = io.TextIOWrapper(io.BytesIO(test_input_str), 'UTF-8')
    with mock.patch.object(sys, 'stdin', test_input):
        assert main(['-']) == 1
    out, _ = capsys.readouterr()
    assert out == expected


@pytest.mark.parametrize(
    'arg',
    ('-i', '--indent'),
)
def test_main_fixes_custom_indent(arg, tmpdir, capsys):
    test_input = (
        'def f(\n'
        '  a,\n'
        '  b,\n'
        '):\n'
        '  pass\n'
    )
    expected = (
        'def f(\n'
        '    a,\n'
        '    b,\n'
        '):\n'
        '  pass\n'
    )
    test_file = tmpdir.join('test.py')
    test_file.write(test_input)
    main([str(test_file), arg, '2']) == 1
    _, err = capsys.readouterr()
    assert err == f'Rewriting {test_file}\n'
    assert test_file.read() == expected
