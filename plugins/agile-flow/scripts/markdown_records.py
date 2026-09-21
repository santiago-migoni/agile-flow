"""Lossless typed sections in authored Markdown; only hidden markers describe types.

Values live in visible prose, never in a second JSON content store. Unknown prose
outside managed sections survives targeted updates. JSON in markers describes a
field key and type, not the functional value.
"""
from __future__ import annotations
import json
import html
import re
from dataclasses import dataclass
from typing import Any

BEGIN = re.compile(r'^<!-- af: (\{.*\}) -->\n', re.M)
END = '<!-- /af -->\n'


@dataclass
class Node:
    key: str
    kind: str
    start: int
    body: int
    end: int
    children: list
    value: Any


def parse_nodes(text: str, position: int = 0, nested: bool = False):
    nodes = []
    while position < len(text):
        begin = BEGIN.search(text, position)
        end = text.find(END, position)
        if nested and end >= 0 and (begin is None or end < begin.start()):
            return nodes, end + len(END)
        if begin is None:
            if nested:
                raise ValueError('Unclosed Markdown field marker.')
            return nodes, len(text)
        meta = json.loads(begin.group(1))
        key, kind = meta['key'], meta['type']
        if not isinstance(key, str) or kind not in {'object', 'array', 'text', 'string-list', 'table', 'number', 'boolean', 'null'}:
            raise ValueError('Invalid Markdown field metadata.')
        heading_end = text.find('\n', begin.end())
        if heading_end < 0 or not text[begin.end():heading_end].startswith('#'):
            raise ValueError('A marked field must have a Markdown heading.')
        body = heading_end + 1
        if kind in {'object', 'array'}:
            children, stop = parse_nodes(text, body, True)
            if len({n.key for n in children}) != len(children):
                raise ValueError('Duplicate Markdown field key.')
            if kind == 'array' and [n.key for n in children] != [str(i) for i in range(len(children))]: raise ValueError('Array field keys must be sequential.')
            value = {n.key: n.value for n in children} if kind == 'object' else [n.value for n in children]
        else:
            stop = text.find(END, body)
            if stop < 0 or BEGIN.search(text, body, stop):
                raise ValueError('Unclosed or nested scalar field.')
            raw = text[body:stop].strip('\n')
            if kind == 'table':
                columns=meta['columns']; schemas=meta['rows']
                lines=[line for line in raw.splitlines() if line.strip()]
                if len(lines)!=len(schemas)+2: raise ValueError('Decision table row count changed; update through the record operation.')
                value=[]
                for line,schema in zip(lines[2:],schemas):
                    if not line.startswith('| ') or not line.endswith(' |'): raise ValueError('Malformed decision table row.')
                    cells=line[2:-2].split(' | ')
                    if len(cells)!=len(columns): raise ValueError('Decision table column count changed.')
                    row={}
                    for column,cell in zip(columns,cells):
                        if column not in schema: continue
                        raw_cell=html.unescape(cell.replace('<br>','\n'))
                        row[column]=raw_cell if schema[column]=='text' else json.loads(raw_cell)
                        if kind_of(row[column])!=schema[column]: raise ValueError('Decision table field type changed.')
                    value.append(row)
            elif kind == 'string-list':
                value=[]
                for line in raw.splitlines():
                    if line.startswith('- '): value.append(line[2:])
                    elif line.startswith('  ') and value: value[-1]+='\n'+line[2:]
                    elif line: raise ValueError('Text list entries must start with a bullet; indent continuations by two spaces.')
            else: value = raw if kind == 'text' else json.loads(raw)
            if kind == 'number' and (isinstance(value, bool) or not isinstance(value, (int, float))):
                raise ValueError('Expected numeric metadata value.')
            if kind == 'boolean' and not isinstance(value, bool):
                raise ValueError('Expected true or false.')
            if kind == 'null' and value is not None:
                raise ValueError('Expected null.')
            children = []
            stop += len(END)
        nodes.append(Node(key, kind, begin.start(), body, stop, children, value))
        position = stop
    if nested:
        raise ValueError('Unclosed Markdown container.')
    return nodes, position


def loads(text: str) -> dict:
    nodes, _ = parse_nodes(text)
    if not nodes or len({n.key for n in nodes}) != len(nodes):
        raise ValueError('Missing or duplicate authoritative Markdown fields.')
    return {n.key: n.value for n in nodes}


def kind_of(value):
    if isinstance(value, dict): return 'object'
    if isinstance(value, list): return 'string-list' if all(isinstance(v,str) for v in value) else 'array'
    if isinstance(value, str): return 'text'
    if isinstance(value, bool): return 'boolean'
    if value is None: return 'null'
    if isinstance(value, (int, float)): return 'number'
    raise ValueError('Unsupported document field type.')


def field(key: str, value: Any, level: int = 2) -> str:
    kind = kind_of(value)
    title = ('Entry '+str(int(key)+1)) if key.isdigit() else key.replace('_', ' ').capitalize()
    metadata={'key':key,'type':kind}
    if key in {'decisions','agreements'} and isinstance(value,list) and value and all(isinstance(row,dict) for row in value):
        kind='table'
        columns=list(dict.fromkeys(k for row in value for k in row))
        preferred=['id','kind','author','reason','scope','source','status','supersedes']
        columns=[k for k in preferred if k in columns]+[k for k in columns if k not in preferred]
        metadata={'key':key,'type':kind,'columns':columns,'rows':[{k:kind_of(v) for k,v in row.items()} for row in value]}
    marker = json.dumps(metadata, ensure_ascii=False)
    start = f'<!-- af: {marker} -->\n{"#" * min(level, 6)} {title}\n\n'
    if kind == 'table':
        def cell(v):
            raw=v if isinstance(v,str) else json.dumps(v,ensure_ascii=False)
            return html.escape(raw,quote=False).replace('|','&#124;').replace('\n','<br>')
        body='| '+' | '.join(k.replace('_',' ').capitalize() for k in columns)+' |\n'
        body+='| '+' | '.join('---' for k in columns)+' |\n'
        for row in value: body+='| '+' | '.join(cell(row[k]) if k in row else '—' for k in columns)+' |\n'
    elif kind in {'object', 'array'}:
        entries = value.items() if kind == 'object' else ((str(i), v) for i, v in enumerate(value))
        body = ''.join(field(k, v, level + 1) for k, v in entries)
    else:
        body = '\n'.join('- '+entry.replace('\n','\n  ') for entry in value) if kind == 'string-list' else (value if kind == 'text' else json.dumps(value))
        if '<!-- af:' in body or '<!-- /af' in body:
            raise ValueError('Reserved document markers cannot appear inside field values.')
        body += '\n'
    return start + body + END + '\n'


def dumps(title: str, data: dict) -> str:
    return f'# {title}\n\n' + ''.join(field(key, value) for key, value in data.items())


def patch(text: str, data: dict, level: int = 2) -> str:
    """Replace changed leaf fields while preserving unchanged text and free notes."""
    nodes, _ = parse_nodes(text)
    known = {n.key for n in nodes}
    edits = []
    for node in nodes:
        if node.key not in data:
            edits.append((node.start, node.end, ''))
        elif node.value != data[node.key]:
            value = data[node.key]
            if node.kind == kind_of(value) and node.kind in {'object', 'array'}:
                mapping = value if isinstance(value, dict) else {str(i): v for i, v in enumerate(value)}
                inner = text[node.body:node.end-len(END)]
                edits.append((node.body, node.end-len(END), patch(inner, mapping, level + 1)))
            else:
                edits.append((node.start, node.end, field(node.key, value, level)))
    for start, end, replacement in reversed(edits):
        text = text[:start] + replacement + text[end:]
    for key, value in data.items():
        if key not in known:
            text += '\n' + field(key, value, level)
    return text
