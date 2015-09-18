
import wayround_org.utils.system_type


def process_h_and_a_opts_wide(opts, config):
    """
    By default matches as many packages as possible

    default returned values are None, None which is
    equivalent to -h=all -a=all options
    """

    host = None
    arch = None

    if '-h' in opts:

        host = opts['-h']

        if host.lower() == 'all':
            host = None

    if host is not None:

        if '-a' in opts:

            arch = opts['-a']

            if arch.lower() == 'all':
                arch = None

    else:

        if '-a' in opts:
            host = config['system_settings']['host']
            arch = opts['-a']

    return host, arch


def process_h_and_a_opts_specific(opts, config):
    """
    By default matches current host and arch

    returned values are cpu-vendor-os triplets
    'all' values can be used to widen result
    """

    host = config['system_settings']['host']
    if '-h' in opts:

        host = opts['-h']

        if host.lower() == 'all':
            host = None

    arch = host

    if host is not None:

        if '-a' in opts:

            arch = opts['-a']

            if arch.lower() == 'all':
                arch = None

    return host, arch


def process_h_and_a_opts_strict(opts, config):
    """
    requires strict values for -h and -a (which defaults to current system)

    'all' values not allowed
    """

    host = None
    arch = None

    if '-h' in opts:
        host = opts['-h']

    else:
        host = config['system_settings']['host']

    if '-a' in opts:
        arch = opts['-a']

    else:
        arch = host

    if wayround_org.utils.system_type.parse_triplet(host) is None:
        raise ValueError("Invalid host triplet")

    if wayround_org.utils.system_type.parse_triplet(arch) is None:
        raise ValueError("Invalid arch triplet")

    return host, arch
