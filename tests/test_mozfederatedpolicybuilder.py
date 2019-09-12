import sys
from mozfederatedpolicybuilder import get_policy
try:
    # python 3.4+ should use builtin unittest.mock not mock package
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_mozilla_federated_aws_policy_builder():
    with open('tests/expected_cloudformation_result.yaml') as f:
        expected_cloudformation_result = f.read()
    with open('tests/expected_awscli_result.txt') as f:
        expected_awscli_result = f.read()
    with open('tests/expected_json_result.json') as f:
        expected_json_result = f.read()

    with patch.object(sys, 'argv', ['', 'c', 'foo,bar', 'baz']):
        good_c_result = get_policy()
    assert good_c_result == expected_cloudformation_result

    with patch.object(
            sys, 'argv', ['', 'cloud', 'foo,bar', 'baz', '123456789012']):
        good_cloudformation_result = get_policy()
    assert good_cloudformation_result == expected_cloudformation_result

    with patch.object(
            sys, 'argv', ['', 'a', 'foo,bar', 'baz', '123456789012']):
        good_awscli_result = get_policy()
    assert good_awscli_result == expected_awscli_result

    with patch.object(
            sys, 'argv', ['', 'json', 'foo,bar', 'baz', '123456789012']):
        good_json_result = get_policy()
    print(good_json_result)
    print(expected_json_result)
    assert good_json_result == expected_json_result
