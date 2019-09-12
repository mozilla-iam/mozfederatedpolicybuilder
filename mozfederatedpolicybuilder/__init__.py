import json
import sys
from collections import OrderedDict
import string
import yaml

try:
    input = raw_input
except NameError:
    pass

FORMAT_PROMPT = '''Policy format options :
* c/cloudformation : A YAML CloudFormation template which provisions a
    federated IAM role
* j/json-cloudformation : A JSON CloudFormation template which provisions a
    federated IAM role
* a/awscli : An AWS CLI command line command which creates a federated IAM role
* p/policy : The JSON trust relationship portion of the IAM policy (this can be
    copy pasted into the web console)'''

GROUPS_PROMPT = '''User groups can be granted access to the federated IAM role.
* Supported : Allow users in the group foo to assume the IAM role : "foo"
* Supported : Allow users in the group foo as well as users in the group bar to
    assume the IAM role : "foo,bar"
* Supported : Allow users in any group that begins with "foo_" : "foo_*"'''

ACCOUNT_ID_PROMPT = '''Enter the AWS Account ID of the account that you will
deploy the IAM role in. This is a 12 digit number.'''

IDENTITY_PROVIDER_URL = 'auth.mozilla.auth0.com/'
AUDIENCE_VALUE = 'N7lULzWtfVUDGymwDs0yDEq6ZcwmFazj'
# Enable PyYAML support for OrderedDict
yaml.add_representer(
    OrderedDict,
    lambda dumper, data: dumper.represent_dict(
        getattr(data, "viewitems" if sys.version_info < (3,) else "items")()),
    Dumper=yaml.SafeDumper)


def capitalize(s):
    if len(s) == 0:
        return s
    else:
        return s[0].capitalize() + s[1:]


def is_role_name_allowed(role_name):
    # Allowed characters are alphanumeric, including the following common
    # characters: plus (+), equal (=), comma (,), period (.), at (@),
    # underscore (_), and hyphen (-).
    allowed_characters = set(string.ascii_letters + '+=,.@_-')
    return False if set(role_name) - allowed_characters else True


def get_json(o):
    return json.dumps(
        o, indent=4,  separators=(',', ': '), sort_keys=False) + "\n"


def get_yaml(o):
    return yaml.safe_dump(data=o, default_flow_style=False)


def create_cloudformation_template(
        role_name,
        assume_role_policy_document,
        policy_name,
        policy,
        groups,
        formatter):
    resource_name = (
        ''.join([capitalize(x) for x in role_name.split('_')]) + 'IAMRole'
        if role_name else 'MyFederatedIAMRole')
    template = OrderedDict()
    template['AWSTemplateFormatVersion'] = '2010-09-09'
    template['Description'] = (
        'Federated IAM Role which the groups {} are permitted to '
        'assume'.format(', '.join(groups)))
    template['Resources'] = {
            resource_name: OrderedDict()
        }
    template['Resources'][resource_name]['Type'] = 'AWS::IAM::Role'
    properties = OrderedDict()
    if role_name:
        properties['RoleName'] = role_name
    properties['Description'] = (
        'Federated IAM Role which the groups {} are permitted to '
        'assume'.format(', '.join(groups)))
    if (assume_role_policy_document['Statement'][0]['Principal']['Federated']
            is None):
        federated_principal = {
            'Fn::Join': [
                '',
                [
                    'arn:aws:iam::',
                    {
                        'Ref': 'AWS::AccountId'
                    },
                    ':oidc-provider/',
                    IDENTITY_PROVIDER_URL
                ]
            ]
        }
        assume_role_policy_document['Statement'][0]['Principal'][
            'Federated'] = federated_principal

    properties['AssumeRolePolicyDocument'] = assume_role_policy_document
    properties['Policies'] = [OrderedDict()]
    properties['Policies'][0]['PolicyName'] = policy_name
    properties['Policies'][0]['PolicyDocument'] = policy
    template['Resources'][resource_name]['Properties'] = properties

    # No description field because of
    # https://github.com/aws-cloudformation/aws-cloudformation-coverage-roadmap/issues/6

    return formatter(template)


def create_awscli_command(
        role_name, assume_role_policy_document, policy_name, policy):
    create_role = r"""aws iam create-role \
    --role-name {role_name} \
    --assume-role-policy-document '{assume_role_policy_document}' \
    --description "Federated Role {role_name}"

sleep 2

aws iam put-role-policy \
    --role-name {role_name} \
    --policy-name {policy_name} \
    --policy-document '{policy_document}'
"""
    return create_role.format(
        role_name=role_name,
        assume_role_policy_document=json.dumps(assume_role_policy_document),
        policy_name=policy_name,
        policy_document=json.dumps(policy)
    )


def create_policy_json(assume_role_policy_document, policy):
    output = '''Trust policy / Assume Role Policy Document

{assume_role_policy_document}

Policy Document

{policy_document}'''
    return output.format(
        assume_role_policy_document=get_json(assume_role_policy_document),
        policy_document=get_json(policy)
    )


def get_policy():
    format_input = sys.argv[1] if len(sys.argv) > 1 else None
    while format_input is None or format_input[0].lower() not in 'cjap':
        if format_input is None:
            print(FORMAT_PROMPT + "\n")
        format_input = input(
            'What format would you like the policy returned in?'
            ' (c/cloudformation / j/json-cloudformation / a/awscli / '
            'p/policy) ')
        if len(format_input) == 0:
            exit(0)
    format = format_input[0].lower()

    groups = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    while groups is None or len(groups) == 0:
        if groups is None:
            print(GROUPS_PROMPT)
        group_input = input(
            'What groups would you like to grant access to this role? ')
        groups = [
            x for x in group_input.split(',') if x != '']

    role_name = sys.argv[3] if len(sys.argv) > 3 else None
    while role_name is None or not is_role_name_allowed(role_name):
        if role_name:
            print(
                'Allowed characters are alphanumeric, including the following '
                'common characters: plus (+), equal (=), comma (,), period (.)'
                ', at (@), underscore (_), and hyphen (-).')
        role_name = input('What name would you like for the AWS IAM Role? ')

    account_id_input = sys.argv[4] if len(sys.argv) > 4 else None
    if format != 'c':
        while account_id_input is None or len(account_id_input) < 12:
            if account_id_input is None:
                print(ACCOUNT_ID_PROMPT + "\n")
            account_id_input = input(
                'What is the AWS Account ID of the account that this role will'
                'be deployed in? ')
            if len(account_id_input) == 0:
                exit(0)

    if len(sys.argv) < 4:
        print("\n\n")

    identity_provider = 'arn:aws:iam::{}:oidc-provider/{}'.format(
        account_id_input, IDENTITY_PROVIDER_URL) if format != 'c' else None
    audience_key = '{}:aud'.format(IDENTITY_PROVIDER_URL)
    amr_key = '{}:amr'.format(IDENTITY_PROVIDER_URL)
    verb = (
        'StringLike'
        if any('*' in x or '?' in x for x in groups)
        else 'StringEquals')

    assume_role_policy_document = OrderedDict()
    assume_role_policy_document['Version'] = '2012-10-17'
    assume_role_policy_document['Statement'] = [OrderedDict()]
    assume_role_policy_document['Statement'][0]['Principal'] = {
        'Federated': identity_provider
    }
    assume_role_policy_document['Statement'][0]['Action'] = (
        'sts:AssumeRoleWithWebIdentity')
    assume_role_policy_document['Statement'][0]['Effect'] = 'Allow'
    assume_role_policy_document['Statement'][0]['Condition'] = OrderedDict()
    assume_role_policy_document['Statement'][0][
        'Condition']['StringEquals'] = {audience_key: AUDIENCE_VALUE}
    assume_role_policy_document['Statement'][0][
        'Condition']['ForAnyValue:{}'.format(verb)] = {}

    policy_name = 'ExamplePolicyGrantingGetCallerIdentity'
    policy = OrderedDict()
    policy['Version'] = '2012-10-17'
    policy['Statement'] = [OrderedDict()]
    policy['Statement'][0]['Action'] = ['sts:GetCallerIdentity']
    policy['Statement'][0]['Resource'] = '*'
    policy['Statement'][0]['Effect'] = 'Allow'

    assume_role_policy_document['Statement'][0][
        'Condition']['ForAnyValue:{}'.format(verb)][amr_key] = groups

    if format == 'c':
        return create_cloudformation_template(
            role_name,
            assume_role_policy_document,
            policy_name,
            policy,
            groups,
            get_yaml)
    elif format == 'j':
        return create_cloudformation_template(
            role_name,
            assume_role_policy_document,
            policy_name,
            policy,
            groups,
            get_json)
    elif format == 'a':
        return create_awscli_command(
            role_name, assume_role_policy_document, policy_name, policy)
    elif format == 'p':
        return create_policy_json(assume_role_policy_document, policy)


def main():
    print(get_policy())


if __name__ == "__main__":
    main()
