
Usage
#####

.. click:: telegram_upload.management:upload
   :prog: telegram-upload
   :show-nested:


.. click:: telegram_upload.management:download
   :prog: telegram-download
   :show-nested:

Interactive download
====================
Use the ``-i`` (or ``--interactive``) option to activate the **interactive mode** to choose the dialog (chat,
channel...) and the files to download::

    $ telegram-download -i

The following keys are available in this mode:

* **Up arrow**: previous option in the list.
* **Down arrow**: next option in the list.
* **Spacebar**: select the current option. The selected option is marked with an asterisk.
* **mouse click**: also to select the option. Some terminals may not support it.
* **Enter**: go to the next wizard step.
* **pageup**: go to the previous page of items. Allows quick navigation..
* **pagedown**: go to the next page of items. Allows quick navigation..

This wizard has two steps. The *first step* chooses the conversation::

    Select the dialog of the files to download:
    [SPACE] Select dialog [ENTER] Next step
    ( ) Groupchat 1
    ( ) Bob's chat
    ( ) A channel
    ( ) Me


The *second step* chooses the files to download. You can choose several files::

    Select all files to download:
    [SPACE] Select files [ENTER] Download selected files
    [ ] image myphoto3.jpg by My Username @username 2022-01-31 02:15:07+00:00
    [ ] image myphoto2.jpg by My Username @username 2022-01-31 02:15:05+00:00
    [ ] image myphoto1.png by My Username @username 2022-01-31 02:15:03+00:00


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
