# ----------------------------------------------------------------------------
# Copyright (C) 2017 Verizon.  All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ----------------------------------------------------------------------------

'''Process and dispatch message content.

A Handler is responsible for processing a specific message type and
determining the disposition of the message content. Because different
message types, coming from different origins, will have their own
encodings, format, syntax and semantics each handler must understand
how to process the messages for which it's responsible and how to
determine the appropriate destination(s).

A typical handler configuration::

    {
        'name': 'handler_name',
        'dispatch': [
            {
                'handler-dispatch-name': 'this_rule_name???',
                'matches-any': [
                    {'key1': 'valueA', 'key2': {'regex': r'regexA'}},
                    {'key1': {'regex': r'regexB'}},
                    ],
                'matches-all': [
                    {'key1': 'valueB', 'key2': {'regex': r'regexC'}},
                    {'key2': {'regex': r'regexC'}},
                    ],
                'dispatch-to': [
                    'dispatcher1_name',
                    'dispatcher2_name',
                    ]
                },
            ],
        }

    The ``name`` field can be any string, preferably one descriptive
    of the type of data the handler should handle.

    The ``dispatch`` structure defines how individual messages will be
    handled. For each element in the list, a message whose keys and
    values satisfy the ``matches-*`` rules will be passed to the
    dispatchers listed in the ``dispatch-to`` list::

        *   A message satisfies a ``matches-*`` rule if, for every
            key in the rule, that key is present in the message and
            the message value for the key is equal to or satisfies
            the regex that is the rule's value for that key.
        *   If the ``matches-all`` key is present, a message
            satisfies its rules if it satisfies every rule in the
            list.
        *   If the ``matches-any`` key is present, a message
            satisfies its rules if it satisfies at least one rule in
            the list.

    Example::

        msg = {
            'model': 'Ford Prefect'
            'color': 'purple',
            }

'''


NOTES = '''
This probably shouldn't be called "sqs_handler", as it's more general.

SQSMessage = {<...sqs_message_headers...>, 'Body': sqs_message_body_json}

if message came from SNS,
sqs_message_body = {
    <...sns_message_headers...>,
    'Message': notification_body_json
    }

notification_body_json will depend on the originating entity.

* Where does scree get deleted?


Elasticsearch record:
{
    '@timestamp': <...>,
    'original_message': <...>,
    'basis'(causation? basis-type?): 'event|state',
    'incident-info': {
        source-reports: [...links...],
        }
    'alert-info': {
        'level': <...>,
        'status': 'new|triaged|assigned|resolved',
        'associated-cases': ...
        }


    }


SIEM Front Ends?
- MozDef: The Mozilla Defense Platform
- Netflix FIDO (Fully Integrated Defense Operation),



Sifter:
  - Load JSON of message body
  - Identify corrent handler based on presence, values of keys.
    E.g., TopicArn, if present, and value.
    Handlers and the rules for identifying them are loaded from config files.
  - Pass message to handler.
  - Optionally, delete anything with no handler as scree.
        "unhandled_message_treatment": None, Delete, DefaultHandler?

Handler:
  - Understands what to look for in specific types of message.
  - Adds wrapper "framework" if not present.
  - Adds 'handled by' value (list?)
  - Selects Dispatcher for message.
  - Responsible for deleting scree?

Dispatcher:
  - Applies Wrapper and Annotators to message.
  - Adds 'dispatched by' value (list?)
  - Routes messages to final destination.

Annotator:
  - Pulls fields from original message, adds additional fields.
  - Adds 'annotated by' value (list?)

Wrapper:
  - Adds fields, does additional calculations, etc, as necessary.

Configuration:
- Sifter configuration: A list of:
    {
        'matches[any|all]': [
            {
                '<KEY>': '<VALUE>',
                '<KEY>': {'regex': '<REGEX>'}
                },
                ...
            ],
        'handlers': [
            'handler_name',
            ...
            ]
        }

    load_handlers_from_file
    load_handlers_from_package
    load_handlers_from_bucket

- Handler configuration: A list of:
    {
        'matches[any|all]': [
            { ...see sifter... }, ...
            ],
        'dispatchers': [
            'dispatcher_name',
            ...
            ]
        }

- Dispatcher configuration:
    {
        'matches[any|all]': [
            { ...see sifter... }, ...
            ],
        'wrappers': [
            'wrapper_name',
            ...
            ],
        'annotators': [
            'annotator_name',
            ...
            ],
        }

 - Wrapper configuration:
    {
    (Hmm, these probably don't get dynamically configured.)
        }

 - Annotator configuration:
    {
        add fields, e.g. alert type, alert status, etc.
        pull fields from inside so the JSON doesn't have to be unpacked.
        }

'''
