import collections
import sys

import typing

try:
    from os import scandir
except ImportError:
    from scandir import scandir


# https://pypi.org/project/asyncio_utils/

async def anext(iterator: typing.AsyncIterator[typing.Any], *args, **kwargs
                ) -> typing.Any:
    """Mimics the builtin ``next`` for an ``AsyncIterator``.

    :param iterator:  An ``AsyncIterator`` to get the next value from.
    :param default:  Can be supplied as second arg or as a kwarg.  If a value is
                     supplied in either of those positions then a
                     ``StopAsyncIteration`` will not be raised and the
                     ``default`` will be returned.

    :raises TypeError:  If the input is not a :class:`collections.AsyncIterator`


    Example::

        >>> async def main():
                myrange = await arange(1, 5)
                for n in range(1, 5):
                    print(n, n == await anext(myrange))
                try:
                    n = await anext(myrange)
                    print("This should not be shown")
                except StopAsyncIteration:
                    print('Sorry no more values!')

        >>> loop.run_until_complete(main())
        1 True
        2 True
        3 True
        4 True
        Sorry no more values!


    """
    if not isinstance(iterator, collections.AsyncIterator):
        raise TypeError(f'Not an AsyncIterator: {iterator}')

    use_default = False
    default = None

    if len(args) > 0:
        default = args[0]
        use_default = True
    else:
        if 'default' in kwargs:
            default = kwargs['default']
            use_default = True

    try:
        return await iterator.__anext__()
    except StopAsyncIteration:
        if use_default:
            return default
        raise StopAsyncIteration
