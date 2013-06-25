~~~~~~~~~
Templates
~~~~~~~~~

All templates are in /buddyup/templates.

=======
Backend
=======

Always use ``buddyup.templating.render_template()`` instead of 
``flask.render_template()``. Buddyup's ``render_template()`` does some extra
work.

.. code-block:: python

    from buddyup.templating import render_template

    @app.route('/')
    return render_template('index.html')


========
Frontend
========

Extra Variables and Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``buddyup.templates.render_template`` adds some extra helpers.

.. data:: user_record


    An instance of buddyup.database.User for the currently logged in user. 
    None if the user is not logged in or if the session is invalid.

    id
        Unique user identifier. (``int``)

    full_name
        Full name (``unicode``)

    groups
        Iterable of ``buddyup.database.Group`` instances. Use a for loop.

.. function:: url_for_user(user, **kwargs)

    Return a URL based on a specific user record or user id. Arguments are 
    otherwise identical to Flask's ``url_for()``. To get a full URL, use::
    
        url_for_user(user, external=True)
    
    ``user`` is either the integer id of the user or an instance of 
    ``buddyup.user.User``.
    
    For a basic setup in a template, use Jinja's filter feature:

    .. code-block:: jinja
        
        <a href="{{ user_record|url_for_user }}">
            {{ user_record.full_name }}
        </a>

    If necessary, add additional arguments:
    
    .. code-block:: jinja

        <a href="{{ user_record|url_for_user(external=True) }}">
            {{ user_record.full_name }}
        </a>

.. function:: url_for_group(group, **kwargs)

    Return a URL based on a specific group record or group id. Otherwise
    identical to ``url_for_user()``.

.. function:: url_for_event(event, **kwargs)

    Return a URL based on a specific event record or event id. Otherwise
    identical to ``url_for_user()``.

.. function:: url_for_course(event, **kwargs)

    Return a URL based on a specific course record or course id. Otherwise
    identical to ``url_for_user()``.

