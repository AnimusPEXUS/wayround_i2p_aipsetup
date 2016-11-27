#!/usr/bin/python3


def main():

    import sys

    del sys.path[0]

    import logging

    import wayround_i2p.utils.program

    wayround_i2p.utils.program.logging_setup(loglevel='INFO')

    import wayround_i2p.aipsetup.commands
    import wayround_i2p.aipsetup.config
    import wayround_i2p.aipsetup.build
    import wayround_i2p.aipsetup.dbconnections

    config = wayround_i2p.aipsetup.config.load_config('/etc/aipsetup.conf')

    package_info = None

    commands = wayround_i2p.aipsetup.commands.commands()

    ret = wayround_i2p.utils.program.program(
        'aipsetup3',
        commands,
        additional_data={
            'config': config
            }
        )

    try:
        import wayround_i2p.aipsetup.gtk
        wayround_i2p.aipsetup.gtk.stop_session()
    except:
        logging.error("Exception while stopping Gtk+ session")

    try:
        wayround_i2p.aipsetup.dbconnections.close_all()
    except:
        logging.exception("Exception while closing database connections")

    return ret

if __name__ == '__main__':
    exit(main())
