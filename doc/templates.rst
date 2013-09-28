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

    .. code-block:: jinja

        <a href="{{ login_url }}">Log In</a>

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

.. data:: is_admin

    Is the user an administrator? None if the user is not logged in

.. data:: user_name

    Full name of the user, or an empty string if the user is not logged in.n

.. function:: js(filename)

    Get the URL for a static JavaScript file. A js extension is added if it
    is not already present. The file will be looked up in aliases.ini to
    find an externally hosted or local minified file if available. The
    directory /static/js/ is used for 

.. function:: css(filename)

    Same as with :func:`js()`, but for CSS and the /static/css/
    directory.

.. function:: img(filename)

    Same as with :func:`js()`, but for images and the /static/img
    directory. No file extensions are added.

.. function:: format_course(course, format)

    Render a ``buddyup.database.Course`` according to a format string in the style:
    
    .. code-block:: python

        "{name} by {instr}"

    Variables:

    * id
    * name
    * instructor
    * instr (alias for instructor)
    
    Example:

    .. code-block:: jinja
    
        {{ course|format_course("{name} by {instr}") }}

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

.. function:: profile(record)

    Return a URL based on a specific SQLAlchemy record with a view page.
    Currently allows:
    
    * Group
    * User
    
    For a basic setup in a template, use Jinja's filter feature:

    .. code-block:: jinja
        
        <a href="{{ user_record|profile }}">
            {{ user_record.full_name }}
        </a>
