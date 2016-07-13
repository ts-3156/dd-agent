from checks import AgentCheck
import subprocess
import re
import time

class UnicornCheck(AgentCheck):
  def check(self, instance):
    wc = self.worker_count()
    self.gauge('unicorn.processes.number', wc)

    for i in xrange(wc):
      cmd = "ps aux | grep 'unicorn_rails worker\[%d\]' | grep -v grep | awk '{print $5 }'" % i
      self.gauge('unicorn.processes.mem.vms', int(self.exec_cmd(cmd)) * 1000, tags=['worker_id:%d' % i])

    for i in xrange(wc):
      cmd = "ps aux | grep 'unicorn_rails worker\[%d\]' | grep -v grep | awk '{print $6 }'" % i
      self.gauge('unicorn.processes.mem.rss', int(self.exec_cmd(cmd)) * 1000, tags=['worker_id:%d' % i])

    cmd = "ps aux | grep 'unicorn_rails master' | grep -v grep | awk '{print $5 }'"
    self.gauge('unicorn.master.mem.vms', int(self.exec_cmd(cmd)) * 1000)

    cmd = "ps aux | grep 'unicorn_rails master' | grep -v grep | awk '{print $6 }'"
    self.gauge('unicorn.master.mem.rss', int(self.exec_cmd(cmd)) * 1000)

    self.gauge('unicorn.processes.idle_count', self.idle_worker_count())

  def idle_worker_count(self):
    wc = self.worker_count()
    before_cpu = {}
    for i in xrange(wc):
      pid = self.worker_pid(i)
      before_cpu[pid] = self.cpu_time(pid)

    time.sleep(1)

    after_cpu = {}
    for i in xrange(wc):
      pid = self.worker_pid(i)
      after_cpu[pid] = self.cpu_time(pid)

    result = 0
    for i in xrange(wc):
      pid = self.worker_pid(i)
      if after_cpu[pid] - before_cpu[pid] == 0:
        result += 1

    return result


  def worker_count(self):
    cmd = "ps aux | grep 'unicorn_rails worker' | grep -v grep | wc -l"
    return int(self.exec_cmd(cmd))
    
  def cpu_time(self, pid):
    cmd = "cat /proc/%s/stat | awk '{print $14,$15 }'" % pid
    usr, sys = map(int, re.split(r'\s+', self.exec_cmd(cmd).strip()))
    return usr + sys

  def worker_pid(self, worker_id):
    cmd = "ps aux | grep 'unicorn_rails worker\[%d\]' | grep -v grep | awk '{print $2 }'" % worker_id
    return self.exec_cmd(cmd).strip()

  def master_pid(self):
    cmd = "ps aux | grep 'unicorn_rails master' | grep -v grep | awk '{print $2 }'"
    return self.exec_cmd(cmd).strip()

  def exec_cmd(self, cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out

