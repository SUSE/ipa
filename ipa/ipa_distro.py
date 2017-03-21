# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import ipa_utils

from ipa_exceptions import IpaDistroException


class Distro(object):
    """Generic module for performing instance level tests."""
    def __init__(self):
        super(Distro, self).__init__()

    def get_reboot_cmd(self):
        """Return reboot command for given distribution."""
        return 'shutdown -r now'

    def get_stop_ssh_service_cmd(self):
        """Return command to stop SSH service on given distribution."""
        raise NotImplementedError('Implement method in child classes.')

    def get_sudo_cmd(self):
        """Return sudo command to wrap one more commands."""
        return 'sudo sh -c'

    def reboot(self, instance_ip, ssh_private_key, ssh_user, sudo=True):
        """Execute reboot command on instance."""
        reboot_cmd = '{};{}'.format(
            self.get_shutdown_ssh_service_cmd(),
            self.get_reboot_cmd()
        )
        if sudo:
            reboot_cmd = "{} '{}'".format(self.get_sudo_cmd(), reboot_cmd)

        print('Rebooting instance: %s\n' % reboot_cmd)
        out, err = ipa_utils.execute_ssh_command(reboot_cmd,
                                                 instance_ip,
                                                 ssh_private_key,
                                                 ssh_user)

        if err:
            raise IpaDistroException(
                'An error occurred rebooting instance: %s\n' % err
            )
