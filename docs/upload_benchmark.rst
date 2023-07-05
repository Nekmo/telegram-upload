Upload benchmarks
=================
The following results are a study about the performance of Telegram-upload uploading files. The results are not
intended to be exhaustive and are subject to errors for multiple reasons. Some of them are:

* The Telegram status *(e.g. the server load)* at the time of the test.
* The network status at the time of the test *(the contracted bandwidth is 600 Mibps)*.
* The hardware used for the test *(in my case a PC with an Intel i7-3770K CPU @ 3.50GHz and 20 GiB of RAM)*.
* The machine load at the time of the test.

The tests were performed using different file sizes. The file sizes were 512 KiB, 20 MiB, 200 MiB and 2 GiB. The chunk
size was the default in Telegram-upload. The chunk size vary depending on the file size:

* *128 KiB* for files smaller than *100 MiB*.
* *256 KiB* for files smaller than *750 MiB*.
* *512 KiB* for files bigger than *750 MiB*.

The tests were performed using different number of parallel chunks uploaded at the same time. By default
Telegram-upload uploads *4 chunks at the same time*. You can change this value using the ``PARALLEL_UPLOAD_BLOCKS``
environment variable. For example::

    $ PARALLEL_UPLOAD_BLOCKS=2 telegram-upload video.mkv

Or exporting the variable::

    $ export PARALLEL_UPLOAD_BLOCKS=2
    $ telegram-upload video.mkv

Note that increasing the number of parallel chunks uploaded at the same time will increase the CPU usage and can
increase the number of 429 errors. These errors are caused by Telegram after exceeding the server's resource limits.

These tests can help you to choose the best number of parallel chunks uploaded at the same time for your use case. All
the tests were performed using 1, 2, 3, 4, 5, 6, 7, 8, 9 and 10 parallel chunks uploaded at the same time.

You can run the tests yourself using the ``upload_benchmark.py`` script in the ``docs`` directory. This script will
upload a file to Telegram using your account and will measure the time it takes to upload the file. To run the script::

    $ python3 ./upload_benchmark.py benchmark

This script will create a ``upload_benchmark.json`` file in the ``docs`` directory with the results. You can use the
``upload_benchmark.py`` script to plot the results using the ``graphs`` command::

    $ python3 ./upload_benchmark.py graphs

The above command will create the images in the same directory. For create the rst tables you can use the ``rst``
command::

    $ python3 ./upload_benchmark.py rst

The following results were obtained using the ``upload_benchmark.py`` script.
