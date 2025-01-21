from ios_build import functions

import unittest

class TestParser(unittest.TestCase):
    def testSortCMakeOptions(self):
        fail_examples = [
            ["NAME-ME"],
            ["NAME=ME=YOU"],
            ["CMAKE_TOOLCHAIN_FILE=file"],
            ["PLATFORM=this"],
            ["CMAKE_INSTALL_PREFIX=dir"],
            ["OPTION1=value1", "OPTION1=value2"]
        ]
        success_examples = [
            [],
            ["VALUE1=value1"],
            ["VALUE1=value1", "VALUE2=123456"],
            ["VALUE1=value1", "VALUE2=123456", "VALUE3=true", "VALUE4=false"]
        ]

        expected_results = [
            {},
            {"VALUE1": "value1"},
            {"VALUE1": "value1", "VALUE2": "123456"},
            {"VALUE1": "value1", "VALUE2": "123456", "VALUE3": "true", "VALUE4": "false"}
        ]

        for example in fail_examples:
            with self.assertRaises(ValueError):
                ios_build.sortCMakeOptions(example)

        self.assertEqual(len(success_examples), len(expected_results))
        
        for i in range(len(success_examples)):
            example_input = success_examples[i]
            expected_result = expected_results[i]

            result = ios_build.sortCMakeOptions(example_input)
            self.assertDictEqual(result, expected_result)

