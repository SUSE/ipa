import json
import pytest

from susepubliccloudinfoclient import infoserverrequests


def pytest_addoption(parser):
    parser.addoption('--provider', action='store', help='ipa provider')
    parser.addoption('--region', action='store', help='ipa region')


@pytest.fixture()
def check_cloud_register(host):
    def f():
        client_log = host.file('/var/log/cloudregister')
        return all([
            client_log.contains('ERROR') is False,
            client_log.contains('failed') is False
        ])
    return f


@pytest.fixture()
def check_service(host):
    def f(service_name, running=True, enabled=True):
        service = host.service(service_name)
        return all([
            service.is_running == running,
            service.is_enabled == enabled
        ])
    return f


@pytest.fixture()
def check_zypper_repo(host):
    def f(repo):
        repo = host.file('/etc/zypp/repos.d/' + repo + '.repo')
        return repo.exists
    return f


@pytest.fixture()
def get_release_value(host):
    def f(key):
        release = host.file('/etc/os-release')

        if not release.exists:
            release = host.file('/etc/SUSE-release')

        pretty_name = None
        key += '='

        for line in release.content_string.split('\n'):
            if line.startswith(key):
                pretty_name = line[len(key):].replace('"', '')\
                        .replace("'", '').strip()
                break

        return pretty_name
    return f


@pytest.fixture()
def get_smt_server_name(host):
    def f(provider):
        return 'smt-{}.susecloud.net'.format(provider)
    return f


@pytest.fixture()
def get_smt_servers(get_release_value, host):
    def f(provider, region):
        cpe_name = get_release_value('CPE_NAME')
        if 'sap' in cpe_name:
            smt_type = 'smt-sap'
        else:
            smt_type = 'smt-sles'

        if provider == 'azure':
            provider = 'microsoft'
        elif provider == 'ec2':
            provider = 'amazon'
        elif provider == 'gce':
            provider = 'google'
        else:
            raise Exception('Provider %s unknown' % provider)

        output = json.loads(
            infoserverrequests.get_server_data(
                provider,
                'smt',
                'json',
                region,
                'type~{smt_type}'.format(smt_type=smt_type)
            )
        )

        return output['servers']
    return f


@pytest.fixture()
def install_zypper_package(host):
    def f(name):
        result = host.run('sudo zypper -n in %s' % name)
        return result.rc
    return f
