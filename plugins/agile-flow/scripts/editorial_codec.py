"""Template-driven editorial Markdown, with value-free reversible bindings.

Bindings describe source paths and types, never a parallel copy of product data.
The previous codec remains a reader for explicitly migrated older checkouts.
"""
import copy
import html
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'templates' / 'markdown'
MISSING = 'Not recorded'
TOKEN = re.compile(r'{{([^}]+)}}')


def get(data, path):
    for key in path:
        data = data[key]
    return data


def put(data, path, value):
    if not path:
        raise ValueError('A binding needs a source path.')
    for key in path[:-1]:
        data = data[key]
    data[path[-1]] = value


def skeleton(value):
    if isinstance(value, dict):
        return {k: skeleton(v) for k, v in value.items()}
    if isinstance(value, list):
        return [skeleton(v) for v in value]
    return None


def cell(value):
    if isinstance(value, str):
        encoded=html.escape(value, quote=False).replace('|', '&#124;').replace('\n', '&#10;').replace('\t','&#9;')
        encoded=re.sub(r'^ +| +$',lambda m:'&#32;'*len(m[0]),encoded)
        return encoded, {'type': 'text'}
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        parts = [cell(v)[0] for v in value]
        return '<br>'.join(parts) if parts else 'No entries', {'type': 'texts', 'empty': not value}
    if isinstance(value, (dict, list)):
        if not value:
            return 'No entries', {'type': 'object' if isinstance(value, dict) else 'array'}
        parts = []; shapes = []
        for key, val in (value.items() if isinstance(value, dict) else enumerate(value)):
            rendered, shape = cell(val)
            label = str(key).replace('_', ' ').capitalize() if isinstance(key, str) else str(key + 1)
            # Nesting uses escaped line breaks so only this level owns <br>.
            parts.append(html.escape(label, quote=False).replace('|', '&#124;') + ': ' + rendered.replace('<br>', '&#60;br&#62;'))
            shapes.append([key, label, shape])
        return '<br>'.join(parts), {'type': 'dict' if isinstance(value, dict) else 'list', 'children': shapes}
    return json.dumps(value), {'type': 'scalar', 'scalar': type(value).__name__}


def uncell(raw, shape):
    kind = shape['type']
    if kind == 'link':
        match=re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)',raw)
        if not match or match[2]!=shape['target']:raise ValueError('Changed record link; use a record operation to change its assignment.')
        value=uncell(match[1],shape['inner'])
        if value!=shape['identity']:raise ValueError('Record link identity and target disagree.')
        return value
    if kind == 'text': return html.unescape(raw)
    if kind == 'texts': return [] if raw == 'No entries' and shape.get('empty') else [html.unescape(v) for v in raw.split('<br>')]
    if kind in {'object', 'array'}:
        if raw != 'No entries': raise ValueError('Use a record operation to populate an untyped empty container.')
        return {} if kind == 'object' else []
    if kind in {'dict', 'list'}:
        parts = raw.split('<br>'); result = {} if kind == 'dict' else []
        if len(parts) != len(shape['children']): raise ValueError('Structured cell shape changed; reconcile with a record operation.')
        for part, (key, label, child) in zip(parts, shape['children']):
            prefix = html.escape(label, quote=False).replace('|', '&#124;') + ': '
            if not part.startswith(prefix): raise ValueError('Structured cell label changed.')
            value = uncell(part[len(prefix):].replace('&#60;br&#62;', '<br>'), child)
            if kind == 'dict': result[key] = value
            else: result.append(value)
        return result
    value = json.loads(raw)
    if type(value).__name__ != shape['scalar']: raise ValueError('Changed scalar type.')
    return value


# Ordered aliases map existing domain vocabulary onto the approved editorial vocabulary.
ALIASES = {
 'project_name':'name', 'status':'administrative_state|status|state', 'date':'updated_at|updated|date', 'owner':'owner',
 'one_paragraph_product_definition':'purpose', 'problem_and_background':'problem|background',
 'desired_future':'vision', 'how_the_product_serves_its_users':'mission',
 'concise_success_factors':'success_factors', 'included_capabilities':'scope', 'explicit_exclusions':'exclusions',
 'confirmed_operational_or_technical_limits':'constraints',
 'on_request_or_automatic_outcomes_and_source':'git_policy', 'separately_agreed_scope_or_not_granted':'publication_permission',
 'planning_status':'status', 'short_strategic_direction':'direction|purpose',
 'BL_id':'id', 'need_title':'name|purpose', 'need_status':'state|status', 'rank_or_unranked':'order',
 'version_or_unassigned':'target_release', 'short_problem_statement_and_relevant_background':'problem|purpose',
 'observable_change_for_the_user_or_operator':'outcome', 'boundaries':'exclusions',
 'why_this_need_has_its_current_priority':'priority', 'version':'release_id|id', 'release_name':'name|objective',
 'release_status':'status', 'concrete_usable_outcome_for_this_release':'objective',
 'observed_learning_and_resulting_decisions':'learning', 'affected_users_required_steps_and_known_limits':'upgrade_notes',
 'ITER_id':'id', 'iteration_status':'state', 'agreed_timeframe_or_not_set':'timeframe',
 'one_coherent_goal':'goal', 'demonstrable_result':'expected_result', 'iteration_scope':'scope',
 'iteration_exclusions':'exclusions', 'concise_approach_components_and_key_tradeoffs':'technical_plan',
 'US_id':'id', 'work_title':'name|purpose', 'concise_need_and_expected_value':'purpose|value', 'included_work':'scope',
 'actor':'story.actor|actor', 'capability':'story.capability|story.want', 'benefit':'story.benefit|story.goal',
 'actual_behavior':'observed', 'expected_behavior':'expected', 'affected_users_or_operations':'impact',
 'first_reproduction_step':'reproduction', 'reason_for_the_work':'technical_objective',
 'proposed_change_and_tradeoffs':'approach', 'components':'components', 'specific_uncertainty':'question',
 'agreed_time_or_scope_limit':'work_limit', 'decision_or_artifact_to_produce':'expected_output',
 'actual_findings_or_pending':'findings|recommendation',
 'observed_verification_status':'status', 'what_is_demonstrated_what_is_not_and_next_action':'conclusion',
 'current_acceptance_status':'acceptance', 'period':'period', 'observations_and_feedback_references':'sources',
 'one_paragraph_product_objective_and_current_position':'purpose', 'one_concrete_next_step':'next_step',
 'specific_decision_or_none':'needed_from_user', 'independent_authorized_work_or_none':'can_continue',
 'brief_explanation_of_current_order_and_material_tradeoffs':'priority_rationale',
 'condition_that_would_change_sequence_or_scope':'adaptation_criteria',
 'assumption_about_product_value_to_test':'mvp.hypothesis', 'specific_initial_users':'mvp.early_users',
 'smallest_tangible_solution_usable_by_those_users':'mvp.minimum_scope',
}
# Each table uses the literal headings/separators from its Markdown template.
# Fields not represented by these columns remain visible in Additional context.
TABLES = {
 'User journeys': [('journeys','id','actor','trigger','steps','outcome','status')],
 'Screens and interactions': [('screens','id','journey','screen','information','actions','status')],
 'States and recovery': [('states','context','state','behavior','recovery','status')],
 'Accessibility': [('accessibility','need','behavior','verification','status')],
 'Alternatives and recommendations': [('alternatives','topic','option','benefits','costs','recommendation','status')],
 'Design decisions': [('decisions','id','decision','scope','basis','source','rationale','status','supersedes')],
 'Architecture decisions': [('decisions','id','decision','scope','basis','source','rationale','status','supersedes')],
 'Questions and revisit points': [('open_questions','question','impact','timing','revisit_when')],
 'Components and responsibilities': [('components','component','responsibility','interfaces','boundary','status')],
 'Data and ownership': [('data','data','owner','persistence','lifecycle','status')],
 'Integrations': [('integrations','system','contract','failure','trust_boundary','status')],
 'Operation and deployment': [('operations','concern','approach','cost','verification','status')],
 'Deferred topics': [('deferred','item','impact','resolution')],
 'Questions to investigate': [('investigate','item','impact','resolution')],

 'People and value': [('users','actor|name','need','value|expected_value'), ('stakeholders','actor|name','need','value|expected_value')],
 'Objectives and success factors': [('objectives','objective|description','evidence','knowledge|status'), ('success_criteria','criterion','evidence','knowledge')],
 'Decisions and collaboration agreements': [('decisions','id','reason|summary|decision|purpose','kind','scope','source','quote','author','at','supersedes'), ('agreements','id','agreement|summary','kind','scope','source','quote','author','at','supersedes')],
 'Facts, assumptions and open decisions': [('confirmed_facts','=Fact','statement','source|impact','resolution'), ('assumptions','=Assumption','statement','basis|impact','resolution'), ('proposals','=Proposal','statement','basis|impact','resolution'), ('open_questions','=Question','question|statement','impact','resolution')],
 'Version roadmap': [('versions','version','stage','intended_outcome','capabilities','dependencies','status')],
 'Major milestones': [('milestones','milestone|name','version','evidence|outcome')],
 'Planning assumptions and uncertainty': [('assumptions','=Assumption','statement','impact','revisit_when'), ('uncertainties','=Uncertainty','statement','impact','revisit_when')],
 'Release references': [('release_references','version','document|reference')],
 'Intended users and expected value': [('users','actor|name','need','value')],
 'Success indicators': [('success_indicators','indicator|name','target|expected','evidence|knowledge')],
 'Dependencies, assumptions and open questions': [('dependencies','=Dependency','item|statement','impact','resolution'), ('assumptions','=Assumption','statement','impact','resolution'), ('open_questions','=Question','question|statement','impact','resolution')],
 'Delivery breakdown': [('story_links','document|story','type','release','iteration','contribution')],
 'Target users and expected value': [('users','user|name','value','evidence')],
 'Planned scope': [('item_ids','$','contribution','rationale')],
 'MVP definition': [('mvp.learning_questions','question','method','decision')],
 'Delivery organization': [('iteration_links','document|iteration','goal','contribution','status')],
 'Dependencies, risks and open decisions': [('dependencies','=Dependency','item|statement','impact|consequence','resolution|response'), ('risks','=Risk','statement|item','impact|consequence','resolution|response'), ('open_questions','=Question','question|statement','impact','resolution'), ('open_decisions','=Decision','statement','impact','resolution')],
 'Release exit conditions': [('exit_conditions','condition','evidence','result')],
 'Scope changes': [('changes','at|date','change|reason','source','effect')],
 'Delivered outcome': [('delivered_outcome','contribution','result','references')],
 'Publication references': [('publication','artifact','reference','status')],
 'Selected stories and baselines': [('item_documents','document','type','contribution','estimate','baseline')],
 'Implementation tasks': [('tasks','id|task','story|item_id','action|description','evidence','status')],
 'Verification plan': [('verification_plan','requirement|story','check','method','evidence')],
 'Authorization and agreements': [('agreements','decision|id','scope','source','status')],
 'Plan changes': [('changes','at|date','change|reason','source','impact')],
 'Delivery increments': [('increments','id','item_ids','objective','authorization','states.development|development_status|status')],
 'Acceptance criteria': [('criteria','id','condition','result')],
 'Definition of Done': [('dod','id','requirement','evidence')],
 'Dependencies and open questions': [('dependencies','=Dependency','item|statement','impact','resolution'), ('uncertainties','=Uncertainty','statement','impact','resolution'), ('open_questions','=Question','question|statement','impact','resolution')],
 'Delivery and evidence references': [('delivery_links','increment_id','revision','verification','review')],
 'Verified scope and baselines': [('scope','increment_id','revision','item_ids','artifact','environment')],
 'Check results and execution details': [('evidence','id','scope|requirement|criterion','check','result','paths|reference|artifacts')],
 'Unavailable checks and blockers': [('blockers','id','condition|reason','impact','resolution_requirement|resolution')],
 'Presented result': [('presented_result','increment_id','revision','scope','limits')],
 'User feedback and acceptance decisions': [('reviews','id','increment_id+delivery_revision','parts|accepted_parts|scope','decision','message_reference|source')],
 'Resulting work': [('resulting_work','work','origin','treatment','reference')],
 'Unresolved feedback': [('unresolved_feedback','question','impact','action')],
 'Observations and proposed improvements': [('improvements','id','observation','source','adjustment|proposal','state|status')],
 'What to retain': [('retain','practice','benefit','observation')],
 'Follow-up': [('follow_up','id','action','target_cycle','owner','effect'), ('improvements','id','adjustment','target_cycle','owner','effect_evidence')],
 'Changes': [('changes','at|date','change|reason','source'), ('amendments','at|date','change|reason','source')],
 'Prioritized needs': [('needs','order','document','value','state','target_release')],
 'Completed or retired needs': [('completed','document','state','outcome')],
 'Current release and iteration': [('current','release','objective','iteration','goal','status')],
 'Delivery status': [('deliveries','id','development','verification','acceptance','limit')],
 'Blockers and pending decisions': [('pending','item','impact','resolution')],
 'Git status': [('git','branch','commit','changes','policy')],
}

ALIASES.update({
 'EVD_id':'id', 'REV_id':'id', 'INC_id':'increment_id', 'check_name':'check',
 'revision':'delivery_revision', 'timestamp_or_not_run':'at',
 'actual_procedure_or_command':'method|command', 'expected_result':'expected',
 'actual_result_or_not_observed':'observed', 'limitations_and_uncovered_behavior':'limitations',
 'supporting_paths_or_links':'paths|artifacts', 'exact_user_quote_if_available':'user_quote',
 'explicitly_accepted_parts_or_none_recorded':'accepted_parts',
 'remaining_parts_or_requested_changes':'requested_changes|changes', 'evidence_references':'evidence_ids',
})


def split_sections(text):
    matches = list(re.finditer(r'^## (.+)\n', text, re.M))
    sections = [('', text[:matches[0].start()] if matches else text)]
    for n, match in enumerate(matches):
        sections.append((match[1], text[match.end():matches[n+1].start() if n+1 < len(matches) else len(text)]))
    return sections


REQUIRED_SECTIONS = {
 'product_design': {'Design purpose'},
 'architecture': {'Architecture purpose'},
 'constitution': {'Purpose','People and value','Objectives and success factors','Product boundaries','Decisions and collaboration agreements','Facts, assumptions and open decisions'},
 'roadmap': {'Version roadmap'},
 'product_backlog': {'Prioritized needs'},
 'product_item': {'Problem or opportunity','Intended users and expected value','Expected product outcome','Scope','Priority rationale'},
 'release': {'Release objective','Target users and expected value','Planned scope','Release exit conditions'},
 'planning': {'Iteration goal and expected result','Selected stories and baselines','Scope','Technical approach','Implementation tasks','Verification plan','Authorization and agreements'},
 'story': {'Need and value','Scope','Type-specific detail','Acceptance criteria','Definition of Done'},
 'verification': {'Verified scope and baselines','Check results and execution details','Verification conclusion'},
 'review': {'Presented result','User feedback and acceptance decisions'},
 'retrospective': {'Observations and proposed improvements'},
 'summary': {'Current release and iteration','Delivery status','Next useful action'},
}


class Renderer:
    def __init__(self, data, display=None, links=None):
        self.display=display or {};self.links=links or {}
        self.data = data; self.used = set(); self.slots = []; self.reuse=False
        self.base = next(([k] for k in ('project','item','release','iteration') if k in data), [])

    def path(self, expression, base=None):
        base = self.base if base is None else base
        fallback=None
        for name in expression.split('|'):
            path = base + name.split('.')
            try: get(self.data, path)
            except (KeyError, TypeError, IndexError): continue
            if self.reuse or tuple(path) not in self.used:
                if get(self.data,path) not in ([],{},'',None):return path
                if fallback is None:fallback=path
        if fallback is not None:return fallback
        if base and expression.split('.')[0] in self.data: return self.path(expression, [])
        return None

    def encode_cell(self,path):
        value=get(self.data,path);raw,shape=cell(value)
        if isinstance(value,str) and value in self.links and path[-1] in {'id','parent_id','release_id','iteration_id','target_release','version','iteration','story'}:
            target=self.links[value]
            return '['+raw+']('+target+')',{'type':'link','target':target,'identity':value,'inner':shape}
        return raw,shape

    def capture(self, path):
        raw, shape = self.encode_cell(path); self.used.add(tuple(path))
        ident = len(self.slots); self.slots.append({'path':path, 'shape':shape})
        return raw, '\x00'+str(ident)+'\x00'

    def paragraph(self, text):
        # Link targets are never guessed from missing placeholders.
        text = re.sub(r'\[([^\]]*{{[^\]]+)\]\([^\n)]+\)', r'\1', text)
        rendered = text; pattern = text
        for match in list(TOKEN.finditer(text)):
            token = match[0]; name = match[1]
            prior_reuse=self.reuse;self.reuse=True
            path = self.path(ALIASES.get(name, name));self.reuse=prior_reuse
            if path is None:
                if name in self.display:
                    raw,shape=cell(self.display[name]);ident=len(self.slots)
                    self.slots.append({'display':name,'shape':shape});marker='\x00'+str(ident)+'\x00'
                else:raw=marker=MISSING
            else: raw, marker = self.capture(path)
            target=token+'.' if raw.endswith('.') and token+'.' in rendered else token
            rendered = rendered.replace(target, raw, 1); pattern = pattern.replace(target, marker, 1)
        return rendered, pattern

    def table(self, block, section):
        lines = block.splitlines(); headers = [v.strip() for v in lines[0].strip('|').split('|')]
        specs = TABLES.get(section, [])
        if section == '__story_metadata': specs = [('', 'type','parent_id','release_id','iteration_id','state','estimate')]
        if section == '__nfr': specs = [('', 'quality_attribute','applicability','target','verification_method')]
        rows = []; schema = []; groups = []
        for spec in specs:
            path = self.base if spec[0] == '' else self.path(spec[0])
            if path is None: continue
            value = get(self.data,path)
            is_list = isinstance(value,list)
            items = value if is_list else [value]
            groups.append({'path':path,'list':is_list})
            for n, item in enumerate(items):
                rp = path + [n] if is_list else path
                cells = []; shapes = []; assigned_scalar = False
                for expression in spec[1:]:
                    if '+' in expression and isinstance(item,dict):
                        parts=[];texts=[]
                        for component in expression.split('+'):
                            p=self.path(component,rp)
                            if p is None:texts.append(MISSING);parts.append({'literal':MISSING})
                            else:
                                raw,shape=self.encode_cell(p);self.used.add(tuple(p))
                                texts.append(raw);parts.append({'relative':p[len(rp):],'shape':shape})
                        cells.append(' / '.join(texts));shapes.append({'parts':parts});continue
                    if expression.startswith('='):
                        cells.append(expression[1:]); shapes.append({'literal':expression[1:]}); continue
                    if isinstance(item,dict):
                        p = self.path(expression, rp) if expression != '$' else None
                    else:
                        p = rp if not assigned_scalar else None; assigned_scalar = True
                    if p is None: cells.append(MISSING); shapes.append({'literal':MISSING})
                    else:
                        raw, shape = self.encode_cell(p); self.used.add(tuple(p))
                        cells.append(raw); shapes.append({'relative':p[len(rp):], 'shape':shape})
                rows.append('| '+' | '.join(cells)+' |')
                descriptor={'group':len(groups)-1, 'shape':skeleton(item), 'cells':shapes}
                if isinstance(item,dict):
                    represented={b['relative'][0] for b in shapes if 'relative' in b and b['relative']}
                    if set(item)-represented:
                        identity=next((key for key in ('id','version') if key in item and key in represented),None)
                        if identity is not None:
                            descriptor['fixed_identity']={'key':identity,'value':item[identity]}
                        else:
                            first=next((n for n,b in enumerate(shapes) if 'relative' in b),None)
                            if first is not None:descriptor['position_guard']={'column':first,'digest':hashlib.sha256(cells[first].encode()).hexdigest()}
                schema.append(descriptor)
            # Empty containers need no hidden value and remain empty in the skeleton.
        rendered = '\n'.join(lines[:2]+rows) if rows else 'No entries recorded.'
        ident = len(self.slots)
        self.slots.append({'table':True,'headers':headers,'groups':groups,'rows':schema})
        return rendered, '\x00'+str(ident)+'\x00'

    def leftovers(self):
        result=[]
        def visit(value,path):
            if tuple(path) in self.used: return
            if isinstance(value,dict):
                for key,val in value.items(): visit(val,path+[key])
            elif isinstance(value,list) and value and any(tuple(path)==p[:len(path)] for p in self.used):
                for n,val in enumerate(value):visit(val,path+[n])
            elif value not in ({},[]): result.append(path)
        visit(self.data,[])
        return result


def render(kind,title,data,notes='',document_path=None,available=None,display=None,links=None):
    template=(ROOT/(kind+'.md')).read_text()
    if document_path is not None and available is not None:
        import posixpath
        def existing_link(match):
            target=match[2]
            if '{{' in target or ':' in target or target.startswith('#'):return match[0]
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(document_path),target))
            return match[0] if resolved in available else match[1]
        template=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',existing_link,template)
    if kind=='summary' and not data.get('git'):
        template=re.sub(r'^## Git status\n.*?(?=^## |\Z)','',template,flags=re.M|re.S)
    original_template=template
    if kind=='story':
        work=data['item'].get('type')
        template=re.sub(r'^### (US|NFR|BUG|TCH|SPK) — [^\n]+\n.*?(?=^### |^## |\Z)',lambda m:m[0] if m[1]==work else '',template,flags=re.M|re.S)
    if kind=='release' and not data.get('release',{}).get('mvp'):
        template=re.sub(r'^## MVP definition\n.*?(?=^## |\Z)','',template,flags=re.M|re.S)
    # Repeated event details are represented once in the record tables plus the
    # supplementary context, never duplicated as independently editable copies.
    template=re.sub(r'^### (?:Baseline for|{{EVD_id}}|{{REV_id}}).*?(?=^## |\Z)','',template,flags=re.M|re.S)
    writer=Renderer(data,display,links); output=[]; sections=[]
    for name,body in split_sections(template):
        rendered=[]; patterns=[];slot_start=len(writer.slots)
        writer.reuse=(kind=='retrospective' and name=='Follow-up')
        for block in re.split(r'\n\s*\n',body.strip()):
            if not block:continue
            if kind=='constitution' and block.startswith('**Git agreement:**') and not data.get('project',{}).get('git_policy') and not data.get('project',{}).get('publication_permission'):continue
            if name=='Sources':
                source=writer.path('references|provenance')
                if source is None:raw=pattern='No sources recorded.'
                else:
                    value=get(data,source)
                    if isinstance(value,list) and all(isinstance(v,str) for v in value):
                        pairs=[writer.capture(source+[n]) for n in range(len(value))]
                        raw='\n'.join('- '+r for r,p in pairs) or 'No sources recorded.'
                        pattern='\n'.join('- '+p for r,p in pairs) or raw
                    else:
                        raw,pattern=writer.capture(source);raw='- '+raw;pattern='- '+pattern
            elif name=='Adaptation criteria' and writer.path('adaptation_criteria') is not None and isinstance(get(data,writer.path('adaptation_criteria')),list):
                path=writer.path('adaptation_criteria');values=get(data,path)
                pairs=[writer.capture(path+[n]) for n in range(len(values))]
                raw='\n'.join('- '+r for r,p in pairs) or 'No adaptation criteria recorded.'
                pattern='\n'.join('- '+p for r,p in pairs) or raw
            elif block.startswith('1. {{first_reproduction_step}}'):
                path=writer.path('reproduction')
                value=get(data,path) if path is not None else None
                if isinstance(value,list) and all(isinstance(v,str) for v in value):
                    values=[];markers=[]
                    for n,item in enumerate(value):
                        raw,pattern=writer.capture(path+[n]);values.append(str(n+1)+'. '+raw);markers.append(str(n+1)+'. '+pattern)
                    raw='\n'.join(values) or 'No reproduction steps recorded.';pattern='\n'.join(markers) or raw
                elif path is not None:
                    raw,pattern=writer.capture(path);raw='1. '+raw;pattern='1. '+pattern
                else:raw=pattern='No reproduction steps recorded.'
            elif block.startswith('|'):
                key='__story_metadata' if kind=='story' and name=='' else '__nfr' if name=='Type-specific detail' else name
                raw,pattern=writer.table(block,key)
            else:
                if block.startswith('# '):
                    tokens=TOKEN.findall(block)
                    if all(writer.path(ALIASES.get(t,t)) is not None or t in writer.display for t in tokens):raw,pattern=writer.paragraph(block)
                    else:raw='# '+title; pattern='# \x00title\x00'
                else:raw,pattern=writer.paragraph(block)
            rendered.append(raw);patterns.append(pattern)
        if kind in {'verification','review'} and name in {'Check results and execution details','User feedback and acceptance decisions'}:
            group='evidence' if kind=='verification' else 'reviews'
            detail=re.search(r'^### {{(?:EVD_id|REV_id)}}.*?(?=^## |\Z)',original_template,re.M|re.S)
            prior_base=writer.base;writer.reuse=True
            for index,record in enumerate(data.get(group,[])):
                writer.base=[group,index]
                body=detail[0].strip()
                if kind=='review' and not record.get('user_quote'):
                    body=body.replace('> {{exact_user_quote_if_available}}','User quotation not recorded; see the source reference above.')
                raw,pattern=writer.paragraph(body)
                rendered.append(raw);patterns.append(pattern)
            writer.base=prior_base;writer.reuse=False
        writer.reuse=False
        if kind=='planning' and name=='Delivery increments':
            baseline_template=re.search(r'^### Baseline for.*?(?=^## |\Z)',original_template,re.M|re.S)[0].strip()
            old_base=writer.base
            for n,inc in enumerate(data.get('increments',[])):
                if not inc.get('story_baseline'):continue
                writer.base=['increments',n];writer.reuse=True
                header=baseline_template.split('\n\n')[0].replace('{{INC_id}}','{{baseline_increment}}')
                ALIASES['baseline_increment']='id'
                raw,pattern=writer.paragraph(header);rendered.append(raw);patterns.append(pattern)
                specs=[]
                for story,baseline in inc['story_baseline'].items():
                    for group,label,value in [('criteria','Acceptance','result'),('dod','DoD','requirement')]:
                        if group in baseline:specs.append(('story_baseline.'+story+'.'+group,'='+story,'='+label,'id',value))
                TABLES['__baseline']=specs
                raw,pattern=writer.table(baseline_template.split('\n\n',1)[1],'__baseline');rendered.append(raw);patterns.append(pattern)
            writer.base=old_base;writer.reuse=False
        bound=writer.slots[slot_start:]
        meaningful=any(('path' in slot and get(data,slot['path']) not in ([],{})) or slot.get('rows') or 'display' in slot for slot in bound)
        if name and name not in REQUIRED_SECTIONS.get(kind,set()) and not meaningful:
            # Empty containers survive in the structural skeleton; no functional
            # value is lost by omitting an inapplicable optional section.
            continue
        output.append((('## '+name+'\n\n') if name else '')+'\n\n'.join(rendered))
        sections.append({'heading':name,'pattern':'\n\n'.join(patterns)})
    remaining=writer.leftovers()
    if remaining:
        rows=[]; patterns=[]
        for path in remaining:
            label=' / '.join(str(k+1) if isinstance(k,int) else k.replace('_',' ').capitalize() for k in path if k not in {'project','item','release','iteration'})
            raw,marker=writer.capture(path)
            rows.append('| '+label+' | '+raw+' |');patterns.append('| '+label+' | '+marker+' |')
        header='| Context | Detail |\n| --- | --- |\n'
        output.append('## Additional context\n\n'+header+'\n'.join(rows))
        sections.append({'heading':'Additional context','pattern':header+'\n'.join(patterns)})
    schema={'codec':'editorial-v2','kind':kind,'shape':skeleton(data),'sections':sections,'slots':writer.slots}
    text='\n\n'.join(output).rstrip()+('\n\n'+notes.strip() if notes.strip() else '')+'\n'
    if unpack(text,schema)!=data: raise ValueError('Editorial Markdown round-trip changed meaning: '+kind)
    return text,schema


def parse_table(raw,slot,result,seen):
    if raw.strip()=='No entries recorded.':
        if slot['rows']: raise ValueError('Deleting an entire populated table requires reconciliation.')
        return
    rows=[]
    for line in raw.strip().splitlines():
        if not line.strip().startswith('|') or not line.strip().endswith('|'): raise ValueError('Unexpected prose inside a structured table.')
        rows.append([v.strip().replace(r'\|','&#124;') for v in re.split(r'(?<!\\)\|',line.strip()[1:-1])])
    if len(rows)<2 or rows[0]!=slot['headers'] or any(not re.fullmatch(':?-+:?',v) for v in rows[1]):raise ValueError('Changed editorial table columns.')
    descriptors=slot['rows']; actual=rows[2:]
    dynamic=not any('fixed_identity' in r or 'position_guard' in r for r in descriptors) and len(slot['groups'])==1 and slot['groups'][0]['list'] and descriptors and all(r==descriptors[0] for r in descriptors)
    if not dynamic and len(actual)!=len(descriptors):raise ValueError('Mixed rows need an explicit record operation.')
    if dynamic:
        group=slot['groups'][0];put(result,group['path'],[copy.deepcopy(descriptors[0]['shape']) for row in actual])
    counts={}
    for n,row in enumerate(actual):
        desc=descriptors[0] if dynamic else descriptors[n]; group=slot['groups'][desc['group']]
        index=counts.get(desc['group'],0);counts[desc['group']]=index+1
        path=group['path']+([index] if group['list'] else [])
        if len(row)!=len(desc['cells']):raise ValueError('Wrong editorial table cell count.')
        if 'position_guard' in desc:
            guard=desc['position_guard']
            if hashlib.sha256(row[guard['column']].encode()).hexdigest()!=guard['digest']:
                raise ValueError('A row without an identity has separate details; refine it through a record operation.')
        if 'fixed_identity' in desc:
            identity=desc['fixed_identity']
            for raw_cell,binding in zip(row,desc['cells']):
                if binding.get('relative')==[identity['key']] and uncell(raw_cell,binding['shape'])!=identity['value']:
                    raise ValueError('A row with separate details cannot change identity or order; use a record operation.')
        for raw_cell,binding in zip(row,desc['cells']):
            if 'parts' in binding:
                values=raw_cell.split(' / ')
                if len(values)!=len(binding['parts']):raise ValueError('Incomplete delivery / revision reference.')
                for part,member in zip(values,binding['parts']):
                    if 'literal' in member:
                        if part!=member['literal']:raise ValueError('Unbound reference changed.')
                    else:assign(result,path+member['relative'],uncell(part,member['shape']),seen)
            elif 'literal' in binding:
                if raw_cell!=binding['literal']:raise ValueError('Unbound table cell changed; add the field through a record operation.')
            else:assign(result,path+binding['relative'],uncell(raw_cell,binding['shape']),seen)


def extract(text,schema):
    if re.search(r'^(<<<<<<<|=======|>>>>>>>)',text,re.M):raise ValueError('Unresolved merge conflict in document.')
    if '<!-- af:' in text:raise ValueError('Legacy markers require migration.')
    actual=split_sections(text);known={s['heading'] for s in schema['sections']};notes=[];selected={}
    for name,body in actual:
        if name in known:
            if name in selected:raise ValueError('Missing or duplicate structured heading: '+name)
            selected[name]=body.strip()
        else:notes.append('## '+name+'\n'+body)
    result=copy.deepcopy(schema['shape']);seen={}
    for section in schema['sections']:
        name=section['heading']
        if name not in selected:raise ValueError('Missing or duplicate structured heading: '+name)
        pattern=section['pattern'];pieces=re.split(r'\x00([^\x00]+)\x00',pattern);regex='';bindings=[]
        for n,piece in enumerate(pieces):
            if n%2:
                bindings.append(piece)
                regex+=r'([^\n]*?)' if piece=='title' or not schema['slots'][int(piece)].get('table') else r'(\|[^\n]*\|(?:\n\|[^\n]*\|)*|No entries recorded\.)'
            else:
                # Flexible table whitespace, with the approved labels preserved.
                escaped=re.escape(piece)
                escaped=escaped.replace(r'\ ',r'[ \t]*')
                regex+=escaped
        match=re.fullmatch(regex,selected[name])
        if not match:raise ValueError('Editorial section structure changed: '+name+'; preserve its labels or reconcile before writing.')
        for key,raw in zip(bindings,match.groups()):
            if key=='title':continue
            slot=schema['slots'][int(key)]
            if slot.get('table'):parse_table(raw,slot,result,seen)
            elif 'display' in slot:uncell(raw,slot['shape'])  # Observed header context is not an editable domain record.
            else:assign(result,slot['path'],uncell(raw,slot['shape']),seen)
    return result,'\n'+''.join(notes) if notes else ''


def unpack(text,schema):
    return extract(text,schema)[0]


def assign(result,path,value,seen):
    key=tuple(path)
    if key in seen and seen[key]!=value:raise ValueError('Conflicting repeated reference; reconcile the edited record.')
    seen[key]=value;put(result,path,value)
