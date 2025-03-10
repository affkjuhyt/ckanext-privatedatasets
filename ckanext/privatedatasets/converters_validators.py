from __future__ import absolute_import

import re
import six

from itertools import count

from ckan.plugins import toolkit
from ckan.common import _

from ckanext.privatedatasets import constants, db


def private_datasets_metadata_checker(key, data, errors, context):
    dataset_id = data.get(('id',))
    private_val = data.get(('private',))

    # Avoid missing value
    # "if not private_val:" is not valid because private_val can be False
    if not isinstance(private_val, six.string_types) and not isinstance(private_val, bool):
        private_val = None

    # If the private field is not included in the data dict, we must check the current value
    if private_val is None and dataset_id:
        dataset_dict = toolkit.get_action('package_show')({'ignore_auth': True}, {'id': dataset_id})
        private_val = dataset_dict.get('private')

    private = private_val is True if isinstance(private_val, bool) else private_val == 'True'
    metadata_value = data[key]

    # If allowed users are included and the dataset is not private outside and organization, an error will be raised.
    if metadata_value and not private:
        errors[key].append(_('This field is only valid when you create a private dataset'))


def allowed_users_convert(key, data, errors, context):
    # By default, all the fileds are in the data dictionary even if they contains nothing. In this case,
    # the value is 'ckan.lib.navl.dictization_functions.Missing' and for this reason the type is checked

    # Get the allowed user list
    data.pop(('__junk',), None)
    if (constants.ALLOWED_USERS,) in data and isinstance(data[(constants.ALLOWED_USERS,)], list):
        allowed_users = data[(constants.ALLOWED_USERS,)]
    elif (constants.ALLOWED_USERS_STR,) in data and isinstance(data[(constants.ALLOWED_USERS_STR,)], six.string_types):
        allowed_users_str = data[(constants.ALLOWED_USERS_STR,)].strip()
        allowed_users = [allowed_user for allowed_user in allowed_users_str.split(',') if allowed_user.strip() != '']
    else:
        allowed_users = None

    if allowed_users is not None:
        current_index = max([int(k[1]) for k in data.keys() if len(k) == 2 and k[0] == key[0]] + [-1])

        if len(allowed_users) == 0:
            data[(constants.ALLOWED_USERS,)] = []
        else:
            for num, allowed_user in zip(count(current_index + 1), allowed_users):
                allowed_user = allowed_user.strip()
                data[(key[0], num, 'value')] = allowed_user


def get_allowed_users(key, data, errors, context):
    pkg_id = data[('id',)]

    db.init_db(context['model'])

    users = db.AllowedUser.get(package_id=pkg_id)

    for i, user in enumerate(users):
        data[(key[0], i, 'value')] = user.user_name


def url_checker(key, data, errors, context):
    url = data.get(key, None)

    if url:
        # DJango Regular Expression to check URLs
        regex = re.compile(
            r'^https?://'  # scheme is validated separately
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if regex.match(url) is None:
            errors[key].append(_('The URL "%s" is not valid.') % url)
