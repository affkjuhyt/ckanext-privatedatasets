from __future__ import absolute_import

import sqlalchemy as sa

AllowedUser = None


def init_db(model):

    global AllowedUser
    if AllowedUser is None:

        class _AllowedUser(model.DomainObject):

            @classmethod
            def get(cls, **kw):
                '''Finds all the instances required.'''
                query = model.Session.query(cls).autoflush(False)
                return query.filter_by(**kw).all()

        AllowedUser = _AllowedUser

        # FIXME: Maybe a default value should not be included...
        package_allowed_users_table = sa.Table(
            'package_allowed_users',
            model.meta.metadata,
            sa.Column('package_id', sa.types.UnicodeText, primary_key=True, default=u''),
            sa.Column('user_name', sa.types.UnicodeText, primary_key=True, default=u''),
        )

        # Create the table only if it does not exist
        package_allowed_users_table.create(checkfirst=True)

        model.meta.mapper(AllowedUser, package_allowed_users_table,)
