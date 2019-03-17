"""Orca.

Usage:
  orca instances deduce [-y]
  orca instances export
  orca provision
  orca provision new [--name=NAME] [--storage=SIZE] [--drop=DROP] [--image=IMAGE]
  orca initialize [--rerun] [--trust=NETWORK]...
  orca configure

Options:
  -h --help         show this screen.
  --version         show version.

  --name=NAME       name of the new instance.
                    must ONLY contain letters, digits and underscores.
                    must NOT be longer than 32 characters

  --storage=SIZE    size of the attached nextcloud volume in GB. [default: 10]
                    must be between 1-3000GB

  --drop=DROP       Digital Ocean droplet size to use. [default: s-1vcpu-1gb]

  --image=IMAGE     which Digital Ocean image to use. [default: ubuntu-18-04-x64]
                    only tested with ubuntu-18-04-x64 but others may work too


  --rerun           reinitialize using 'orca' user.
                    this effectively enforces compliance with the 'managed' role,
                    but using the configured orca user, since root login is disabled
                    after the first initialization.

  --trust=NETWORK   source networks to trust for ssh connections. [default: any]
                    these arguments are used when configuring ufw on the endpoint.
                    can be used multiple times to specify more networks or addresses
                    e.g. --trust=192.168.0.25 --trust=10.0.0.0/8
"""

import re
import sys
import json
import subprocess
import os
import tempfile
from shutil import copyfile
from docopt import docopt


valid_instance_name = re.compile(r"[^a-zA-Z_0-9]")

def instantiate_template(src, dst, dictionary):
    with open(dst, 'w') as instance:
        with open(src, 'r') as template:
            for line in template:
                for name, value in dictionary.items():
                    instance.write(line.replace('{{{{{}}}}}'.format(name), value))


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
                    file.write("{} ansible_ssh_private_key_file={} orca_public_key='{}.pub'\n".format(host['address'], host['ssh_key'], host['ssh_key']))
            
            print("exported {} instances to ansible/hosts".format(len(hosts)))
    elif(arguments['provision']):
        if(arguments['new']):
            print(arguments)
            
            instance_name = arguments['--name']
            while(instance_name == None or len(instance_name) == 0 or len(instance_name) > 32 or len(valid_instance_name.findall(instance_name)) != 0):
                if(instance_name == None):
                    instance_name = input('instance name: ')
                elif(len(instance_name) == 0):
                    print("ERROR: no name given")
                    instance_name = input('instance name: ')
                elif(len(instance_name) > 32):
                    print("ERROR: name too long ({}). max length: 32".format(len(instance_name)))
                    instance_name = input('instance name: ')
                else:
                    invalid_chars = ", ".join(["'{}'".format(x) for x in valid_instance_name.findall(instance_name)])
                    print("ERROR: invalid characters in name: {}".format(invalid_chars))
                    instance_name = input('instance name: ')

            instance_dir = "instances/{}".format(instance_name)
            if(os.path.exists(instance_dir)):
                if(input("WARN: instance directory already exists! abort? [Y/n]: ") != "n"):
                    exit()
            else:
                os.mkdir(instance_dir, 0o700)

            privkey = "{}/{}".format(instance_dir, "id_ed25519")
            pubkey = "{}/{}".format(instance_dir, "id_ed25519.pub")
            if(os.path.isfile(privkey) or os.path.isfile(pubkey)):
                if(input("WARN: ssh keys already exist for this instance. recreate? [y/N]: ") == "y"):
                    os.remove(privkey)
                    os.remove(pubkey)

            if(not os.path.isfile(privkey) and not os.path.isfile(pubkey)):
                subprocess.run(["ssh-keygen", "-t", "ed25519", "-a", "100", "-f", privkey, "-C", "orca@{}".format(instance_name), "-N", ""])

            instantiate_template('templates/000-ssh.tf', "{}/000-ssh.tf".format(instance_dir), {'INSTANCEID': instance_name})
            instantiate_template('templates/010-nextcloud.tf', "{}/010-nextcloud.tf".format(instance_dir), {'INSTANCEID': instance_name})
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