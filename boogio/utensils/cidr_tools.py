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

'''Manipulate and compare CIDR blocks and addresses.'''

IP_ADDRESS_NETWORK_BITS = 32

UNIVERSAL_CIDR = '0.0.0.0/0'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def sort_cidrs(cidr_a, cidr_b):
    '''Sort cidrs and IPs numerically.'''
    blocks_a, mask_a = cidr_a.split('/') if '/' in cidr_a else (cidr_a, 32)
    blocks_b, mask_b = cidr_b.split('/') if '/' in cidr_b else (cidr_b, 32)

    blocks_a = blocks_a.split('.')
    blocks_b = blocks_b.split('.')

    mask_a = mask_a or '32'
    mask_b = mask_b or '32'

    assert len(blocks_a) == len(blocks_b)
    assert len(blocks_a) == 4

    # Sort by largest blocks to smallest.
    for block_num in range(4):
        diff = int(blocks_a[block_num]) - int(blocks_b[block_num])
        if diff != 0:
            return diff

    # The cidr portions are the same, sort the smaller mask first.
    return int(mask_a) - int(mask_b)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def to_cidr(address_or_cidr):
    '''Return a CIDR block representation of an IP address or CIDR block.

    Arguments:

        address_or_cidr (str):
            The IP address or CIDR block.

    Returns:

        (str) If ``address_or_cidr`` is an IP address, its value as a
        /32 CIDR block; otherwise, ``address_or_cidr``.

    '''
    if '/' not in address_or_cidr:
        return '/'.join(
            [address_or_cidr, str(IP_ADDRESS_NETWORK_BITS)]
            )

    else:
        return address_or_cidr


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def cidr_address(cidr):
    '''Extract the address portion of a CIDR block.

    Arguments:

        cidr (str):
            The CIDR block to split.

    Returns:

        (str) The IP address portion of the CIDR block.


    Example::

        >>> cidr_address('10.23.0.0/16)
        10.23.0.0

    '''
    return cidr.split('/')[0]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def cidr_netmask_size(cidr):
    '''Extract the netmask size portion of a CIDR block.

    Arguments:

        cidr (str):
            The CIDR block to split.

    Returns:

        (int) The netmask portion of the CIDR block.


    Example::

        >>> cidr_netmask_size('10.23.0.0/16)
        16

    '''
    if '/' not in cidr:
        return IP_ADDRESS_NETWORK_BITS
    return int(cidr.split('/')[1])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def bitmask_octet(bit_count):
    '''Return the numeric value (0-255) of a bitmask for k bits, 0 <= k <=8.

    Arguments:

        bit_count (int):
            The number of high order bits to set to 1 in the bitmask.

    Returns:

        (int) The numeric value of the bitmask. If ``bit_count`` is
        less than or equal to 0, the value 0 will be returned.
        Otherwise, the bitmask will be the sum 128 + 64 + 32 + ... of
        ``bit_count`` decreasing powers of 2. If ``bit_count`` is
        greater than 8 it will be treated as 8.

    Examples::

        >>> bitmask_octet(8)
        255
        >>> bitmask_octet(2)
        192
        >>> bitmask_octet(1)
        128
        >>> bitmask_octet(0)
        0

    '''
    if bit_count <= 0:
        return 0
    if bit_count > 8:
        bit_count = 8
    return reduce(
        lambda x, y: x | y,
        [1 << (8 - bn) for bn in range(1, bit_count + 1)]
        )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def netmask_octets(netmask_size):
    '''Return the bit mask for netmask_size network bits, as a 4-tuple.

    Arguments:

        netmask_size (int):
            The number of bits in the netmask.

    Returns:

        (tuple) The bit mask as a tuple of four integers in the range
        0 to 255.

    Examples::

        >>> netmask_octets(16)
        (255, 255, 0, 0)
        >>> netmask_octets(32)
        (255, 255, 255, 255)
        >>> netmask_octets(11)
        (255, 224, 0, 0)

    '''
    mask_blocks = [min(max(netmask_size - ii * 8, 0), 8) for ii in range(4)]
    mask_blocks = tuple(
        bitmask_octet(bit_count)
        for bit_count in mask_blocks
        )
    return mask_blocks


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def cidr_netmask_octets(cidr):
    '''Return the netmask for the network bits of cidr, as a 4-tuple.

    Arguments:

        cidr (str):
            The CIDR block for which to return the netmask octets.

    Returns:

        (tuple) The netmask octets for the CIDR block, as a tuple of
        four integers in the range 0 to 255.

    Examples::

        >>> cidr_netmask_octets('10.23.0.0/16')
        (255, 255, 0, 0)
        >>> cidr_netmask_octets('10.23.0.0/32')
        (255, 255, 255, 255)
        >>> cidr_netmask_octets('10.23.0.0/22')
        (255, 255, 252, 0)

    '''
    netmask_size = cidr_netmask_size(to_cidr(cidr))
    return netmask_octets(netmask_size)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def masked_address_octets(address, mask_blocks):
    '''Return the network octets of address given a network mask tuple.

    Arguments:

        address (str):
            The address for which to return the network octets tuple.

        mask_blocks (tuple):
            The four-tuple of network mask octets.

    Returns:

        (tuple) The octets of the subnet portion of ``address`` given
        a network mask represented by ``mask_blocks``.

    Examples::

        >>> masked_address_octets(
                '10.23.71.93', cidr_netmask_octets('10.23.0.0/16')
                )
        [10, 23, 0, 0]
        >>> masked_address_octets(
                '10.23.71.93', cidr_netmask_octets('10.23.0.0/20')
                )
        [10, 23, 64, 0]
        >>> masked_address_octets(
                '10.23.71.93', cidr_netmask_octets('10.23.0.0/28')
                )
        [10, 23, 71, 80]

    '''
    address_blocks = [int(i) for i in address.split('.')]
    address_blocks = [address_blocks[n] & mask_blocks[n] for n in range(4)]
    return address_blocks


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def masked_address(address, mask_blocks):
    '''Return the network address of address given a network mask tuple.

    Arguments:

        address (str):
            The address for which to return the network octets tuple.

        mask_blocks (tuple):
            The four-tuple of network mask octets.

    Returns:

        (string) The subnet portion of ``address`` given a network
        mask represented by ``mask_blocks``.

    Examples::

        >>> masked_address('10.23.71.93', cidr_netmask_octets('10.23.0.0/16'))
        '10.23.0.0'
        >>> masked_address('10.23.71.93', cidr_netmask_octets('10.23.0.0/20'))
        '10.23.64.0'
        >>> masked_address('10.23.71.93', cidr_netmask_octets('10.23.0.0/24'))
        '10.23.71.0'

    '''
    return '.'.join([
        str(b) for b in masked_address_octets(address, mask_blocks)
        ])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_subcidr(cidr1, cidr2):
    '''Determine if CIDR block cidr1 lies inside CIDR block cidr2.

    Arguments:

        cidr1, cidr2 (str):
            The CIDR blocks to compare.

    Returns:

        (bool) ``True`` if ``cidr1`` is a subcidr of ``cidr2``, that
        is, every address that falls within ``cidr1`` also falls
        within ``cidr2``. ``False`` otherwise.

    Examples::

        >>> is_subcidr('128.56.0.0/16', '128.0.0.0/8')
        True
        >>> is_subcidr('128.56.0.0/16', '0.0.0.0/0')
        True
        >>> is_subcidr('128.56.0.0/16', '128.56.1.0/16')
        True
        >>> is_subcidr('128.56.0.0/16', '128.78.0.0/16')
        False


    '''
    # The subcidr has to have a more specific subnet, i.e. a longer
    # subnet mask.
    if cidr_netmask_size(cidr1) < cidr_netmask_size(cidr2):
        return False

    masked_1 = masked_address(
        cidr_address(to_cidr(cidr1)), cidr_netmask_octets(to_cidr(cidr2))
        )
    masked_2 = masked_address(
        cidr_address(to_cidr(cidr2)), cidr_netmask_octets(to_cidr(cidr2))
        )
    return masked_1 == masked_2


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_universal_cidr(value):
    '''Is value the universal CIDR?
    '''
    return True if value == UNIVERSAL_CIDR else False


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_valid_address(value):
    '''Is value in the format of a valid IP address?
    '''

    if not (isinstance(value, str) or isinstance(value, unicode)):
        return False

    import re
    address_re = r'''(?x)
        ^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
        $
        '''

    return re.match(address_re, value) is not None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_valid_cidr(value):
    '''Is value in the format of a valid CIDR block with netmask?
    '''

    if not (isinstance(value, str) or isinstance(value, unicode)):
        return False

    import re
    cidr_re = r'''(?x)
        ^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
            \/(?:[0-2]?[0-9]|3[0-2])
        $
        '''

    return re.match(cidr_re, value) is not None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_valid_address_or_cidr(value):
    '''Is value in the format of a valid IP address or CIDR block with netmask?
    '''
    return is_valid_address(value) or is_valid_cidr(value)

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class Cidr(object):
#     '''Manipulate and compare CIDR blocks and addresses.
#     '''
