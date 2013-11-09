#!/usr/bin/env python
from nereid import Nereid
from werkzeug.contrib.sessions import FilesystemSessionStore
from nereid.sessions import Session

CONFIG = dict(

    # The name of database
    DATABASE_NAME='tutorial',

    # Static file root. The root location of the static files. The static/ will
    # point to this location. It is recommended to use the web server to serve
    # static content
    STATIC_FILEROOT='static/',

    # Tryton Config file path
    TRYTON_CONFIG='../etc/trytond.conf',

    # If the application is to be configured in the debug mode
    DEBUG=False,

    # Load the template from FileSystem in the path below instead of the
    # default Tryton loader where templates are loaded from Database
    TEMPLATE_LOADER_CLASS='nereid.templating.FileSystemLoader',
    TEMPLATE_SEARCH_PATH='.',
)


# Create a new application
app = Nereid()

# Update the configuration with the above config values
app.config.update(CONFIG)

# Initialise the app, connect to cache and backend
app.initialise()

# Setup the filesystem cache
app.session_interface.session_store = FilesystemSessionStore(
    '/tmp', session_class=Session
)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0')
