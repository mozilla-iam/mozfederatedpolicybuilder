# mozfederatedpolicybuilder

[![PyPI version](https://badge.fury.io/py/mozfederatedpolicybuilder.svg)](https://badge.fury.io/py/mozfederatedpolicybuilder) [![test workflow](https://github.com/mozilla-iam/mozfederatedpolicybuilder/actions/workflows/test.yml/badge.svg)](https://github.com/mozilla-iam/mozfederatedpolicybuilder/actions/workflows/test.yml)


The Mozilla federated policy builder helps craft AWS IAM Roles that permit users
to assume those roles using a federated identity.

## Installation

```
pip install mozfederatedpolicybuilder
```

## Usage

```
mozfederatedpolicybuilder
```

You'll be prompted to choose what type of output you want

```
Policy format options :
* c/cloudformation : A YAML CloudFormation template which provisions a
    federated IAM role
* j/json-cloudformation : A JSON CloudFormation template which provisions a
    federated IAM role
* a/awscli : An AWS CLI command line command which creates a federated IAM role
* p/policy : The JSON trust relationship portion of the IAM policy (this can be
    copy pasted into the web console)

What format would you like the policy returned in? (c/cloudformation / a/awscli / j/json)
```

Select an output type. You'll be prompted for the groups you want to grant access

```
User groups can be granted access to the federated IAM role.
* Supported : Allow users in the group foo to assume the IAM role : "foo"
* Supported : Allow users in the group foo as well as users in the group bar to
    assume the IAM role : "foo,bar"
* Supported : Allow users in any group that begins with "foo_" : "foo_*"
What groups would you like to grant access to this role?
```

You'll next be prompted for the name of the AWS IAM Role

```
What name would you like for the AWS IAM Role?
```

Finally the tool will return the policy details in the format you've requested
