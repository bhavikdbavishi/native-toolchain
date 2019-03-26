#!/usr/bin/env python
# Copyright 2019 Cloudera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Assert that a system has the correct libraries/binaries to build the
# native toolchain. Since we support centos5 which ships with python2.6,
# this script must be python2.6 .

import distutils.core  # noqa: F401
import distutils.spawn
import platform
import subprocess
import logging
import os
import re
import shutil

LOG = logging.getLogger('assert-dependencies')


def check_output(cmd):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ret = p.communicate()
  if p.poll():
    raise Exception('%s returned' % cmd, p.returncode)
  return ret


def regex_in_list(regex, l):
  cr = re.compile(regex)
  return any(map(cr.match, l))


def check_libraries():
  patterns = [r'libdb.*\.so',
              r'libffi.*\.so',
              r'libkrb.*\.so',
              r'libncurses\.so',
              r'libsasl.*\.so',
              r'libcrypto\.so',
              r'libz\.so']
  libraries = [line.split()[0] for line in check_output(["ldconfig", "-p"])[0].splitlines()]
  for pattern in patterns:
    LOG.info('Checking pattern: %s' % pattern)
    if not regex_in_list(pattern, libraries):
      raise Exception('Unable to find pattern: %s in `ldconfig -p`' % pattern)


def check_path():
  progs = ['aclocal',
           'autoconf',
           'automake',
           'aws',
           'bison',
           'ccache',
           'flex',
           'lsb_release',
           'libtool',
           'gcc',
           'git',
           'java',
           'make',
           ('mawk', 'gawk'),
           'mvn',
           'patch',
           'pigz',
           'python',
           'soelim',
           'unzip',
           'bzip2',
           'yacc']
  which = distutils.spawn.find_executable
  for p in progs:
    if isinstance(p, tuple):
      LOG.info('Checking for any program of: %s' % ', '.join(p))
      if not any(map(which, p)):
        raise Exception('Unable to find any of \'%s\' in PATH' % ', '.join(p))
      continue
    LOG.info('Checking program: %s' % p)
    if not which(p):
      raise Exception('Unable to find %s in PATH' % p)


def check_openssl_version():
  LOG.info('Checking openssl version')
  want = '1.0.1e'
  distro = platform.dist()[1]
  if distro == 'centos':
    out = check_output(['rpm', '-qa', 'openssl'])[0].rstrip()
    if want not in out:
      raise Exception('Unexpected openssl version. Was: %s, expected: %s' % (out, want))


def check_aws_works():
  # Due to the python/pip version discrepancies it's
  # worthwhile to verify that aws was correctly installed
  # and not just in our path
  LOG.info('Checking that aws is correctly isntalled.')
  check_output(['aws', '--version'])


def check_mvn_works():
  LOG.info('Checking that mvn is correctly installed.')
  check_output(['mvn', '--version'])


def git_clone_works_with_https():
  distro, version, _ = platform.dist()
  if distro == 'centos' and version.startswith('6'):
    # See: https://github.com/apache/kudu.git/info/refs
    LOG.info('Checking if git can clone from github.com')
    check_output(['git', 'clone', 'https://github.com/cloudera/kudu.git'])
    assert os.path.isdir('kudu')
    shutil.rmtree('kudu')


def main():
  logging.basicConfig(level=logging.INFO)
  check_libraries()
  git_clone_works_with_https()
  check_path()
  check_openssl_version()
  check_aws_works()
  check_mvn_works()


if __name__ == '__main__':
  main()
