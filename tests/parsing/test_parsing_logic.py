import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import json
from pathlib import Path

# Adjust the path to import from the parent directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from parse_sample_tweets import (
    parse_single_tweet_v2,
    translate_event_type,
    GLOBAL_EVENT_TYPE_MAPPING,
    get_location_hierarchy_and_aliases,
    load_geo_data,
    GLOBAL_LOCATION_LOOKUP,
    GLOBAL_GEO_HIERARCHY,
    extract_word_buckets,
    extract_target_groups,
    extract_communities,
    extract_schemes_mentioned
)

class TestParsingLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load all necessary global data once for all tests
        load_geo_data()

    def setUp(self):
        # Mock the ParsingOrchestrator for each test
        self.orchestrator_mock = MagicMock()
        self.orchestrator_mock.location_matcher = MagicMock()
        
        # Default mock behavior for orchestrator.parse_tweet
        self.orchestrator_mock.parse_tweet.return_value = {
            "tweet_id": "test_id",
            "event_type": "other",
            "event_type_confidence": 0.3,
            "event_date": "2025-11-10T08:15:11.402000+00:00",
            "date_confidence": 0.6,
            "locations": [],
            "people_mentioned": [],
            "organizations": [],
            "schemes_mentioned": [],
            "overall_confidence": 0.3,
            "needs_review": True,
            "review_status": "pending",
            "_metadata": {
                "language": {"language": "hindi", "confidence": 0.8},
                "classification_keywords": []
            }
        }
        
        # Default mock behavior for location_matcher.extract_locations
        self.orchestrator_mock.location_matcher.extract_locations.return_value = []

    # --- Test Cases for Event Type Translation ---
    def test_translate_event_type_basic(self):
        primary, secondary = translate_event_type("rally", "some text")
        self.assertEqual(primary, "रैली")
        self.assertEqual(secondary, [])

    def test_translate_event_type_general_shubhkaamna(self):
        primary, secondary = translate_event_type("general", "शुभकामना संदेश")
        self.assertEqual(primary, "शुभकामना / बधाई")
        self.assertEqual(secondary, [])

    def test_translate_event_type_community_meeting_prashasan(self):
        primary, secondary = translate_event_type("community_meeting", "प्रशासनिक बैठक")
        self.assertEqual(primary, "प्रशासनिक समीक्षा बैठक")
        self.assertEqual(secondary, [])
    
    # --- Test Cases for Location Hierarchy ---
    def test_location_hierarchy_raipur(self):
        mock_matched_location = {
            'name': 'रायपुर', 
            'name_en': 'Raipur', 
            'type': 'city', 
            'confidence': 0.9, 
            'state': 'Chhattisgarh', 
            'district': '', 
            'block': '', 
            'assembly_constituency': ''
        }
        structured_loc, hierarchy_path, aliases = get_location_hierarchy_and_aliases(mock_matched_location)
        
        self.assertEqual(structured_loc['district'], 'रायपुर')
        self.assertEqual(structured_loc['assembly'], 'रायपुर शहर उत्तर')
        self.assertEqual(structured_loc['block'], 'रायपुर')
        self.assertIn('छत्तीसगढ़', hierarchy_path)
        self.assertIn('रायपुर जिला', hierarchy_path)
        self.assertIn('रायपुर शहर उत्तर विधानसभा', hierarchy_path)
        self.assertIn('रायपुर विकासखंड', hierarchy_path)
        self.assertIn('रायपुर', aliases)
        self.assertIn('raaypur', aliases)
        self.assertEqual(structured_loc['canonical_key'], 'CG_रायपुर_रायपुर_शहर_उत्तर_रायपुर_रायपुर_रायपुर')

    def test_location_hierarchy_default_cg(self):
        # Test when no location is extracted, should default to Chhattisgarh
        mock_matched_location = {} # No location found
        structured_loc, hierarchy_path, aliases = get_location_hierarchy_and_aliases(mock_matched_location)
        self.assertEqual(structured_loc['canonical_key'], '')
        self.assertEqual(structured_loc['canonical_key'], '')
        self.assertEqual(hierarchy_path, []) # Expect empty hierarchy path
        self.assertEqual(aliases, [])      # Expect empty aliases
        self.assertEqual(structured_loc['district'], '') # Should be empty for default
    
    # --- Test Cases for New Entity Extraction ---
    def test_extract_word_buckets(self):
        text = "यह एक विकास का कार्य है और इसमें कई समस्याएँ हैं।"
        buckets = extract_word_buckets(text)
        self.assertIn('सकारात्मक', buckets)
        self.assertIn('नकारात्मक', buckets)
        self.assertIn('सरकारी_कार्य', buckets)
        self.assertNotIn('जन_सहभागिता', buckets)
        self.assertEqual(len(buckets), 3)

    def test_extract_target_groups(self):
        text = "युवा और किसान हमारे देश का भविष्य हैं।"
        groups = extract_target_groups(text)
        self.assertIn('युवा', groups)
        self.assertIn('किसान', groups)
        self.assertEqual(len(groups), 2)
    
    def test_extract_communities(self):
        text = "सिख और हिन्दू समुदाय ने मिलकर यह उत्सव मनाया।"
        communities = extract_communities(text)
        self.assertIn('सिख', communities)
        self.assertIn('हिन्दू', communities)
        self.assertEqual(len(communities), 3)

    def test_extract_schemes_mentioned(self):
        text = "प्रधानमंत्री आवास योजना के तहत लाभार्थियों को घर मिले।"
        schemes = extract_schemes_mentioned(text)
        self.assertIn('प्रधानमंत्री आवास योजना', schemes)
        self.assertEqual(len(schemes), 1)

    # --- Test Cases for Confidence Scoring ---
    def test_confidence_scoring_full_match(self):
        # Mock orchestrator to return an event_type with high confidence
        self.orchestrator_mock.parse_tweet.return_value['event_type'] = 'rally'
        self.orchestrator_mock.parse_tweet.return_value['event_type_confidence'] = 0.9
        
        # Mock location_matcher to find a location with high confidence
        self.orchestrator_mock.location_matcher.extract_locations.return_value = [
            {'name': 'रायपुर', 'name_en': 'Raipur', 'type': 'city', 'confidence': 0.95, 'state': 'Chhattisgarh', 'district': '', 'block': '', 'assembly_constituency': ''}
        ]
        
        raw_tweet = {
            "tweet_id": "1",
            "text": "आज रायपुर में युवा किसान रैली हुई जिसमें विकास की बातें की गईं और प्रधानमंत्री आवास योजना का उल्लेख किया गया।",
            "created_at": "2025-11-10T08:15:11.402000Z"
        }
        
        parsed_output = parse_single_tweet_v2(raw_tweet, self.orchestrator_mock)
        
        # Expected confidences:
        # event_type_confidence = 0.9
        # location_confidence = 0.95
        # word_buckets_confidence = 0.7 (विकास, सरकारी_कार्य)
        # target_groups_confidence = 0.7 (युवा, किसान)
        # communities_confidence = 0.0
        # schemes_mentioned_confidence = 0.7 (प्रधानमंत्री आवास योजना)
        
        # (0.9 + 0.95 + 0.7 + 0.7 + 0.0 + 0.7) / 5 (excluding 0.0 for communities) = 3.95 / 5 = 0.79
        self.assertAlmostEqual(parsed_output['parsed_data_v2']['confidence'], 0.79, places=2)
        self.assertEqual(parsed_output['parsed_data_v2']['event_type'], 'रैली')
        self.assertEqual(parsed_output['parsed_data_v2']['location']['district'], 'रायपुर')
        self.assertIn('युवा', parsed_output['parsed_data_v2']['target_groups'])
        self.assertIn('प्रधानमंत्री आवास योजना', parsed_output['parsed_data_v2']['schemes_mentioned'])
        self.assertIn('सकारात्मक', parsed_output['parsed_data_v2']['word_buckets'])

    def test_confidence_scoring_no_matches(self):
        # Mock orchestrator to return an event_type with low confidence
        self.orchestrator_mock.parse_tweet.return_value['event_type'] = 'other'
        self.orchestrator_mock.parse_tweet.return_value['event_type_confidence'] = 0.1
        self.orchestrator_mock.parse_tweet.return_value['overall_confidence'] = 0.1 # Ensure old overall_confidence is low
        
        # Mock location_matcher to find no locations
        self.orchestrator_mock.location_matcher.extract_locations.return_value = []
        
        raw_tweet = {
            "tweet_id": "2",
            "text": "एक सामान्य ट्वीट।",
            "created_at": "2025-11-10T08:15:11.402000Z"
        }
        
        parsed_output = parse_single_tweet_v2(raw_tweet, self.orchestrator_mock)
        
        # Expected confidences:
        # event_type_confidence = 0.1
        # location_confidence = 0.5 (fallback to CG)
        # word_buckets_confidence = 0.0
        # target_groups_confidence = 0.0
        # communities_confidence = 0.0
        # schemes_mentioned_confidence = 0.0
        
        # (0.1 + 0.5) / 2 = 0.3
        self.assertAlmostEqual(parsed_output['parsed_data_v2']['confidence'], 0.3, places=2)
        self.assertEqual(parsed_output['parsed_data_v2']['event_type'], 'अन्य')
        self.assertEqual(parsed_output['parsed_data_v2']['location']['canonical_key'], 'CG')
        self.assertEqual(parsed_output['parsed_data_v2']['word_buckets'], [])

    def test_orchestrator_parse_tweet_failure(self):
        # Mock orchestrator.parse_tweet to return None
        self.orchestrator_mock.parse_tweet.return_value = None
        
        raw_tweet = {
            "tweet_id": "3",
            "text": "यह एक परीक्षण ट्वीट है।",
            "created_at": "2025-11-10T08:15:11.402000Z"
        }
        
        parsed_output = parse_single_tweet_v2(raw_tweet, self.orchestrator_mock)
        
        # When old_parsed_data is None, parsed_data_v2 should still be initialized with defaults.
        # Event type will be 'अन्य', location will be 'CG', other extractions will run.
        # Confidence calculation will use default location_confidence (0.5) and any new entity extractions.
        
        # Here, "word_buckets" will be empty, etc.
        # event_type_confidence = 0.0 (because old_parsed_data is None)
        # location_confidence = 0.5 (fallback to CG default)
        # word_buckets_confidence = 0.0
        # ...
        
        # (0.5) / 1 = 0.5
        self.assertAlmostEqual(parsed_output['parsed_data_v2']['confidence'], 0.5, places=2)
        self.assertEqual(parsed_output['parsed_data_v2']['event_type'], 'अन्य')
        self.assertEqual(parsed_output['parsed_data_v2']['location']['canonical_key'], 'CG')
        self.assertEqual(parsed_output['parsed_data_v2']['word_buckets'], [])

if __name__ == '__main__':
    unittest.main()