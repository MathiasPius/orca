"""Orca.

Usage:
  orca instances deduce [-y]
  orca instances export
  orca provision
  orca provision new <name>
  orca initialize [--rerun] [--trust=NETWORK]...
  orca configure

Options:
  --rerun           reinitialize using 'orca' user.
                    this effectively enforces compliance with the 'managed' role,
                    but using the configured orca user, since root login is disabled
                    after the first initialization.

  --trust=NETWORK   source networks to trust for ssh connections. [default: any]
                    can be used multiple times to specify more networks or addresses
                    e.g. --trust=192.168.0.25 --trust=10.0.0.0/8
                
  -h --help     Show this screen.
  --version     Show version.
"""

import sys
import json
import subprocess
import os
import tempfile
from shutil import copyfile
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Orca 0.1')

    if(arguments['instances']):
        if(arguments['deduce']):
            instances = os.listdir("instances")
            with tempfile.NamedTemporaryFile('w') as file:
                for instance in instances:
                    file.write("module \"{0}\" {{ source = \"../instances/{0}\" }}\n".format(instance))
                    
                file.write("\n")
                file.write("output \"hosts\" {\n" )
                file.write("  value = [\n")

                for instance in instances:
                    file.write("  {\n")
                    file.write("    ssh_key = \"${{module.{}.ssh_key}}\"\n".format(instance))
                    file.write("    address = \"${{module.{}.ipv4}}\"\n".format(instance))
                    file.write("  },\n")

                file.write("  ]\n")
                file.write("}")
                file.flush()

                if(os.path.isfile("terraform/instances.tf")):
                    print("showing diff of old (left) and new (right) file\n")
                    print("--@@@--")
                    subprocess.run(["diff", "-y", "terraform/instances.tf", file.name])
                    print("\n--@@@--\n")
                    if(arguments['-y'] or input("\nreplace old (left) instances.tf with new (right)? [y/N]: ") == "y"):
                        os.remove("terraform/instances.tf")
                        copyfile(file.name, "terraform/instances.tf")
                        print("wrote {} instances to terraform/instances.tf".format(len(instances)))
                    else:
                        print("deduced instances ignored, no changes made.")
                else:
                    copyfile(file.name, "terraform/instances.tf")
                    print("wrote {} instances to terraform/instances.tf".format(len(instances)))

        elif(arguments['export']):
            output = json.loads(subprocess.check_output(["terraform", "output", "-json"]))
            hosts = output['hosts']['value']

            with open('ansible/hosts', 'w') as file:
                file.write("[nextcloud]\n")
                for host in hosts:
                    file.write("{} ansible_ssh_private_key_file={} orca_public_key='{}.pub'".format(host['address'], host['ssh_key'], host['ssh_key']))
            
            print("exported {} instances to ansible/hosts".format(len(hosts)))
    elif(arguments['provision']):
        if(arguments['new']):
            print("this is where the interactive provisioning goes")
        else:
            subprocess.run(["terraform", "init"], capture_output=True)
            subprocess.run(["terraform", "apply"])
    elif(arguments['initialize']):
        trusted_networks = { 'trusted_networks': arguments['--trust'] }
        if(arguments['--rerun']):
            subprocess.run(["ansible-playbook", "-i", "ansible/hosts", "ansible/reinitialize.yaml", "-e", json.dumps(trusted_networks)])
        else:
            subprocess.run(["ansible-playbook", "-i", "ansible/hosts", "ansible/initialize.yaml", "-e", json.dumps(trusted_networks)])
    elif(arguments['configure']):
        subprocess.run(["ansible-playbook", "-i", "ansible/hosts", "ansible/configure.yaml"])
    else:
        print(arguments)