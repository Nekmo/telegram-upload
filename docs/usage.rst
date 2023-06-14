
Usage
#####

.. click:: telegram_upload.management:upload
   :prog: telegram-upload
   :show-nested:


.. click:: telegram_upload.management:download
   :prog: telegram-download
   :show-nested:

Interactive mode
================
Use the ``-i`` (or ``--interactive``) option to activate the **interactive mode** to choose the dialog (chat,
channel...) and the files. To **upload files** using interactive mode:

    $ telegram-upload -i

To **download files** using interactive mode:

    $ telegram-download -i

The following keys are available in this mode:

* **Up arrow**: previous option in the list.
* **Down arrow**: next option in the list.
* **Spacebar**: select the current option. The selected option is marked with an asterisk.
* **mouse click**: also to select the option. Some terminals may not support it.
* **Enter**: go to the next wizard step.
* **pageup**: go to the previous page of items. Allows quick navigation..
* **pagedown**: go to the next page of items. Allows quick navigation..

Interactive upload
------------------
This wizard has two steps. The *first step* chooses the files to upload. You can choose several files::

    Select the local files to upload:
    [SPACE] Select file [ENTER] Next step
    [ ] myphoto1.jpg
    [ ] myphoto2.jpg
    [ ] myphoto3.jpg

The *second step* chooses the conversation::

    Select the dialog of the files to download:
    [SPACE] Select dialog [ENTER] Next step
    ( ) Groupchat 1
    ( ) Bob's chat
    ( ) A channel
    ( ) Me


Interactive download
--------------------
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

Split files
===========
By default, when trying to **upload** a file larger than the supported size by Telegram, an error will occur. However,
*Telegram-upload* has different policies for large files using the ``--large-files`` parameter:

* ``fail`` (default): The execution of telegram-upload is stopped and the uploads are not continued.
* ``split``: The files are split as parts. For example *myfile.tar.00*, *myfile.tar.01*...

The syntax is:

.. code-block::

    ~$ telegram-upload --large-files <fail|split>

To join the split files using the *split* option, you can use in GNU/Linux:

.. code-block:: bash

    ~ $ cat myfile.tar.* > myfile.tar

In windows there are different programs like `7z <https://7-zip.org/>`_ or `GSplit <https://www.gdgsoft.com/gsplit>`_.

*Telegram-upload* when downloading split files by default will download the files without joining them. However, the
**download** policy can be changed using the ``--split-files`` parameter:

* ``keep`` (default): Files are downloaded without joining.
* ``join``: Downloaded files are merged after downloading. In case of errors, such as missing files, the keep policy
  is used.

The syntax is:

.. code-block::

    ~$ telegram-download --split-files <keep|join>
