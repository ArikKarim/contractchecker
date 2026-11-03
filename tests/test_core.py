import json
from pathlib import Path
import unittest
from contractchecker.rules import analyze, features
from contractchecker.metrics import binary_metrics, wilson
from contractchecker.model import NaiveBayes

class CoreTests(unittest.TestCase):
    def test_evidence_offsets_original_unicode(self):
        text='“MAE” means a change that would\nreasonably be expected to harm operations; excluding actions taken by Buyer.'
        result=analyze(text)
        for item in list(result['features'].values())+result['review_prompts']:
            e=item['evidence']
            if e:self.assertEqual(text[e['start']:e['end']],e['quote'])

    def test_exclusion_does_not_supply_forward_trigger(self):
        text='MAE means an adverse business change; provided, however, that forecasts would reasonably be expected to be excluded.'
        self.assertFalse(features(text)['forward_looking']['value'])

    def test_input_validation(self):
        for bad in ('', ' ',None,'x'*100001):
            with self.assertRaises(ValueError):analyze(bad)

    def test_closing_ability_wording_regression(self):
        for text in ['MAE means an effect on the ability of the Company to consummate the Merger.',
                     'MAE means an event that prevents the Company from consummating the Merger.']:
            self.assertTrue(features(text)['consummation']['value'])

    def test_requested_action_is_not_buyer_action(self):
        self.assertFalse(features('MAE means an adverse change, excluding actions taken by the Company at the written request of Parent.')['buyer_actions']['value'])
        self.assertTrue(features('MAE means an adverse change, excluding actions taken by Parent.')['buyer_actions']['value'])

    def test_confusion_matrix(self):
        m=binary_metrics([1,1,0,0],[1,0,1,0])
        self.assertEqual((m['tp'],m['tn'],m['fp'],m['fn']),(1,1,1,1))
        self.assertEqual(m['macro_f1'],.5)
        lo,hi=wilson(5,10)
        self.assertAlmostEqual(lo,1-hi)

    def test_model_learns_a_signal(self):
        m=NaiveBayes().fit(['red apple','red berry','blue sea','blue sky'],[1,1,0,0])
        self.assertEqual(m.predict('red apple'),1)
        self.assertEqual(m.predict('blue sea'),0)

    def test_dataset_integrity_and_groups(self):
        root=Path(__file__).resolve().parents[1]
        rs=[json.loads(x) for x in (root/'data/maud_mae.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(len({r['contract_id'] for r in rs}),152)
        for a,b in [('train','dev'),('train','test'),('dev','test')]:
            self.assertFalse({r['normalized_group'] for r in rs if r['split']==a}&{r['normalized_group'] for r in rs if r['split']==b})
        for r in rs:
            self.assertEqual(len(r['labels']),4)
            self.assertEqual(r['contains_source_omission'],'<omitted>' in r['text'])

if __name__=='__main__':unittest.main()
