import sys
from mozfederatedpolicybuilder import get_policy
try:
    # python 3.4+ should use builtin unittest.mock not mock package
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_mozilla_federated_aws_policy_builder():
    with open('tests/cloudformation.yaml') as f:
        expected_cloudformation_result_yaml = f.read()
    with open('tests/awscli.txt') as f:
        expected_awscli_result = f.read()
    with open('tests/cloudformation.json') as f:
        expected_cloudformation_result_json = f.read()
    with open('tests/policy.txt') as f:
        expected_policy_result = f.read()
    with open('tests/cloudformation_with_managed_policy.yaml') as f:
        expected_cloudformation_managed_policy_result = f.read()
    with open('tests/awscli_with_managed_policy.txt') as f:
        expected_awscli_managed_policy_result = f.read()

    with patch.object(
            sys, 'argv', ['', 'c', 'foo,bar', 'baz', '123456789012', 'none']):
        good_c_result = get_policy()
    assert good_c_result == expected_cloudformation_result_yaml

    with patch.object(
            sys,
            'argv',
            ['', 'cloud', 'foo,bar', 'baz', '123456789012', 'none']):
        good_cloudformation_result = get_policy()
    assert good_cloudformation_result == expected_cloudformation_result_yaml

    with patch.object(
            sys, 'argv', ['', 'a', 'foo,bar', 'baz', '123456789012', 'none']):
        good_awscli_result = get_policy()
    assert good_awscli_result == expected_awscli_result

    with patch.object(
            sys,
            'argv',
            ['', 'json', 'foo,bar', 'baz', '123456789012', 'none']):
        good_cloudformation_result_json = get_policy()
    # print(good_cloudformation_result_json)
    # print(expected_cloudformation_result_json)
    assert (
            good_cloudformation_result_json ==
            expected_cloudformation_result_json)

    with patch.object(
            sys,
            'argv',
            ['', 'p', 'foo,bar', 'baz', '123456789012']):
        good_json_policy_result = get_policy()
    assert good_json_policy_result == expected_policy_result

    with patch.object(
            sys,
            'argv',
            ['', 'c', 'foo,bar', 'baz', '123456789012',
             'arn:aws:iam::aws:policy/ReadOnlyAccess']):
        good_cloudformation_managed_policy_result = get_policy()
    assert (
        good_cloudformation_managed_policy_result ==
        expected_cloudformation_managed_policy_result)

    with patch.object(
            sys,
            'argv',
            ['', 'a', 'foo,bar', 'baz', '123456789012',
             'arn:aws:iam::aws:policy/ReadOnlyAccess']):
        good_awcli_managed_policy_result = get_policy()
    assert (
        good_awcli_managed_policy_result ==
        expected_awscli_managed_policy_result)
