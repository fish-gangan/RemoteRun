import time

from remote.run_remote import RemoteRunner
import sys

runner = RemoteRunner()
runner.run()
for i in range(5):
    print("%s->当前运行的文件=%s python解释器路径=%s" % (i, __file__, sys.executable))
    time.sleep(0.1)
