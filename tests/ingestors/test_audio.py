# -*- coding: utf-8 -*-
import datetime
from ..support import TestCase


class AudioIngestorTest(TestCase):

    def test_audio(self):
        fixture_path = self.fixture('memo.m4a')
        result = self.manager.ingest(fixture_path)
        self.assertEqual(result.status, result.STATUS_SUCCESS)
        self.assertEqual(result.title, 'Core Media Audio')
        self.assertEqual(result.generator, 'com.apple.VoiceMemos (iOS 11.4)')
        self.assertEqual(
            result.created_at, datetime.datetime(2018, 6, 20, 12, 9, 42)
        )
        self.assertEqual(result.duration, '2808')
        self.assertEqual(result.sampling_rate, '44.1')
        self.assertIn('audio', result.flags)
