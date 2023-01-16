import pytest
from tokenize_rt import src_to_tokens

from double_indent import _find_outer_parens
from double_indent import _fix_src
from double_indent import _is_multiline_def


def test_find_matching_parens():
    f = '''\
def f(
    x = (5, 6),
    x = 6,
):
    pass
'''
    tokens = src_to_tokens(f)
    assert _find_outer_parens(tokens) == (3, 26)


def test_is_multiline_def_true():
    f = '''\
def f(
    x = 5,
    x = 6,
):
    pass
'''
    tokens = src_to_tokens(f)
    assert _is_multiline_def(tokens, 0) is True


def test_is_multiline_def_false():
    f = '''\
def f(x = 5, x = 6):
    pass
'''
    tokens = src_to_tokens(f)
    assert _is_multiline_def(tokens, 0) is False


def test_is_multiline_def_past_end():
    f = '''\
def f(x = 5, x = 6)
'''
    with pytest.raises(AssertionError) as exc_info:
        tokens = src_to_tokens(f)
        _is_multiline_def(tokens, 0)

    assert exc_info.value.args[0] == 'past end'


@pytest.mark.parametrize(
    'src',
    (
        pytest.param(
            'def f(a, b): pass\n',
            id='one line def',
        ),
        pytest.param(
            'def f(\n'
            '    a, b,\n'
            '): pass\n',
            id='args on one line',
            marks=pytest.mark.xfail(reason='no indent multiple args, 1 line'),
        ),
        pytest.param(
            'def f(\n'
            '        a = [\n'
            '            "a",\n'
            '        ],\n'
            '): pass\n',
            id='multiline default args',
        ),
        pytest.param(
            'def f(a, b) -> bool: pass\n',
            id='one line def type annotations',
        ),
        pytest.param(
            'def f(  \n'
            '        a,\n'
            '        b,\n'
            '):pass\n',
            id='correct indentation',
        ),
        pytest.param(
            'def f(\n'
            '        a,\n'
            '        b = 69,\n'
            '): pass\n',
            id='correct indentation with defaults',
        ),
        pytest.param(
            'class x:\n'
            '    def foo(self): pass\n',
            id='one line method def',
        ),
        pytest.param(
            'def f(\n'
            '        a: int,\n'
            '        b: str,\n'
            ') -> bool:\n'
            '    pass\n',
            id='correct def type annotations',
        ),
        pytest.param(
            'def f(\n'
            '        a,\n'
            '        *,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='correct kwarg only',
        ),
        pytest.param(
            'def f(\n'
            '        a,\n'
            '        /,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='correct positional only',
        ),
        pytest.param(
            'def f(\n'
            '        x,\n'
            '        y,\n'
            '):\n'
            '    def ff(\n'
            '            y,\n'
            '    ): pass\n',
            id='correct nested function def',
        ),
        pytest.param(
            'def f():\n'
            '    pass\n',
            id='function without args',
        ),
    ),
)
def test_noop(src):
    assert _fix_src(src, indent=4) == src


@pytest.mark.parametrize(
    ('src', 'exp'),
    (
        pytest.param(
            'def f(\n'
            '    a,\n'
            '    b,\n'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='incorrect indent',
        ),
        pytest.param(
            'def f(\n'
            '    a: str,\n'
            '    b: tuple[int, int],\n'
            ') -> bool:\n'
            '    pass\n',
            'def f(\n'
            '        a: str,\n'
            '        b: tuple[int, int],\n'
            ') -> bool:\n'
            '    pass\n',
            id='incorrect indent with type annotations',
        ),
        pytest.param(
            'def f(\n'
            '    a,\n'
            '    b = call(some),\n'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        b = call(some),\n'
            '):\n'
            '    pass\n',
            id='incorrect indent default call',
        ),
        pytest.param(
            'def f(\n'
            'a,\n'
            'b,\n'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='no existing indentation',
        ),
        pytest.param(
            'def f(\n'
            '    a,\n'
            '    *,\n'
            '    b,\n'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        *,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='incorrect kwarg only',
        ),
        pytest.param(
            'def f(\n'
            '    a,\n'
            '    *,\n'
            '    b,\n'
            '    **kwargs,'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        *,\n'
            '        b,\n'
            '        **kwargs,'
            '):\n'
            '    pass\n',
            id='incorrect kwarg only **kwargs',
        ),
        pytest.param(
            'def f(\n'
            '    a,\n'
            '    b,\n'
            '    *args,'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        b,\n'
            '        *args,'
            '):\n'
            '    pass\n',
            id='incorrect *args',
        ),
        pytest.param(
            'class C:\n'
            '    def f(\n'
            '       self,\n'
            '       y,\n'
            '    ):\n'
            '        pass\n',
            'class C:\n'
            '    def f(\n'
            '            self,\n'
            '            y,\n'
            '    ):\n'
            '        pass\n',
            id='incorrect class method def',
        ),
        pytest.param(
            'def f(\n'
            '    a,\n'
            '    #  comment,\n'
            '    b,\n'
            '):\n'
            '    pass\n',
            'def f(\n'
            '        a,\n'
            '        #  comment,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='comment in function definition',
        ),
        pytest.param(
            'def f(\n'
            '    x,\n'
            '    y,\n'
            '):\n'
            '    def ff(\n'
            '        y,\n'
            '    ): pass\n',
            'def f(\n'
            '        x,\n'
            '        y,\n'
            '):\n'
            '    def ff(\n'
            '            y,\n'
            '    ): pass\n',
            id='nested function def',
        ),
        pytest.param(
            'async def f(\n'
            '    x,\n'
            '    y,\n'
            '):\n'
            '    async def ff(\n'
            '        y,\n'
            '    ): pass\n',
            'async def f(\n'
            '        x,\n'
            '        y,\n'
            '):\n'
            '    async def ff(\n'
            '            y,\n'
            '    ): pass\n',
            id='nested async function def',
        ),
        pytest.param(
            'async def f(\n'
            '    a,\n'
            '    b,\n'
            '):\n'
            '    pass\n',
            'async def f(\n'
            '        a,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='async function def',
        ),
        pytest.param(
            'def f(\n'
            '    a = [\n'
            '        "a",\n'
            '    ],\n'
            '): pass\n',
            'def f(\n'
            '        a = [\n'
            '            "a",\n'
            '        ],\n'
            '): pass\n',
            id='multiline default args are indented',
            marks=pytest.mark.xfail(reason='not implemented yet'),
        ),

    ),
)
def test_fixes(src, exp):
    new = _fix_src(src, indent=4)
    assert new == exp
