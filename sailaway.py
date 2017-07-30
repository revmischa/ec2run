#!/usr/bin/env python3

from cyber import ec2
from cyber import ssh


def main():
    instance = ec2.run_instance()
    ip = instance.public_ip_address

    try:
        client = ssh.connect(ip)
        client.copy_files()
        client.close()
        client.ssh_client(ip)
        # client.interactive()
    except Exception as ex:
        print("*** Exception:")
        print(ex)

    instance.terminate()
    print("*** Terminated")


if __name__ == '__main__':
    main()
