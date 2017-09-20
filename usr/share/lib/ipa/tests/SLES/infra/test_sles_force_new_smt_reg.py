import pytest

from distutils.version import StrictVersion


def test_sles_force_new_smt_reg(check_cloud_register,
                                get_release_value,
                                get_smt_servers,
                                host,
                                request):
    certs_dir = '/var/lib/regionService/certs/'
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    result = host.run('zypper if cloud-regionsrv-client | grep Version')
    version = result.stdout.split(':')[-1].strip().split('-')[0]

    if StrictVersion(version) < StrictVersion('7.0.6'):
        pytest.skip("Guest register client must be at least version 7.0.6.")

    host.run("sudo sh -c ': > /var/log/cloudregister'")
    result = host.run('cat /etc/regionserverclnt.cfg | grep regionsrv')
    region_srv = result.stdout.split('=')[-1].strip().split(',')[-1]

    result = host.run(
        'openssl x509 -noout -fingerprint -sha1 -inform pem -in %s'
        % ''.join([certs_dir, region_srv, '.pem'])
    )
    fingerprint = result.stdout.split('=')[-1]

    pretty_name = get_release_value('PRETTY_NAME')
    servers = get_smt_servers(pretty_name, provider, region)

    result = host.run(
        'sudo registercloudguest --force-new --smt-ip={ip} '
        '--smt-fqdn={fqdn} --smt-fp={fp}'.format(
            ip=servers[0]['ip'],
            fqdn=servers[0]['name'],
            fp=fingerprint
        )
    )

    assert result.rc == 0
    assert check_cloud_register()
