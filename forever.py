import subprocess, time

foreveeeeeeeeeeeeeeeeeeeeeeeeeeeer = True


def forever():
    proc = subprocess.Popen(["rantevou"])
    time.sleep(2)
    proc.kill()


while foreveeeeeeeeeeeeeeeeeeeeeeeeeeeer:
    forever()
