#!/usr/bin/env bash
chmod o+wt '/sys/fs/cgroup/freezer/'
chmod o+wt '/sys/fs/cgroup/memory/user.slice'
#chmod o+wt '/sys/fs/cgroup/memory/user.slice/user-1000.slice/user@1000.service'
chmod o+wt '/sys/fs/cgroup/cpu,cpuacct/user.slice'
chmod o+wt '/sys/fs/cgroup/cpuset/'
chmod o+wt '/sys/fs/cgroup/cpu,cpuacct/'
swapoff -a
