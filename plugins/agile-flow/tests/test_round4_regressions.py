from __future__ import annotations

import unittest

from test_records import RecordsHarness


class RoundFourRegressions(RecordsHarness, unittest.TestCase):
    def test_repeated_checks_preserve_acceptance_but_changed_files_do_not(self):
        self.prepared()
        for operation in ('start', 'mark-implemented'):
            self.mutate(dict(operation=operation, operation_id=operation, purpose=operation, increment_id='INC-0001'))
        covered = self.root / 'app.py'
        covered.write_text('print("Hello")\n')

        def check(name, attempt, **extra):
            result = self.mutate(dict(operation='record-evidence', operation_id=attempt, purpose=attempt,
                evidence=dict(increment_id='INC-0001', check=name, result='passed', scope='Greeting', paths=['app.py'], **extra)))
            self.assertEqual(result['status'], 'applied')

        check('unit', 'unit-first')
        self.mutate(dict(operation='record-review', operation_id='accept', purpose='Accept with manual check outstanding',
            review=dict(increment_id='INC-0001', decision='accepted', parts=['Returns greeting'], user_quote='I accept the delivery with manual verification outstanding.')))
        for name, attempt in [('manual', 'manual-first'), ('unit', 'unit-rerun')]:
            check(name, attempt)
            inc = self.inspect()['increments'][0]
            self.assertEqual((inc['delivery_revision'], inc['effective_verification'], inc['effective_acceptance']), (1, 'passed', 'accepted'))
            self.assertIn('Current acceptance: accepted', (self.root / '.agile-flow/views/increments/INC-0001.md').read_text())
        covered.write_text('print("Hello")  # formatting comment\n')
        for name in ('unit', 'manual'):
            check(name, name + '-changed', change_impact='non_behavioral', impact_reason='Comment only')
        inc = self.inspect()['increments'][0]
        self.assertEqual((inc['effective_verification'], inc['effective_acceptance']), ('passed', 'pending'))
        self.assertEqual(len(self.inspect()['reviews']), 1)
