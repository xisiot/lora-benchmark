import subprocess
import os
file_path = os.path.join(os.path.dirname(__file__) + 'udp_push_locustfile.py')
print ('locust -f ' + file_path)
subprocess.call('locust -f ' + file_path, True)