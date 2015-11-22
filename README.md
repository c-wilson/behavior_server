#To Run

To run this using apache, install mod_wsgi. This is a web-server-gateway-interface that can be used by django to
dynamically serve your pages via the Apache server.

To make the server configuration, run the following:

```
/path/to/manage.py$ python manage.py collectstatic
/path/to/manage.py$ python manage.py runmodwsgi --reload-on-changes --setup-only --server-root=/another/path
```

The first command above migrates your static paths (ie stylesheets) into a directory that apache can find. Whenever
you change these static files, you must re-run this command.

The second command creates a server configuration in the path that you specify. This configuration will run an apache
process on a port (default is 8000) that is connected to a Python instance through mod_wsgi.

Now navigate to your server configuration path ("another/path" in the example above). Run:

```
/another/path$ ./apachectl start
```
