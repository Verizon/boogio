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

'''Utility functions for creating real-looking fake test credentials.'''

import random

AWS_SECRET_KEY_LENGTH = 40
AWS_SECRET_KEY_CHARS = (
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    '/+'
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def fake_aws_secret_key(prefix='Abc1Fak3'):
    '''
    Create a fake AWS secret key with the indicated prefix.
    '''
    assert len(prefix) <= AWS_SECRET_KEY_LENGTH
    fake = list(prefix) + ['.'] * (AWS_SECRET_KEY_LENGTH - len(prefix))
    for posn in range(len(prefix), AWS_SECRET_KEY_LENGTH):
        fake[posn] = AWS_SECRET_KEY_CHARS[
            random.randint(0, len(AWS_SECRET_KEY_CHARS) - 1)
            ]
    return ''.join(fake)
