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
        lines_to_check: dict[int, int | None],
) -> None:
    idx = start
    line_to_indent: set[int] = set()
    while idx < end:
        if tokens[idx].name == 'NL':
            if (
                    tokens[idx + 1].name == 'UNIMPORTANT_WS' and
                    len(tokens[idx + 1].src) < (indent * 2) + offset and
                    # another argument must follow
                    (
                        tokens[idx + 2].name == 'NAME' or
                        tokens[idx + 2].name == 'COMMENT' or
                        tokens[idx + 2].name == 'STRING' or
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
                # we indented an argument. We need to check if there is more to
                # to the argument i.e. multiline defaults
                if tokens[idx + 1].line in lines_to_check:
                    end_of_arg = lines_to_check[tokens[idx + 1].line]
                    if end_of_arg is not None:
                        line_to_indent |= set(
                            range(tokens[idx + 1].line, end_of_arg + 1),
                        )
                    else:
                        line_to_indent |= set(
                            range(tokens[idx + 1].line, tokens[end].line - 1),
                        )

            elif tokens[idx + 1].name == 'NAME':
                # was not indented at all
                ws = Token('UNIMPORTANT_WS', src=' ' * ((indent * 2) + offset))
                tokens.insert(idx + 1, ws)
            elif tokens[idx].line in line_to_indent:
                # check if we are between some function args?
                current_indent = tokens[idx + 1].src
                new_indent = current_indent + ' ' * indent
                tokens[idx + 1] = tokens[idx + 1]._replace(src=new_indent)

        idx += 1


def _fix_src(contents_text: str, indent: int) -> str:
    func_defs: set[Offset] = set()
    lines_to_check: dict[int, int | None] = {}
    tree = ast.parse(contents_text)
    for node in ast.walk(tree):
        if (
                (
                    isinstance(node, ast.FunctionDef) or
                    isinstance(node, ast.AsyncFunctionDef)
                ) and any((
                    node.args.posonlyargs,
                    node.args.args,
                    node.args.kwonlyargs,
                ))
        ):
            func_defs.add(Offset(node.lineno, node.col_offset))
            for arg_type in ('args', 'kwonlyargs', 'posonlyargs'):
                for idx, arg in enumerate(getattr(node.args, arg_type)):
                    start = arg.lineno
                    # we are at the last argument, we need to find the end of
                    # the function def instead
                    if idx+1 == len(getattr(node.args, arg_type)):
                        end = None
                    else:
                        end = getattr(node.args, arg_type)[idx + 1].lineno - 1
                    lines_to_check[start] = end

    tokens = src_to_tokens(contents_text)
    for idx, token in reversed_enumerate(tokens):
        if token.offset in func_defs:
            depth = 0
            func_end_idx = idx
            while depth or tokens[func_end_idx].src != ':':
                if tokens[func_end_idx].src == '(':
                    depth += 1
                elif tokens[func_end_idx].src == ')':
                    depth -= 1
                func_end_idx += 1

            multiline_def = tokens[func_end_idx].line > tokens[idx].line

            if multiline_def:
                _fix_indent(
                    tokens,
                    start=idx,
                    end=func_end_idx,
                    indent=indent,
                    offset=token.utf8_byte_offset,
                    lines_to_check=lines_to_check,
                )
                pass

    return tokens_to_src(tokens)


def _fix_file(filename: str, args: argparse.Namespace) -> int:
    if filename == '-':
        contents = sys.stdin.buffer.read().decode()
    else:
        with open(filename, 'rb') as f:
            contents = f.read().decode()

    contents_orig = contents_text = contents
    contents_text = _fix_src(contents_text, indent=args.indent)

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
