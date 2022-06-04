from __future__ import annotations

import argparse
import ast
import sys
from typing import Sequence

from tokenize_rt import Offset
from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src


def _fix_indent(
        tokens: list[Token],
        start: int,
        end: int,
        indent: int,
        offset: int,
) -> None:
    idx = start
    while idx < end:
        if tokens[idx].name == 'NL':
            if (
                    tokens[idx + 1].name == 'UNIMPORTANT_WS' and
                    len(tokens[idx + 1].src) != (indent * 2) + offset and
                    # another argument must follow
                    (
                        tokens[idx + 2].name == 'NAME' or
                        tokens[idx + 2].name == 'COMMENT' or
                        # if not a named argument, the operator for positional
                        # or named only arguments must follow
                        (
                            tokens[idx + 2].name == 'OP' and
                            (
                                tokens[idx + 2].src == '*' or
                                tokens[idx + 2].src == '**' or
                                tokens[idx + 2].src == '/'
                            )
                        )
                    )
            ):
                new_indent = ' ' * ((indent * 2) + offset)
                tokens[idx + 1] = tokens[idx + 1]._replace(src=new_indent)
            elif tokens[idx + 1].name == 'NAME':
                # was not indented at all
                ws = Token('UNIMPORTANT_WS', src=' ' * ((indent * 2) + offset))
                tokens.insert(idx + 1, ws)
        idx += 1


def _fix_src(contents_text: str, fname: str, indent: int) -> str:
    func_defs: set[Offset] = set()
    tree = ast.parse(contents_text, filename=fname)
    for node in ast.walk(tree):
        if (
                (
                    isinstance(node, ast.FunctionDef) or
                    isinstance(node, ast.AsyncFunctionDef)
                ) and
                _has_args(node)
        ):
            func_defs.add(Offset(node.lineno, node.col_offset))

    tokens = src_to_tokens(contents_text)
    for idx, token in reversed_enumerate(tokens):
        if token.offset in func_defs:
            depth = 0
            i = idx
            while depth or tokens[i].src != ':':
                if tokens[i].src == '(':
                    depth += 1
                elif tokens[i].src == ')':
                    depth -= 1
                i += 1

            multiline_def = tokens[i].line > tokens[idx].line
            if multiline_def:
                _fix_indent(
                    tokens,
                    start=idx,
                    end=i,
                    indent=indent,
                    offset=token.utf8_byte_offset,
                )

    return tokens_to_src(tokens)


def _has_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    if any((
        node.args.posonlyargs,
        node.args.args,
        node.args.kwonlyargs,
    )):
        return True
    else:
        return False


def _fix_file(filename: str, args: argparse.Namespace) -> int:
    if filename == '-':
        contents = sys.stdin.buffer.read().decode(encoding='UTF-8')
    else:
        with open(filename, 'rb') as f:
            contents = f.read().decode(encoding='UTF-8')

    contents_orig = contents_text = contents
    contents_text = _fix_src(contents_text, fname=filename, indent=args.indent)

    if filename == '-':
        print(contents_text, end='')
    elif contents_text != contents_orig:
        print(f'Rewriting {filename}', file=sys.stderr)
        with open(filename, 'wb') as f:
            f.write(contents_text.encode())

    return contents_text != contents_orig


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    parser.add_argument(
        '-i', '--indent',
        default=4,
        type=int,
        help='number of spaces for indentation',
    )
    args = parser.parse_args(argv)
    ret = 0
    for filename in args.filenames:
        ret |= _fix_file(filename, args=args)

    return ret


if __name__ == '__main__':
    raise SystemExit(main())
