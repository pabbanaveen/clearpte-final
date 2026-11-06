import unittest

from fastapi import HTTPException

from app.api.uploadquestions import parse_array


class UploadArrayParsingTests(unittest.TestCase):
    def test_json_array_is_preserved(self):
        self.assertEqual(parse_array(["one", "two"]), ["one", "two"])

    def test_json_encoded_array_is_decoded(self):
        self.assertEqual(parse_array('["one", "two"]'), ["one", "two"])

    def test_legacy_delimited_values_are_normalized(self):
        self.assertEqual(parse_array("one; two, three"), ["one", "two", "three"])

    def test_numeric_array_is_parsed_to_integers(self):
        self.assertEqual(parse_array("[1, 2, 3]", int), [1, 2, 3])

    def test_invalid_integer_value_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            parse_array("1,not-a-number", int)
        self.assertEqual(raised.exception.status_code, 422)

    def test_empty_values_return_none(self):
        self.assertIsNone(parse_array(None))
        self.assertIsNone(parse_array(""))
        self.assertIsNone(parse_array([]))


if __name__ == "__main__":
    unittest.main()
