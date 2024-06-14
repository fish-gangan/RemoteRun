# RemoteRun

#IDEA 远程在linux执行代码
#在你的任意脚本如下试用：
```
import time
from remote.run_remote import RemoteRunner
import sys

runner = RemoteRunner()
runner.run()
"""
    1. 以上两句代码可将本地idea文件上传到linux, 并在idea发起代码执行，执行的是当前文件哦
    2. 以下代码会真正在linux生效，以上代码在linux会跳过
"""

for i in range(5):
    print("%s->当前运行的文件=%s python解释器路径=%s" % (i, __file__, sys.executable))
    time.sleep(0.1)
```
