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
import subprocess
import logging
import re

LOG = logging.getLogger('assert-dependencies')


def check_output(cmd):
  p = subprocess.Popen(['ldconfig', '-p'], stdout=subprocess.PIPE)
  ret = p.communicate()
  if p.poll():
    raise Exception('%s returned' % cmd, p.returncode)
  return ret


def regex_in_list(regex, l):
  cr = re.compile(regex)
  return any(map(cr.match, l))


def check_libraries():
  patterns = [r'libdb.*\.so',
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
           'bison',
           'ccache',
           'flex',
           'lsb_release',
           'libtool',
           'gcc',
           'git',
           'java',
           'make',
           'pigz',
           'python',
           'unzip',
           'bzip2',
           'yacc']
  which = distutils.spawn.find_executable
  for p in progs:
    LOG.info('Checking program: %s' % p)
    if not which(p):
      raise Exception('Unable to find %s in PATH' % p)


def main():
  logging.basicConfig(level=logging.INFO)
  check_libraries()
  check_path()


if __name__ == '__main__':
  main()
