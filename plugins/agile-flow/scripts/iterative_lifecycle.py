"""Explicit, additive lifecycle adoption and scoped commitment controls.

Functional records remain authored Markdown. Digests protect agreed scope;
progress and observations never rewrite the committed plan.
"""
import copy
import hashlib

MODEL = 'iterative-v1'
OPERATIONS = {'adopt-lifecycle', 'commit-release', 'revise-release', 'commit-sprint',
              'record-finding', 'resolve-finding', 'track-task', 'conclude-sprint', 'assess-release'}
RELEASE_SCOPE = ('objective', 'item_ids', 'scope_items', 'scope', 'exclusions', 'mvp', 'exit_conditions')
SPRINT_SCOPE = ('goal', 'scope', 'exclusions', 'item_ids', 'tasks', 'verification_plan', 'review_access', 'technical_plan', 'expected_result', 'timeframe', 'dependencies', 'risks', 'open_decisions')
STORY_SCOPE = ('id', 'parent_id', 'iteration_id', 'release_id', 'type', 'purpose', 'criteria', 'dod', 'scope', 'exclusions', 'follows_up', 'story', 'quality_attribute', 'applicability', 'verification_method', 'reproduction', 'observed', 'expected', 'impact', 'technical_objective', 'approach', 'components', 'question', 'work_limit', 'expected_output', 'dependencies', 'open_questions')


def require(value, message, error):
    if not value:
        raise error(message)


def source(request, error):
    value = request.get('source') or request.get('authorization_source')
    require(isinstance(value, str) and value.strip(), 'An actual agreement or observation source is required.', error)
    return value


def selected(row, keys):
    return {k: row[k] for k in keys if k in row}


def signature(row, keys, engine):
    return engine.digest(selected(row, keys))


def enabled(state):
    return state['project'].get('lifecycle', {}).get('model') == MODEL


def validate(state, engine, error):
    """Reject manual edits that would silently reinterpret a commitment."""
    for row in state['releases']:
        if row.get('commitment'):
            require(row['commitment'].get('commitment_digest') == signature(row, RELEASE_SCOPE, engine),
                    'Release commitment changed; use revise-release with a source and impact.', error)
    for it in state['iterations']:
        commitment = it.get('commitment')
        if not commitment:
            continue
        require(commitment.get('commitment_digest') == signature(it, SPRINT_SCOPE, engine),
                'Sprint commitment changed; interrupt and plan linked follow-up work.', error)
        for ident, expected in commitment.get('story_digests', {}).items():
            story = engine.find(state['backlog'], ident, 'story')
            require(signature(story, STORY_SCOPE, engine) == expected,
                    'Committed story definition changed; preserve the original and create linked follow-up work.', error)
    for story in state['backlog']:
        if story.get('follows_up'):
            previous = engine.find(state['backlog'], story['follows_up'], 'original story')
            require(previous['iteration_id'] != story['iteration_id'] and previous['parent_id'] == story['parent_id'],
                    'Follow-up work needs a different iteration and the same BL parent.', error)
            seen = {story['id']}
            while previous:
                require(previous['id'] not in seen, 'Follow-up links cannot form a cycle.', error)
                seen.add(previous['id'])
                previous = engine.find(state['backlog'], previous['follows_up'], 'original story') if previous.get('follows_up') else None


def guard(state, request, engine, error, store=None):
    op = request['operation']
    if op == 'plan-iteration' and request['iteration'].get('id'):
        it = engine.find(state['iterations'], request['iteration']['id'], 'iteration')
        require(not it.get('commitment'), 'Sprint is committed; track progress or interrupt and replan.', error)
    if op == 'update-story':
        data = request['story']
        it_id = engine.find(state['backlog'], data['id'], 'story')['iteration_id'] if data.get('id') else data.get('iteration_id')
        it = engine.find(state['iterations'], it_id, 'iteration')
        require(not it.get('closure'), 'Closed sprint stories are historical; create linked follow-up work.', error)
        if not data.get('id'):
            require(not it.get('commitment'), 'Cannot extend a committed sprint.', error)
    if enabled(state) and op in {'prepare', 'start', 'resume', 'prepare-correction', 'mark-implemented'}:
        it_id = request.get('iteration_id')
        if not it_id:
            it_id = engine.find(state['increments'], request.get('increment_id'), 'increment')['iteration_id']
        it = engine.find(state['iterations'], it_id, 'iteration')
        release = engine.find(state['releases'], it['release_id'], 'release')
        require(it.get('commitment') and release.get('commitment') and not it.get('closure'),
                'Reconcile and commit release and sprint before execution.', error)
        selected_ids = set(request.get('increment', {}).get('item_ids', [])) if op == 'prepare' else set(engine.find(state['increments'], request.get('increment_id'), 'increment')['item_ids'])
        require(not any(f['classification'] == 'material-change' and not f.get('resolution') and f.get('story_id') in selected_ids for f in it.get('findings', [])), 'Resolve the material finding before dependent execution.', error)
    if enabled(state) and op == 'close' and request.get('target') == 'iteration':
        raise error('Use conclude-sprint to preserve review, learning and outstanding work.')
    if op == 'reopen' and request.get('target') == 'iteration':
        it = engine.find(state['iterations'], request['iteration_id'], 'iteration')
        require(not it.get('closure'), 'Concluded sprint is historical; plan linked follow-up work.', error)
    if op == 'update-release':
        data = request['release']
        if enabled(state) and data.get('status') == 'released':
            row = engine.find(state['releases'], data['id'], 'release')
            require(effective_fulfillment(store, state, row, engine) == 'completed', 'Assess completed fulfillment before recording publication.', error)
        require(not set(data) & {'commitment', 'fulfillment', 'assessments', 'scope_history'},
                'Use lifecycle operations for commitment, scope history and fulfillment.', error)
    if op == 'plan-iteration':
        require(not set(request['iteration']) & {'commitment', 'closure', 'findings', 'task_progress'},
                'Use lifecycle operations for commitments, findings, progress and closure.', error)


def outstanding(store, state, it, engine, include_followups=False):
    observed = engine.inspect_state(store, state)
    latest = {}
    for inc in observed['increments']:
        if inc['iteration_id'] == it['id'] or include_followups:
            for ident in inc['item_ids']:
                latest[ident] = inc
    covered = {ident for ident, inc in latest.items() if inc['states']['development'] == 'implemented' and inc['effective_verification'] == 'passed' and inc['effective_acceptance'] == 'accepted'}
    if include_followups:
        # Accepted follow-up work can fulfill a release without rewriting the
        # interrupted sprint. Its explicit release assessment supplies the
        # scope-resolution source; a link alone never grants acceptance.
        for story in state['backlog']:
            if story['id'] in covered and story['release_id'] == it['release_id']:
                previous = story.get('follows_up')
                while previous:
                    covered.add(previous)
                    previous = engine.find(state['backlog'], previous, 'original story').get('follows_up')
    return sorted(set(it['item_ids']) - covered)


def apply(store, state, request, engine, error, files):
    op = request['operation']; now = engine.utc_now(); origin = source(request, error)
    def find(group, key):
        return engine.find(state[group], request[key], key)
    if op == 'adopt-lifecycle':
        require(not enabled(state), 'Lifecycle already adopted.', error)
        state['project']['lifecycle'] = {'model': MODEL, 'source': origin, 'adopted_at': now}
        state['project'].setdefault('amendments', []).append({'at': now, 'reason': request['purpose'], 'source': origin})
        return
    require(enabled(state), 'Preview and adopt the iterative lifecycle first.', error)
    if op in {'commit-release', 'revise-release', 'assess-release'}:
        row = find('releases', 'release_id')
        require(row['status'] not in {'released', 'canceled'}, 'Historical release cannot be rewritten.', error)
        if op == 'revise-release':
            require(row.get('commitment') and request.get('impact'), 'A committed release and change impact are required.', error)
            fields = request.get('fields', {})
            require(fields and not set(fields) - set(RELEASE_SCOPE), 'Revise only release scope fields.', error)
            row.setdefault('scope_history', []).append({'at': now, 'source': origin, 'impact': request['impact'], 'previous': selected(row, RELEASE_SCOPE), 'commitment': row.pop('commitment')})
            row.update(copy.deepcopy(fields)); row['fulfillment'] = 'incomplete'
            if 'scope_items' in fields and 'item_ids' not in fields:
                row['item_ids'] = [r['item_id'] for r in fields['scope_items']]
        if op in {'commit-release', 'revise-release'}:
            require(row.get('scope_items') and row.get('exit_conditions'), 'Release commitment needs bounded BL contributions and exit conditions.', error)
            require(not row.get('commitment'), 'Release already committed; use revise-release.', error)
            conditions = row['exit_conditions']
            require(isinstance(conditions, list) and all(isinstance(c, dict) and isinstance(c.get('condition'), str) and c['condition'].strip() for c in conditions), 'Exit conditions require structured condition rows.', error)
            require(len({c['condition'] for c in conditions}) == len(conditions), 'Exit conditions must be distinct.', error)
            row['commitment'] = {'source': origin, 'at': now, 'commitment_digest': signature(row, RELEASE_SCOPE, engine)}
            row['status'] = 'planned'
        else:
            require(row.get('commitment'), 'Commit the release before assessing fulfillment.', error)
            result = request.get('result')
            require(result in {'incomplete', 'completed'}, 'Release assessment is incomplete or completed.', error)
            require(request.get('outcome') and request.get('evidence'), 'Assessment needs actual outcome and evidence references.', error)
            if result == 'completed':
                iterations = [it for it in state['iterations'] if it['release_id'] == row['id']]
                require(iterations and all(it.get('closure') for it in iterations), 'Conclude release sprints before completion.', error)
                require(all(not release_pending(store, state, row, it, engine) for it in iterations), 'Release still has unfinished or unaccepted selected work.', error)
                contributions = request.get('contributions', [])
                require(len(contributions) == len(row['scope_items']) and all(isinstance(r, dict) and r.get('item_id') == c['item_id'] and r.get('contribution') == c['contribution'] and r.get('result') == 'delivered' and r.get('evidence') for r, c in zip(contributions, row['scope_items'])), 'Every committed BL contribution needs matching delivered evidence.', error)
                results = request.get('exit_results', [])
                require(len(results) == len(row['exit_conditions']) and all(isinstance(r, dict) and r.get('condition') == c.get('condition') and r.get('result') == 'passed' and r.get('evidence') for r, c in zip(results, row['exit_conditions'])), 'Every release exit condition needs matching passed evidence.', error)
                require(request.get('acceptance_source'), 'Release acceptance needs an actual user source.', error)
            row['fulfillment'] = result
            row.setdefault('assessments', []).append({'at': now, 'source': origin, **{k: copy.deepcopy(request[k]) for k in ('result', 'outcome', 'evidence', 'exit_results', 'contributions', 'acceptance_source') if k in request}})
        row.setdefault('changes', []).append({'at': now, 'reason': request['purpose'], 'source': origin})
        return
    it = find('iterations', 'iteration_id')
    require(not it.get('closure'), 'Sprint has already concluded.', error)
    if op == 'commit-sprint':
        release = engine.find(state['releases'], it['release_id'], 'release')
        require(release.get('commitment') and release['status'] == 'planned', 'A committed release is required.', error)
        require(not it.get('commitment'), 'Sprint already committed.', error)
        require(it['state'] in {'draft', 'open'}, 'Only draft or open sprints can be committed.', error)
        require(not any(engine.active_development(inc, state['project']) and inc['iteration_id'] != it['id'] for inc in state['increments']), 'Reconcile the already active sprint before committing another.', error)
        if request.get('review_access'):
            require(not it.get('review_access'), 'Existing review access must be preserved during adoption.', error)
            it['review_access'] = request['review_access']
        require(not any(other.get('commitment') and not other.get('closure') for other in state['iterations']), 'Conclude the committed sprint before committing another.', error)
        require(it.get('item_ids') and it.get('review_access') and not it.get('open_decisions'), 'Select work, resolve material decisions and define owner review access.', error)
        stories = [engine.find(state['backlog'], ident, 'story') for ident in it['item_ids']]
        require(all(s['parent_id'] in release['item_ids'] and s.get('criteria') and s.get('dod') and s['type'] != 'unresolved' and not s.get('open_questions') for s in stories), 'Selected work needs release coverage, type, criteria, DoD and resolved questions.', error)
        for inc in state['increments']:
            if inc['iteration_id'] == it['id']:
                for ident, baseline in inc.get('story_baseline', {}).items():
                    story = engine.find(state['backlog'], ident, 'story')
                    require(story['criteria'] == baseline['criteria'] and story['dod'] == baseline['dod'], 'Reconcile the historical delivery baseline before adopting its sprint commitment.', error)
        tasks = it.get('tasks', [])
        require(all(isinstance(t, dict) and t.get('id') and (t.get('story') or t.get('item_id')) in it['item_ids'] for t in tasks) and len({t['id'] for t in tasks}) == len(tasks), 'Tasks need unique IDs and selected story links.', error)
        it['planning_baseline'] = {s['_path']: hashlib.sha256(files[s['_path']].encode()).hexdigest() for s in stories}
        it['commitment'] = {'source': origin, 'at': now, 'commitment_digest': signature(it, SPRINT_SCOPE, engine), 'story_digests': {s['id']: signature(s, STORY_SCOPE, engine) for s in stories}}
    elif op == 'record-finding':
        classification = request.get('classification')
        require(classification in {'implementation-detail', 'defect', 'opportunity', 'material-change'}, 'Unknown finding classification.', error)
        require(request.get('origin') and request.get('impact') and request.get('disposition'), 'Finding needs origin, impact and disposition.', error)
        if classification == 'opportunity':
            engine.find(state['product_backlog'], request.get('backlog_id'), 'opportunity BL')
        if classification in {'implementation-detail', 'defect', 'material-change'}:
            require(request.get('story_id') in it['item_ids'], 'Current-scope finding must name a selected story.', error)
        it.setdefault('findings', []).append({'id': f"FND-{len(it.get('findings', []))+1:03d}", 'at': now, 'source': origin, **{k: request[k] for k in ('classification', 'origin', 'impact', 'disposition', 'backlog_id', 'story_id') if k in request}})
    elif op == 'resolve-finding':
        finding = engine.find(it.get('findings', []), request.get('finding_id'), 'finding')
        require(not finding.get('resolution') and request.get('resolution') and request.get('disposition') in {'within-scope', 'deferred'}, 'Resolve an open finding with rationale and within-scope or deferred disposition.', error)
        if request['disposition'] == 'deferred':
            engine.find(state['product_backlog'], request.get('backlog_id'), 'deferred BL')
            finding['backlog_id'] = request['backlog_id']
        finding.update(resolution=request['resolution'], resolution_source=origin, resolved_at=now, disposition=request['disposition'])
    elif op == 'track-task':
        require(it.get('commitment'), 'Commit the sprint before tracking execution.', error)
        require(request.get('task_id') in {t['id'] for t in it.get('tasks', [])}, 'Unknown committed task.', error)
        require(request.get('status') in {'planned', 'in_progress', 'blocked', 'done'} and request.get('evidence'), 'Task observation needs status and evidence or explanation.', error)
        it.setdefault('task_progress', []).append({'at': now, 'task': request['task_id'], 'status': request['status'], 'evidence': request['evidence'], 'source': origin})
    elif op == 'conclude-sprint':
        require(request.get('result') in {'completed', 'interrupted'} and request.get('reason'), 'Conclude as completed or interrupted with a reason.', error)
        require(request['result'] != 'completed' or it.get('commitment'), 'Commit the sprint before declaring completed fulfillment.', error)
        base = f"release/{it['release_id']}/{it['id']}"
        review = any(r['iteration_id'] == it['id'] for r in state['reviews']) or state.get('report_context', {}).get(base+'/review.md')
        retro = any(r['iteration_id'] == it['id'] for r in state['improvements']) or state.get('report_context', {}).get(base+'/retrospective.md')
        require(review and retro, 'Record actual review and retrospective before sprint closure.', error)
        pending = outstanding(store, state, it, engine)
        require(request.get('outstanding_story_ids') == pending, 'Name exactly the outstanding selected stories; closure does not complete them.', error)
        require(request['result'] != 'completed' or not pending, 'Cannot complete a sprint with outstanding work.', error)
        # Delegate administrative close to the existing engine, preserving evidence.
        for inc in state['increments']:
            if inc['iteration_id'] == it['id']:
                engine.mutate(state, {**request, 'operation': 'close', 'target': 'increment', 'increment_id': inc['id']}, store.root)
        it['state'] = 'closed'
        it['closure'] = {'at': now, 'result': request['result'], 'source': origin, 'reason': request['reason'], 'outstanding_story_ids': pending}
    it.setdefault('changes', []).append({'at': now, 'reason': request['purpose'], 'source': origin})


def release_pending(store, state, release, it, engine):
    pending = outstanding(store, state, it, engine, include_followups=True)
    return [ident for ident in pending if engine.find(state['backlog'], ident, 'story')['parent_id'] in release['item_ids']]


def effective_fulfillment(store, state, row, engine):
    recorded = row.get('fulfillment', 'not_assessed')
    if recorded != 'completed':
        return recorded
    iterations = [it for it in state['iterations'] if it['release_id'] == row['id']]
    if not iterations or any(not it.get('closure') or release_pending(store, state, row, it, engine) for it in iterations):
        return 'needs_reassessment'
    return 'completed'


def preview(store):
    observed = store.inspect()
    return {'status': 'ok', 'source_fingerprint': observed['fingerprint'], 'revision': observed['revision'],
            'model': MODEL, 'already_adopted': enabled(observed),
            'changes': ['Record lifecycle adoption in constitution; preserve documents, identities, evidence and approvals.'],
            'reconciliation': [{'iteration': it['id'], 'commitment': 'record actual agreement before dependent execution'} for it in observed['iterations'] if it['state'] not in {'closed', 'canceled'} and not it.get('commitment')],
            'release_reconciliation': [r['id'] for r in observed['releases'] if r['status'] not in {'released', 'canceled'} and not r.get('commitment')],
            'interface_content': [k for k in ('screens', 'states', 'accessibility') if (observed.get('product_design') or {}).get(k)],
            'limitations': ['Existing interface content is not moved.', 'No approval, commitment, completion or publication is inferred.']}


def adopt(store, request):
    report = preview(store)
    if report['already_adopted']:
        return {'status': 'already_applied', 'revision': report['revision']}
    if request.get('expected_source_fingerprint') != report['source_fingerprint']:
        return {'status': 'conflict', 'errors': ['Lifecycle adoption preview is stale.']}
    return store.transaction({'operation': 'adopt-lifecycle', 'operation_id': 'adopt-lifecycle-'+report['source_fingerprint'],
                              'purpose': 'Adopt strategic and operational lifecycle without reinterpreting history',
                              'expected_revision': report['revision'], 'expected_fingerprint': report['source_fingerprint'],
                              'authorization_source': request.get('authorization_source')})
