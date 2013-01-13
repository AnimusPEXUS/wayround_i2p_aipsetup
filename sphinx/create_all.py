
import os
import os.path

dir = os.path.dirname(__file__)

lst = os.listdir(os.path.join(dir, '..', 'org', 'wayround', 'aipsetup'))

lst.sort()

for i in lst:

    if i.endswith('.py'):

        mod_name = i[:-3]

        fn = os.path.join(dir, mod_name + '.rst')

        f = open(fn, 'w')

        title = ":mod:`{mod_name}` Module".format(mod_name=mod_name)
        underline = '-' * len(title)

        f.write(
            """\
.. This document is automatically generated with create_all.py script

{title}
{underline}

.. automodule:: org.wayround.aipsetup.{mod_name}
    :members:
    :undoc-members:
    :show-inheritance:
""".format(
                mod_name=mod_name,
                title=title,
                underline=underline
                )
            )

        f.close()

        print("generated {}".format(mod_name))

exit(0)
