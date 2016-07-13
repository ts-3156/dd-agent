from checks import AgentCheck
import subprocess
import re
import time

class UnicornCheck(AgentCheck):
  def check(self, instance):
    wc = self.worker_count()
    self.gauge('sidekiq.threads.number', wc)
    self.gauge('sidekiq.threads.busy_count', self.busy_worker_count())
    self.gauge('sidekiq.threads.idle_count', self.idle_worker_count())

#     for i in xrange(wc):
#       cmd = "ps aux | grep 'unicorn_rails worker\[%d\]' | grep -v grep | awk '{print $5 }'" % i
#       self.gauge('unicorn.processes.mem.vms', int(self.exec_cmd(cmd)) * 1000, tags=['worker_id:%d' % i])
# 
#     for i in xrange(wc):
#       cmd = "ps aux | grep 'unicorn_rails worker\[%d\]' | grep -v grep | awk '{print $6 }'" % i
#       self.gauge('unicorn.processes.mem.rss', int(self.exec_cmd(cmd)) * 1000, tags=['worker_id:%d' % i])
# 
    cmd = "ps aux | egrep 'sidekiq[[:blank:]]+[[:digit:]]+' | grep -v grep | awk '{print $5 }'"
    self.gauge('sidekiq.master.mem.vms', int(self.exec_cmd(cmd)) * 1000)

    cmd = "ps aux | egrep 'sidekiq[[:blank:]]+[[:digit:]]+' | grep -v grep | awk '{print $6 }'"
    self.gauge('sidekiq.master.mem.rss', int(self.exec_cmd(cmd)) * 1000)

  def idle_worker_count(self):
    return self.worker_count() - self.busy_worker_count()

  def busy_worker_count(self):
    cmd = "ps aux | egrep 'sidekiq[[:blank:]]+[[:digit:]]+' | grep -v grep"
    num = re.search(r'sidekiq\s+[0-9\.]+\s+\w+\s+\[(\d+)\s+\w+\s+\d+\s+\w+\]', self.exec_cmd(cmd)).group(1)
    return int(num)


  def worker_count(self):
    # sidekiq 4.1.4 app_name [0 of 3 busy]
    cmd = "ps aux | egrep 'sidekiq[[:blank:]]+[[:digit:]]+' | grep -v grep"
    num = re.search(r'sidekiq\s+[0-9\.]+\s+\w+\s+\[\d+\s+\w+\s+(\d+)\s+\w+\]', self.exec_cmd(cmd)).group(1)
    return int(num)
    
  def master_pid(self):
    cmd = "ps aux | egrep 'sidekiq[[:blank:]]+[[:digit:]]+' | grep -v grep | awk '{print $2 }'"
    return self.exec_cmd(cmd).strip()

  def exec_cmd(self, cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out

