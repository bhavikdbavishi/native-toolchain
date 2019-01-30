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

BUILD_DIR=build_docker
STAMP_DIR=$(BUILD_DIR)/stamp
SHELL=/bin/bash -o pipefail
DISTROS = centos6 \
	centos7 \
	debian7 \
	debian8 \
	ubuntu12 \
	ubuntu14 \
	ubuntu16 \
	ubuntu18

$(STAMP_DIR)/impala-toolchain-% :
	@mkdir -p $(@D)
	./in-docker.py $(IN_DOCKER_ARGS) $(@F) -- ./buildall.sh |sed -s 's/^/$(@F): /'
	@touch $@

all: $(foreach d,$(DISTROS),$(STAMP_DIR)/impala-toolchain-$d)

