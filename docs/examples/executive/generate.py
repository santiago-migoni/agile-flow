"""Generate the synthetic executive-reading example through real transactions."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--plugin', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.plugin.resolve()))
from scripts.clean_store import CleanStore

with tempfile.TemporaryDirectory() as tmp:
    store = CleanStore(tmp)
    sequence = 0
    def op(operation, **values):
        global sequence
        sequence += 1
        request = dict(operation=operation, operation_id='example-'+str(sequence), purpose='Consolidate the synthetic workshop example', provenance='Synthetic owner conversation', **values)
        if store.path.exists():
            observed = store.inspect()
            request.update(expected_revision=observed['revision'], expected_fingerprint=observed['fingerprint'])
        result = store.transaction(request)
        assert result['status'] == 'applied', result
    op('initialize', project={'name': 'Workshop', 'purpose': 'Replace manual workspace setup with a coherent owner workflow.', 'background': 'The owner assembles development workspaces manually and wants repeatable project setup.', 'next_step': 'Choose the first owner task that the product should replace.'})
    decisions = [{'id': 'PD-001', 'decision': 'Workspace types may be created independently.', 'scope': 'Workspace creation', 'basis': 'user-definition', 'source': 'Synthetic owner: create only the workspace types I need.', 'status': 'decided'}]
    decisions += [{'id': f'PD-{n:03}', 'decision': f'Configuration agreement {n}: preserve the owner-selected workspace setting.', 'scope': 'Synthetic configuration surface '+str(n), 'basis': 'user-definition', 'source': 'Synthetic configuration discussion', 'status': 'decided'} for n in range(2, 22)]
    op('update-product-design', document={'purpose': 'Define workspace setup independently of delivery scheduling.', 'decisions': decisions,
        'rules': [{'id': 'RUL-001', 'rule': 'Apply the workspace-type agreement to the creation form.', 'scope': 'Creation form', 'status': 'confirmed', 'agreement_refs': ['product-design.md::PD-001']}],
        'journeys': [{'id': 'JRN-001', 'actor': 'Owner', 'trigger': 'New project', 'steps': ['Name the project', 'Choose a workspace type', 'Save a draft'], 'outcome': 'A configured workspace', 'applicability': 'The owner chooses the type as needed.', 'status': 'confirmed', 'agreement_refs': ['product-design.md::PD-001']}],
        'states': [{'id': f'ST-{n:03}', 'context': 'Workspace', 'state': f'Candidate state {n}', 'behavior': f'Detailed technical proposal {n}, still subject to product discussion.', 'recovery': 'Investigate during workflow design.', 'status': 'proposed'} for n in range(1, 15)],
        'open_questions': [{'id': 'Q-001', 'question': 'Should the first useful outcome replace setup or daily workspace operation?', 'impact': 'Defines the initial product boundary.', 'timing': 'now', 'status': 'open'}],
        'alternatives': [{'id': 'ALT-001', 'topic': 'Creation', 'option': 'Automatically create all workspace types', 'status': 'rejected'}, {'id': 'ALT-002', 'topic': 'Creation', 'option': 'Let the owner choose workspace types', 'status': 'decided'}]})
    op('update-architecture', document={'purpose': 'Preserve implementation alternatives for later discussion.',
        'components': [{'id': 'COMP-001', 'component': 'Shared runtime', 'boundary': 'Retained historical alternative', 'status': 'rejected'}, {'id': 'COMP-002', 'component': 'Isolated workspace runtime', 'boundary': 'Proposal; no implementation approval', 'status': 'proposed'}],
        'operations': [{'id': 'OPS-001', 'concern': 'Automatic provisioning', 'approach': 'Provision while editing', 'status': 'superseded'}, {'id': 'OPS-002', 'concern': 'Explicit provisioning', 'approach': 'Discuss a separate provision action', 'status': 'proposed'}],
        'open_questions': [{'id': 'AR-Q-001', 'question': 'Which configuration format supports repeatable setup?', 'impact': 'Technical design', 'timing': 'investigate'}]})
    op('update-backlog', item={'purpose': 'Configure a project workspace', 'value': 'Reduce manual setup effort.', 'outcome': 'The owner prepares a workspace without assembling configuration by hand.', 'scope': ['Project and workspace configuration'], 'references': ['product-design.md::PD-001']})
    op('update-collaboration', context={'focus': 'Choose the first useful owner outcome', 'level': 'strategic',
        'synthesis': 'Workspace independence is defined. The first useful outcome is still open; technical workflow proposals remain available for later design.',
        'highlights': [{'text': 'Workspace creation follows the owner-selected type.', 'references': ['product-design.md::PD-001']}],
        'can_continue': 'Compare setup and daily-operation outcomes using the existing needs.'})
    observed = store.inspect()
    assert not observed['document_changes']
    args.output.mkdir(parents=True, exist_ok=True)
    for source in store.directory.rglob('*.md'):
        if '.internal' in source.parts: continue
        destination = args.output/source.relative_to(store.directory)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    summary = (args.output/'summary.md').read_text()
    print(json.dumps({'summary_bytes': len(summary.encode()), 'summary_lines': len(summary.splitlines()), 'decisions': len(decisions), 'state_proposals': 14, 'documents': observed['documents']}))
