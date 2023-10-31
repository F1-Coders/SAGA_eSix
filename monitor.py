import subprocess

cmd = "ps -aux | grep esix"
case1 = "/usr/bin/xvfb-run python3 esix.py"
case2 = "python3 esix.py"

def run():
    check = []
    result = subprocess.check_output(cmd, shell=True).decode()
    proc_str = result.split('\n')
    for i in range(len(proc_str[:-1])):
        proc = proc_str[i]
        if (case1 in proc) or (case2 in proc):
            check.append(i)
    if len(check) != 2:
        print('eSix spider error!')

run()