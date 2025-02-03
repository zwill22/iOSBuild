from ios_build import parser

import json
import unittest
import argparse


class TestParseTools(unittest.TestCase):
    def testSortCMakeOptions(self):
        fail_examples = [
            ["NAME-ME"],
            ["NAME=ME=YOU"],
            ["CMAKE_TOOLCHAIN_FILE=file"],
            ["PLATFORM=this"],
            ["CMAKE_INSTALL_PREFIX=dir"],
            ["OPTION1=value1", "OPTION1=value2"],
        ]
        success_examples = [
            [],
            ["VALUE1=value1"],
            ["VALUE1=value1", "VALUE2=123456"],
            ["VALUE1=value1", "VALUE2=123456", "VALUE3=true", "VALUE4=false"],
        ]

        expected_results = [
            {},
            {"VALUE1": "value1"},
            {"VALUE1": "value1", "VALUE2": "123456"},
            {
                "VALUE1": "value1",
                "VALUE2": "123456",
                "VALUE3": "true",
                "VALUE4": "false",
            },
        ]

        for example in fail_examples:
            with self.assertRaises(ValueError):
                parser.sortCMakeOptions(example)

        self.assertEqual(len(success_examples), len(expected_results))

        for i in range(len(success_examples)):
            example_input = success_examples[i]
            expected_result = expected_results[i]

            result = parser.sortCMakeOptions(example_input)
            self.assertDictEqual(result, expected_result)

    def testLoadJson(self):
        loaded_json = parser.loadJson("tests/example.json")
        self.assertDictEqual(loaded_json, {"key1": "value1", "key2": "value2"})

    def testSortArgsEmpty(self):
        namespace = argparse.Namespace()

        with self.assertRaises(AttributeError):
            parser.sortArgs(namespace)

        namespace.cmake_options = None
        namespace.platform_json = None
        namespace.platform_options = None

        expected_result = {
            "cmake_options": {}
        }

        with self.assertRaises(AttributeError):
            parser.sortArgs(namespace)

        namespace.dev_print = False
        expected_result["dev_print"] = False

        result = parser.sortArgs(namespace)

        self.assertDictEqual(result, expected_result)

    def testSortArgsConflict(self):
        namespace = argparse.Namespace()

        namespace.cmake_options = None
        namespace.platform_json = "tests/example.json"
        namespace.platform_options = "\{\}"

        namespace.dev_print = False

        with self.assertRaises(AssertionError):
            parser.sortArgs(namespace)

    def testSortArgsPlatformJson(self):
        namespace = argparse.Namespace()

        namespace.cmake_options = None
        namespace.platform_json = "tests/example.json"
        namespace.platform_options = None

        namespace.dev_print = False

        expected_result = {
            "dev_print": False,
            "cmake_options": {},
            "platform_options": {"key1": "value1", "key2": "value2"}
        }

        result = parser.sortArgs(namespace)
        
        self.assertDictEqual(result, expected_result)

        namespace.dev_print = True
        expected_result["dev_print"] = True
        self.assertDictEqual(parser.sortArgs(namespace), expected_result)

    def testSortArgsPlatformOptions(self):
        namespace = argparse.Namespace()

        namespace.cmake_options = None
        namespace.platform_json = None
        options = {"key": "value"}
        namespace.platform_options = json.dumps(options)
        namespace.dev_print = False

        expected_result = {
            "dev_print": False,
            "cmake_options": {},
            "platform_options": options
        }

        result = parser.sortArgs(namespace)

        self.assertDictEqual(result, expected_result)

    def testSortArgsCMakeOptions(self):
        namespace = argparse.Namespace()

        namespace.cmake_options = ["CHEESE=MELTED", "OPTION=FLAG"]
        namespace.platform_json = None
        namespace.platform_options = None

        namespace.dev_print = False

        expected_result = {}
        expected_result["dev_print"] = False
        expected_result["cmake_options"] = {
            "CHEESE": "MELTED",
            "OPTION": "FLAG"
        }

        result = parser.sortArgs(namespace)

        self.assertDictEqual(result, expected_result)
