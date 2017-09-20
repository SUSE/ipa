import shlex


def test_sles_switch_smt(get_smt_server_name,
                         get_smt_servers,
                         get_release_value,
                         host,
                         request):
    """
    This is a helper function for SMT failover test.

    It is cast as a test to be easily included in test suite.
    """
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    result = host.run(
        'cat /etc/hosts | grep %s' % get_smt_server_name(provider)
    )
    smt_ip = shlex.split(result.stdout)[0]

    pretty_name = get_release_value('PRETTY_NAME')
    servers = get_smt_servers(pretty_name, provider, region)

    for server in servers:
        if server['ip'] != smt_ip:
            result = host.run(
                "sudo sed -i 's/{current}/{new}/' /etc/hosts".format(
                    current=smt_ip,
                    new=server['ip']
                )
            )
            assert result.rc == 0
            break
