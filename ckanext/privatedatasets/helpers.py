from __future__ import absolute_import

import logging
import os

from ckan.common import request
import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.privatedatasets import db


log = logging.getLogger(__name__)


def is_dataset_acquired(pkg_dict):

    db.init_db(model)

    if tk.c.user:
        return len(db.AllowedUser.get(package_id=pkg_dict['id'], user_name=tk.c.user)) > 0
    else:
        return False


def is_owner(pkg_dict):
    if tk.c.userobj is not None:
        return tk.c.userobj.id == pkg_dict['creator_user_id']
    else:
        return False


def get_allowed_users_str(users):
    if users:
        return ','.join([user for user in users])
    else:
        return ''


def can_read(pkg_dict):
    try:
        context = {'user': tk.c.user, 'userobj': tk.c.userobj, 'model': model}
        return tk.check_access('package_show', context, pkg_dict)
    except tk.NotAuthorized:
        return False


def get_config_bool_value(config_name, default_value=False):
    env_name = config_name.upper().replace('.', '_')
    value = os.environ.get(env_name, tk.config.get(config_name, default_value))
    return value if type(value) == bool else value.strip().lower() in ('true', '1', 'on')


def show_acquire_url_on_create():
    return get_config_bool_value('ckan.privatedatasets.show_acquire_url_on_create')


def show_acquire_url_on_edit():
    return get_config_bool_value('ckan.privatedatasets.show_acquire_url_on_edit')


def acquire_button(package):
    '''
    Return a Get Access button for the given package id when the dataset has
    an acquisition URL.

    :param package: the the package to request access when the get access
        button is clicked
    :type package: Package

    :returns: a get access button as an HTML snippet
    :rtype: string

    '''

    if 'acquire_url' in package and request.path.startswith('/dataset')\
            and package['acquire_url'] != '':
        url_dest = package['acquire_url']
        data = {'url_dest': url_dest}
        return tk.render_snippet('snippets/acquire_button.html', data)
    else:
        return ''
