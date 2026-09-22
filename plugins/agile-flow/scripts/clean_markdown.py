"""Plain Markdown codec. Field structure, never functional values, is portable metadata."""
import html
import copy
import json
import re
try:
    from . import markdown_records as md, template_documents as templates
except ImportError:
    import markdown_records as md, template_documents as templates


def headings(text):
    result=[];offset=0;fence=None
    for line in text.splitlines(True):
        stripped=line.lstrip()
        marker=re.match(r'(`{3,}|~{3,})',stripped)
        if marker:
            char=marker[1][0]
            if fence is None:fence=char
            elif fence==char:fence=None
        elif fence is None:
            match=re.match(r'^(#{1,6}) +(.+?)\s*$',line)
            if match:result.append({'level':len(match[1]),'title':match[2].casefold(),'start':offset,'body':offset+len(line)})
        offset+=len(line)
    for n,h in enumerate(result):
        h['end']=next((v['start'] for v in result[n+1:] if v['level']<=h['level']),len(text))
    return result


def readable_cell(value):
    leaves=[]
    def shape(v,path):
        if isinstance(v,dict) and v:return {'object':{k:shape(x,path+[k]) for k,x in v.items()}}
        if isinstance(v,list) and v:return {'array':[shape(x,path+[str(n+1)]) for n,x in enumerate(v)]}
        label=' / '.join(path) or 'Value'
        raw=v if isinstance(v,str) else ('No entries' if v in ([],{}) else json.dumps(v))
        leaves.append(html.escape(label+': '+raw,quote=False).replace('|','&#124;').replace('\n','&#10;'))
        return {'path':label,'type':md.kind_of(v)}
    schema=shape(value,[])
    return '<br>'.join(leaves),schema


def parse_readable_cell(value,schema):
    leaves=iter(value.split('<br>'))
    def parse(node):
        if 'object' in node:return {k:parse(v) for k,v in node['object'].items()}
        if 'array' in node:return [parse(v) for v in node['array']]
        raw=html.unescape(next(leaves));prefix=node['path']+': '
        if not raw.startswith(prefix):raise ValueError('Structured cell labels changed; reconcile before writing.')
        raw=raw[len(prefix):]
        if node['type']=='text':return raw
        if raw=='No entries':return {} if node['type']=='object' else []
        return json.loads(raw)
    try:result=parse(schema)
    except StopIteration:raise ValueError('Structured table cell is incomplete.')
    if next(leaves,None) is not None:raise ValueError('Structured table cell has extra values.')
    return html.escape(json.dumps(result,ensure_ascii=False),quote=False).replace('|','&#124;').replace('\n','<br>')


def strip(marked):
    wrapper='<details>\n<summary>Record details and traceability</summary>'
    if wrapper in marked:
        opening=marked.index(wrapper);depth=0;closing=None
        for match in re.finditer(r'</?details>',marked[opening:]):
            depth += -1 if match.group().startswith('</') else 1
            if depth==0:closing=(opening+match.start(),opening+match.end());break
        if closing:
            marked=marked[:closing[0]]+marked[closing[1]:]
            marked=marked[:opening]+marked[opening+len(wrapper):]
    nodes,_=md.parse_nodes(marked);replacements=[]
    def schema(node):
        match=md.BEGIN.match(marked,node.start);meta=json.loads(match[1])
        heading=marked[match.end():marked.find('\n',match.end())]
        level=len(heading)-len(heading.lstrip('#'))
        if node.kind=='table':
            nested={};columns=meta['columns'];rows=[]
            for n,row in enumerate(node.value):
                identity=row.get('id',str(n));cells=[]
                for key in columns:
                    if key not in row:cells.append('—');continue
                    v=row[key]
                    if isinstance(v,(dict,list)):
                        cell,shape=readable_cell(v);nested.setdefault(str(identity),{})[key]=shape
                    else:cell=html.escape(v if isinstance(v,str) else json.dumps(v),quote=False).replace('|','&#124;').replace('\n','<br>')
                    cells.append(cell)
                rows.append('| '+' | '.join(cells)+' |')
            if nested:
                meta['readable_cells']=nested
                body='| '+' | '.join(k.replace('_',' ').capitalize() for k in columns)+' |\n| '+' | '.join('---' for k in columns)+' |\n'+'\n'.join(rows)+'\n'
                replacements.append((node.start,node.end,heading+'\n\n'+body+'\n'))

        if level>=5 and node.kind in {'object','array'} and node.children:
            # Keep deeply nested snapshots readable as a two-column path table,
            # with types and container shape carried only by the schema.
            leaves=[]
            def flatten(value,path):
                if isinstance(value,dict) and value:
                    return {'type':'object','children':{k:flatten(v,path+[k]) for k,v in value.items()}}
                if isinstance(value,list) and value:
                    return {'type':'array','children':[flatten(v,path+[str(n)]) for n,v in enumerate(value)]}
                n=len(leaves);leaves.append((path,value));return {'type':md.kind_of(value),'leaf':n}
            shape=flatten(node.value,[])
            body='| Field | Value |\n| --- | --- |\n'
            for path,value in leaves:
                raw=value if isinstance(value,str) else json.dumps(value)
                body+='| '+html.escape(' / '.join(path)).replace('|','&#124;')+' | '+html.escape(raw).replace('|','&#124;').replace('\n','<br>')+' |\n'
            replacements.append((node.start,node.end,heading+'\n\n'+body+'\n'))
            return {'meta':meta,'heading':heading.lstrip('# ').casefold(),'level':level,'children':[],'shape':shape,'paths':[path for path,value in leaves]}
        return {'meta':meta,'heading':heading.lstrip('# ').casefold(),'level':level,'children':[schema(c) for c in node.children]}
    structure=[schema(n) for n in nodes]
    for a,b,value in reversed(replacements):marked=marked[:a]+value+marked[b:]
    clean=md.BEGIN.sub('',marked).replace(md.END,'\n')
    return re.sub(r'\n{3,}', '\n\n', clean).rstrip()+'\n',structure


def table_meta(meta,body):
    """Accept whitespace, row order and new homogeneous rows; reject ambiguous columns."""
    lines=[line.strip() for line in body.splitlines() if line.strip()]
    if len(lines)<2:raise ValueError('A structured table needs a header and separator.')
    rows=[]
    for line in lines:
        if not line.startswith('|') or not line.endswith('|'):raise ValueError('Unexpected prose inside a structured table; add a Notes heading.')
        rows.append([c.strip().replace(r'\|','&#124;') for c in re.split(r'(?<!\\)\|',line[1:-1])])
    if any(not re.fullmatch(r':?-+:?',c) for c in rows[1]):raise ValueError('Invalid table separator.')
    if meta['type']=='properties':
        if [c.casefold() for c in rows[0]]!=['field','value']:raise ValueError('Metadata table needs Field and Value columns.')
        fields={k.split('/')[-1].replace('_',' ').casefold():(k,t) for k,t in meta['fields']}
        order=[]
        for row in rows[2:]:
            if len(row)!=2 or row[0].casefold() not in fields:raise ValueError('Unknown metadata field; reconcile its schema before writing.')
            order.append(fields[row[0].casefold()])
        if len(order)!=len(fields) or len({k for k,t in order})!=len(order):raise ValueError('Missing or duplicate metadata field.')
        meta['fields']=order
    else:
        columns={k.replace('_',' ').casefold():k for k in meta['columns']}
        if len(rows[0])!=len(columns) or set(c.casefold() for c in rows[0])!=set(columns):raise ValueError('Changed table columns; reconcile the document schema.')
        meta['columns']=[columns[c.casefold()] for c in rows[0]]
        if meta.get('readable_cells'):
            for n,row in enumerate(rows[2:]):
                identity=html.unescape(row[meta['columns'].index('id')]) if 'id' in meta['columns'] else str(n)
                shape=meta['readable_cells'].get(identity)
                if shape is None:raise ValueError('New complex table rows need an explicit record operation.')
                for key,node in shape.items():
                    index=meta['columns'].index(key);row[index]=parse_readable_cell(row[index],node)

        types={k:{r[k] for r in meta['rows'] if k in r} for k in meta['columns']}
        if any(len(t)!=1 for t in types.values()):
            if len(rows)-2!=len(meta['rows']):raise ValueError('Mixed-type rows require an explicit record operation.')
        else:
            meta['rows']=[{k:next(iter(types[k])) for k,c in zip(meta['columns'],row) if c!='—'} for row in rows[2:]]
    return meta,'\n'.join('| '+' | '.join(row)+' |' for row in rows)+'\n'


def restore(text,structure):
    if '<!-- af:' in text or '<!-- /af' in text:raise ValueError('Legacy markers need explicit migration.')
    if re.search(r'^(<<<<<<<|=======|>>>>>>>)',text,re.M):raise ValueError('Unresolved merge conflict in document.')
    hs=headings(text);edits=[]
    def visit(nodes,start,end,parent_level):
        direct=[h for h in hs if start<=h['start']<end and h['level']==parent_level+1]
        known={n['heading'] for n in nodes}
        if any(h['title'].startswith('entry ') and h['title'] not in known for h in direct):raise ValueError('New structured record needs an explicit operation.')
        for node in nodes:
            matches=[h for h in direct if h['title']==node['heading']]
            if len(matches)!=1:raise ValueError('Missing or duplicate structured heading: '+node['heading'])
            h=matches[0];stop=h['end'];meta=copy.deepcopy(node['meta'])
            if 'shape' in node:
                lines=[line.strip() for line in text[h['body']:stop].splitlines() if line.strip()]
                if len(lines)!=len(node['paths'])+2:raise ValueError('Snapshot table shape changed; reconcile before editing.')
                values=[]
                for line,path in zip(lines[2:],node['paths']):
                    cells=[html.unescape(c.strip()).replace('<br>','\n') for c in line.strip('|').split('|')]
                    if len(cells)!=2 or cells[0]!=' / '.join(path):raise ValueError('Snapshot identity changed.')
                    values.append(cells[1])
                def inflate(shape):
                    if 'children' in shape:
                        children=shape['children']
                        return {k:inflate(v) for k,v in children.items()} if isinstance(children,dict) else [inflate(v) for v in children]
                    raw=values[shape['leaf']]
                    return raw if shape['type']=='text' else json.loads(raw)
                edits.append((h['start'],stop,md.field(meta['key'],inflate(node['shape']),h['level'])))
                continue
            if meta['type'] in {'object','array'}:
                visit(node['children'],h['body'],stop,h['level'])
            else:
                # An additional heading denotes a free authored section, not a value.
                stop=next((v['start'] for v in hs if h['body']<=v['start']<stop),stop)
                if meta['type'] in {'table','properties'}:
                    meta,body=table_meta(meta,text[h['body']:stop]);edits.append((h['body'],stop,'\n'+body))
            edits.append((h['start'],h['start'],'<!-- af: '+json.dumps(meta)+' -->\n'))
            edits.append((stop,stop,md.END))
    visit(structure,0,len(text),1)
    # End markers must precede the next sibling's start marker at the same offset.
    for a,b,value in sorted(edits,key=lambda e:(e[0],e[1],not e[2].startswith(md.END)),reverse=True):text=text[:a]+value+text[b:]
    return text


def unpack(text,structure):
    return templates.unpack(restore(text,structure))


def render(kind,title,data,old=None,structure=None):
    marked=restore(old,structure) if old is not None else None
    result=templates.render(kind,title,data,marked)
    if old is None:
        from pathlib import Path
        template=(Path(__file__).resolve().parents[1]/'templates/markdown'/(kind+'.md')).read_text()
        order=[h['title'] for h in headings(template) if h['level']==2]
        nodes,_=md.parse_nodes(result)
        if any(n.key.casefold() not in order for n in nodes):raise ValueError('Template omits a structured section.')
        result=template.splitlines()[0].replace('{{title}}',title)+'\n\n'+''.join(result[n.start:n.end]+'\n' for n in sorted(nodes,key=lambda n:order.index(n.key.casefold())))
    clean,new_schema=strip(result)
    if unpack(clean,new_schema)!=data:raise ValueError('Clean Markdown round-trip changed meaning.')
    return clean,new_schema
