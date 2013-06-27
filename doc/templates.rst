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

.. data:: login_url

    CAS login URL (``unicode``)

.. data:: logged_in

    Is the user logged in? A ``bool`` value.
    
    .. code-block:: jinja
    
        {% if logged_in %}
            You're Logged In!
        {% endif %}

.. data:: user_record


    An instance of buddyup.database.User for the currently logged in user. 
    None if the user is not logged in or if the session is invalid.

    id
        Unique user identifier. (``int``)

    full_name
        Full name (``unicode``)

    groups
        Iterable of ``buddyup.database.Group`` instances. Use a for loop.

.. function:: format_course(course, format)

    Render a ``buddyup.database.Course`` according to a format string in the syle::
    
        "{subject} {number}"
    
    Variables:
    * id
    * crn
    * subject
    * number
    * section
    
    Example:

    ..code-block:: jinja
    
        {{ course|format_course("{subject}{number} #{section}") }}

.. function format_event(event, format)

    Render a :class:`buddyup.database.Event` according to a format string. Pass in
    datef and/or timef to get formatted dates/times.

    ``datef`` and ``timef`` are in the style of Python's datetime.strftime. See:
    
    http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    
    Variables:
    * id
    * location
    * start_date (if datef is passed in)
    * end_date (if datef is passed in)
    * start_time (if timef is passed in)
    * end_time (if timef is passed in)
    
.. function format_user(user, format)

    Render a ``buddyup.database.User`` according to a format string.
    
    Variables:
    * id
    * user_name
    * full_name

.. function:: paragraph(string)

    Return a list of paragraphs. For example:
    
    .. code-block:: jinja
    
        {% for p in message.text|paragraphs %}
            <p>{{ p }}</p>
        {% endfor %}

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

.. function:: url_for_event(event, **kwargs)

    Return a URL based on a specific event record or event id. Otherwise
    identical to ``url_for_user()``.

.. function:: url_for_course(event, **kwargs)

    Return a URL based on a specific course record or course id. Otherwise
    identical to ``url_for_user()``.
