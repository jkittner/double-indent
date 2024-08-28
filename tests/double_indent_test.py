import pytest

from double_indent import _fix_src


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
            '        *,\n'
            '        a,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='correct kwarg only as first arg',
        ),
        pytest.param(
            'def f(\n'
            '        *,\n'
            '        a,\n'
            '        b,\n'
            '):\n'
            '    pass\n',
            id='correct posonly as first arg',
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
        pytest.param(
            'def f(\n'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '        z=1,\n'
            '): pass\n',
            id='function with multiline default',
        ),
        pytest.param(
            'def f(\n'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '        *,\n'
            '        z=1,\n'
            '): pass\n',
            id='function with multiline default, kwonly',
        ),
        pytest.param(
            'def f(\n'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '        /,\n'
            '        z=1,\n'
            '): pass\n',
            id='function with multiline default, posonly',
        ),
        pytest.param(
            'def f(\n'
            '        a: str,\n'
            '        b: dict[\n'
            '            str, \n'
            '            str, \n'
            '        ]\n,'
            '): pass\n',
            id='function has multiline type annotation',
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
            '    x=y(\n'
            '        foo=bar,\n'
            '    ),\n'
            '    z=1,\n'
            '): pass\n',
            'def f(\n'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '        z=1,\n'
            '): pass\n',
            id='function with multiline default',
        ),
        pytest.param(
            'def f(\n'
            '    z=1,\n'
            '    x=y(\n'
            '        foo=bar,\n'
            '    ),\n'
            '): pass\n',
            'def f(\n'
            '        z=1,\n'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '): pass\n',
            id='function with multiline default last arg',
        ),
        pytest.param(
            'def f(\n'
            '    z=1,\n'
            '    *\n,'
            '    x=y(\n'
            '        foo=bar,\n'
            '    ),\n'
            '): pass\n',
            'def f(\n'
            '        z=1,\n'
            '        *\n,'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '): pass\n',
            id='function with multiline default, kwonlyargs',
        ),
        pytest.param(
            'def f(\n'
            '    z=1,\n'
            '    /\n,'
            '    x=y(\n'
            '        foo=bar,\n'
            '    ),\n'
            '): pass\n',
            'def f(\n'
            '        z=1,\n'
            '        /\n,'
            '        x=y(\n'
            '            foo=bar,\n'
            '        ),\n'
            '): pass\n',
            id='function with multiline default, posonly',
        ),
        pytest.param(
            'def f(\n'
            '    a: str,\n'
            '    b: dict[\n'
            '        str, \n'
            '        str, \n'
            '    ]\n,'
            '): pass\n',
            'def f(\n'
            '        a: str,\n'
            '        b: dict[\n'
            '            str, \n'
            '            str, \n'
            '        ]\n,'
            '): pass\n',
            id='function with multiline type annotation',
        ),
    ),
)
def test_fixes(src, exp):
    new = _fix_src(src, indent=4)
    assert new == exp
