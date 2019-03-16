import sys
import json
import subprocess


if len(sys.argv) <= 1:
    print("unknown command")
else:
    if(sys.argv[1] == "hosts"):
        if(sys.argv[2] == "refresh"):
            output = json.loads(subprocess.check_output(["terraform", "output", "-json"]))
            hosts = output['hosts']['value']

            with open('ansible/hosts', 'w') as file:
                file.write("[nextcloud]")
                for host in hosts:
                    file.write("{} ansible_ssh_private_key_file={}".format(host['address'], host['ssh_key']))
            
            print("wrote {} host(s) to ansible/hosts".format(len(hosts)))
        else:
            print("unknown hosts command: {}".format(sys.argv[2]))
    else:
        print("unknown command: {}".format(sys.argv[1]))
