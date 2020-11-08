
Usage
#####

.. click:: telegram_upload.management:upload
   :prog: telegram-upload
   :show-nested:


.. click:: telegram_upload.management:download
   :prog: telegram-download
   :show-nested:


Proxies
=======
You can use **mtproto proxies** without additional dependencies or **socks4**, **socks5** or **http** proxies
installing ``pysocks``. To install it::

    $ pip install pysocks

To define the proxy you can use the ``--proxy`` parameter::

    $ telegram-upload image.jpg --proxy mtproxy://secret@proxy.my.site:443

Or you can define one of these variables: ``TELEGRAM_UPLOAD_PROXY``, ``HTTPS_PROXY`` or ``HTTP_PROXY``. To define the
environment variable from terminal::

    $ export HTTPS_PROXY=socks5://user:pass@proxy.my.site:1080
    $ telegram-upload image.jpg


Parameter ``--proxy`` has higher priority over environment variables. The environment variable
``TELEGRAM_UPLOAD_PROXY`` takes precedence over ``HTTPS_PROXY`` and it takes precedence over ``HTTP_PROXY``. To disable
the OS proxy::

    $ export TELEGRAM_UPLOAD_PROXY=
    $ telegram-upload image.jpg

The syntax for **mproto proxy** is::

    mtproxy://<secret>@<address>:<port>

For example::

    mtproxy://secret@proxy.my.site:443

The syntax for **socks4**, **socks5** and **http** proxy is::

    <protocol>://[<username>:<password>@]<address>:<port>

An example without credentials::

    http://1.2.3.4:80

An example with credentials::

    socks4://user:pass@proxy.my.site:1080
