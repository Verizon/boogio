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

'''Use a cidr_catalog.CidrCatalog instance to add information to informers.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class CidrCatalogHelper(object):
    '''Add information based on a CidrCatalog to AWSInformer instances.

    If the class has public attributes, they should be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section.

    Attributes:
        catalog (cidr_catalog.CidrCatalog):
            The CidrCatalog instance.

    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, catalog):
        '''Initialize a CidrCatalogHelper instance.'''

        self.catalog = catalog

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def annotate_group_cidrip(self, informer, *attrs):
        '''Add the listed attributes as key-value pairs in IpRanges.

        Arguments:

            informer (SecurityGroupInformer):
                A ``SecurityGroupInformer`` instance.

            *attrs (tuple of str):
                A list of ``CidrCatalogEntry`` attributes from the
                ``CidrCatalog.entry_reference_methods`` list.
        '''
        all_ip_permissions = [
            x for x in [
                informer.resource.get('IpPermissions'),
                informer.resource.get('IpPermissionsEgress'),
                ]
            if x is not None
            ]

        if not all_ip_permissions:
            return

        for ip_perm in reduce(lambda x, y: x + y, all_ip_permissions):
            ip_ranges = ip_perm.get('IpRanges')
            if not ip_ranges:
                continue
            for ip_range in ip_ranges:
                cidr_ip = ip_range.get('CidrIp')
                for attr in attrs:
                    ip_range.update(
                        {attr: self.catalog.covering_attr(attr, cidr_ip)}
                        )
