import socket
import sys
import termios
import tty
import paramiko
import os
from paramiko.py3compat import u

# thing to send over SSH on instance connect
IRSSI_COMMAND = 'bash launch.sh\n'


class CyberSSH(paramiko.SSHClient):
    """SSH functionality."""

    def copy_files(self):
        sftp = self.open_sftp()
        try:
            sftp.mkdir('.irssi', mode=0o700)
        except:
            pass  # whatever
        # self._sftp_copy(sftp, 'irssiconfig', '.irssi/config')
        self._sftp_copy(sftp, 'screenrc', '.screenrc')
        self._sftp_copy(sftp, 'launch.sh', 'launch.sh')
        sftp.close()

    def _sftp_copy(self, sftp: str, src: str, dst: str):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        local_file_path = os.path.join(dir_path, '..', src)
        print(f"*** Copying {local_file_path} -> {dst}")
        sftp.put(local_file_path, dst)

    def screen_irssi(self):
        self.exec_command(
            command=IRSSI_COMMAND,
            get_pty=True,
        )

    def interactive(self: paramiko.client):
        try:
            chan = self.invoke_shell(term='xterm-256color')
            chan.send(IRSSI_COMMAND)
            print('*** Connected!\n')
            self.posix_shell(chan)
            chan.close()
            self.close()

        except Exception as e:
            try:
                self.close()
            except:
                pass
            raise Exception from e

    def posix_shell(self, chan):
        import select

        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            chan.settimeout(0.0)

            while True:
                r, w, e = select.select([chan, sys.stdin], [], [])
                if chan in r:
                    try:
                        x = u(chan.recv(1024))
                        if len(x) == 0:
                            sys.stdout.write('\r\n*** EOF\r\n')
                            break
                        sys.stdout.write(x)
                        sys.stdout.flush()
                    except socket.timeout:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    chan.send(x)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


def _keyfile() -> str:
    return os.path.join(os.environ['HOME'], '.ssh', 'awsmish.pem')


def connect(hostname: str, username: str = 'ec2-user') -> CyberSSH:
    port = 22

    if hostname.find(':') >= 0:
        hostname, portstr = hostname.split(':')
        port = int(portstr)

    client = CyberSSH()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    print('*** Connecting...')
    client.connect(hostname, port, username, key_filename=_keyfile())
    return client