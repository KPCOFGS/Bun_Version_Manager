import os
import shutil
import argparse
import subprocess

class BunVersionManager():
    def __init__(self):
        self.base_dir = os.path.join(os.path.expanduser("~"), "bvm")
        self.dynamic_file = os.path.join(self.base_dir, "current_version")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _get_version_dir(self, version):
        return os.path.join(self.base_dir, version)

    def add(self, version):
        version_dir = self._get_version_dir(version)
        if os.path.exists(version_dir):
            print(f"Version {version} already exists.")
            return
        os.makedirs(version_dir)

        # Download the .bun version
        subprocess.run(f"curl -fsSL https://bun.sh/install | bash -s bun-v{version}", shell=True, check=True, cwd=version_dir)

        # Move the .bun folder to the target directory
        bun_dir = os.path.join(os.path.expanduser("~"), ".bun")
        target_bun_dir = os.path.join(version_dir, ".bun")
        shutil.move(bun_dir, target_bun_dir)

        # Remove environment variable exports from shell config
        self.remove_env_exports()

        self.switch(version)

    def remove_env_exports(self):
        shell = os.getenv('SHELL')
        if shell:
            shell = shell.split('/')[-1]  # Extract the shell name (e.g., bash, zsh, fish)
            if shell == 'bash':
                shell_config_file = os.path.expanduser('~/.bashrc')
                path_line = 'export PATH'
            elif shell == 'zsh':
                shell_config_file = os.path.expanduser('~/.zshrc')
                path_line = 'export PATH'
            elif shell == 'fish':
                shell_config_file = os.path.expanduser('~/.config/fish/config.fish')
                path_line = 'set -x PATH'
            else:
                return
            if os.path.exists(shell_config_file):
                with open(shell_config_file, 'r') as f:
                    lines = f.readlines()

                has_current_version_line = False
                for line in lines:
                    if "$HOME/bvm/current_version" in line and "export PATH" in line:
                        has_current_version_line = True
                        break
                with open(shell_config_file, 'w') as f:
                    for line in lines:
                        if ("export BUN_INSTALL=\"$HOME/.bun\"" in line or
                            "export PATH=$BUN_INSTALL/bin:$PATH" in line or
                            line.strip() == "# bun"):
                            continue
                        f.write(line)
                    if "# bun\n" in lines:
                        f.write("")

                    if not has_current_version_line:
                        f.write(f'\nif [ -f "$HOME/bvm/current_version" ]; then\n')
                        f.write(f'    {path_line}="$(cat $HOME/bvm/current_version)/.bun/bin:$PATH"\n')
                        f.write(f'fi\n')


    def delete(self, version):
        version_dir = self._get_version_dir(version)
        if not os.path.exists(version_dir):
            print(f"Version {version} does not exist.")
            return
        shutil.rmtree(version_dir)

    def switch(self, version):
        version_dir = self._get_version_dir(version)
        if not os.path.exists(version_dir):
            print(f"Version {version} does not exist.")
            return
        # Write the version directory to the dynamic file
        with open(self.dynamic_file, 'w') as f:
            f.write(f'{version_dir}')
        self.refresh_shell()

    def list(self):
        versions = os.listdir(self.base_dir)
        if versions:
            print("Downloaded versions:")
            for version in versions:
                if version != "current_version":
                    print(version)
        else:
            print("No versions downloaded.")

    def refresh_shell(self):
        try:
            if os.name == 'posix':  # Unix-like system
                os.system("exec $SHELL")
        except Exception as e:
            print(f"An error occurred while refreshing the shell: {e}. Open a new shell session for the script to take effect")


def main():
    parser = argparse.ArgumentParser(description='Manage .bun versions.')
    parser.add_argument('command', choices=['add', 'delete', 'switch', 'list'])
    parser.add_argument('version', nargs='?', help='The version to operate on.')

    args = parser.parse_args()

    bun_manager = BunVersionManager()

    if args.command == 'add':
        bun_manager.add(args.version)
    elif args.command == 'delete':
        bun_manager.delete(args.version)
    elif args.command == 'switch':
        bun_manager.switch(args.version)
    elif args.command == 'list':
        bun_manager.list()

if __name__ == "__main__":
    main()
