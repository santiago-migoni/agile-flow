"""Approved editorial sections backed by visible Markdown fields.

The template JSON contains layout rules only. Every functional value lives once
in Markdown; bookkeeping fields remain visible in a collapsed details section.
"""
from __future__ import annotations
import json
from pathlib import Path
try:
    from . import markdown_records as md
except ImportError:
    import markdown_records as md

LAYOUTS = Path(__file__).resolve().parents[1] / 'templates' / 'legacy' / 'documents.json'


def unpack(text):
    groups = md.loads(text)
    data = {}
    for values in groups.values():
        if not isinstance(values, dict): raise ValueError('Template section must contain fields.')
        for path, value in values.items():
            parts = path.split('/')
            obj = data
            for part in parts[:-1]:
                if not isinstance(obj.setdefault(part, {}), dict): raise ValueError('Conflicting field paths.')
                obj = obj[part]
            if parts[-1] in obj: raise ValueError('Duplicate authored field.')
            obj[parts[-1]] = value
    return data


def flat(data):
    # Keep record lists and structured prose intact; flatten the document wrapper.
    out = {}
    for key, value in data.items():
        if isinstance(value, dict) and key in {'project','item','iteration','release'}:
            for field, content in value.items():
                if field=='mvp' and isinstance(content,dict):
                    for part,entry in content.items():out[key+'/mvp/'+part]=entry
                else:out[key+'/'+field] = content
        else: out[key] = value
    return out


def render(kind, title, data, old=None):
    layouts = json.loads(LAYOUTS.read_text())
    rules = layouts[kind]
    fields = flat(data)
    grouped = {name:{} for name, _ in rules}
    grouped['Record details'] = {}
    for path, value in fields.items():
        key = path.split('/')[-1]
        section = 'MVP definition' if '/mvp/' in path else next((name for name, keys in rules if key in keys), 'Record details')
        grouped[section][path] = value
    grouped = {k:v for k,v in grouped.items() if v}
    if old is None:
        result = md.dumps(title, grouped)
    else:
        # Keep existing section placement and all free notes; new sections follow
        # the approved order. Unknown fields remain in their original section.
        prior = md.loads(old)
        new = {}
        remaining = dict(fields)
        for section, values in prior.items():
            new[section] = {path: remaining.pop(path) for path in values if path in remaining}
        for section, values in grouped.items():
            for path, value in values.items():
                if path in remaining:
                    new.setdefault(section,{})[path] = remaining.pop(path)
        result = md.patch(old, new)
    # Field identities are paths, but the displayed labels are concise.
    nodes,_ = md.parse_nodes(result)
    edits=[]
    for node in nodes:
        for child in node.children:
            heading_start=result.find('\n',child.start)+1
            heading_end=result.find('\n',heading_start)
            label=child.key.split('/')[-1].replace('_',' ').capitalize()
            edits.append((heading_start,heading_end,'### '+label))
    for a,b,value in reversed(edits):result=result[:a]+value+result[b:]
    # Use shared table serialization for all object lists, not heading-per-row.
    if old is None and 'Record details' in grouped:
        nodes,_=md.parse_nodes(result)
        n=next(n for n in nodes if n.key=='Record details')
        result=result[:n.start]+'<details>\n<summary>Record details and traceability</summary>\n\n'+result[n.start:n.end]+'\n</details>\n'+result[n.end:]
    if unpack(result)!=data: raise ValueError('Template round-trip changed document content.')
    return result
