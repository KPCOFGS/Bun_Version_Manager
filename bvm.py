import os
import shutil
import argparse
import subprocess
import requests
from bs4 import BeautifulSoup
class BunVersionManager():
    def __init__(self):
        '''
        Creates bvm folder if it does not exist.
        Creates current_version in the bvm folder.
        current_version file keeps track of the current using version of Bun.
        '''
        self.base_dir = os.path.join(os.path.expanduser("~"), "bvm")
        self.dynamic_file = os.path.join(self.base_dir, "current_version")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _get_version_dir(self, version):
        '''
        Get version directories
        '''
        return os.path.join(self.base_dir, version)

    def add(self, version):
        '''
        Add a Bun version if it does not exist in bvm folder.
        Download the version using curl
        Bun will be downloaded as .bun folder in your home directory.
        Then Move .bun to ~/bvm/its_version_folder
        Bun will also add PATH to your shell regardless of existing duplicates.
        Which will be fixed by removing duplicates
        Then switch to the downloaded version automatically
        '''
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
        '''
        Bun will add PATH to your shell regardless of existing duplicates.
        Which will be fixed by removing duplicates.
        Then add a new PATH that will recognize what version of Bun user's using
        '''
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
        '''
        Delete a version
        '''
        version_dir = self._get_version_dir(version)
        if not os.path.exists(version_dir):
            print(f"Version {version} does not exist.")
            return
        shutil.rmtree(version_dir)

    def switch(self, version):
        '''
        Switch a version
        '''
        version_dir = self._get_version_dir(version)
        if not os.path.exists(version_dir):
            print(f"Version {version} does not exist.")
            return
        # Write the version directory to the dynamic file
        with open(self.dynamic_file, 'w') as f:
            f.write(f'{version_dir}')
        print("Success! Switched to the new bun version. Start a new shell session for this to take effect")
    def list(self):
        '''
        List all downloaded Bun versions
        '''
        versions = os.listdir(self.base_dir)
        if versions:
            print("Downloaded versions:")
            for version in versions:
                if version != "current_version":
                    print(version)
        else:
            print("No versions downloaded.")

    def browse(self, page_number):
        '''
        Browse through Bun releases using requests and beautifulsoup4
        '''
        url = f"https://github.com/oven-sh/bun/releases?page={page_number}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', class_='Link--primary Link')
            print(f"*** Page {page_number} ***")
            print()
            _next = 0
            for link in links:
                print(link.get_text())
                _next += 1
            if _next == 10:
                print()
                print(f"To see more results, do: python bvm.py browse {int(page_number) + 1}")
            elif _next == 0:
                print("No content")
        else:
            print(f"Failed to fetch page {page_number}: Status code {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description='Manage .bun versions.')
    parser.add_argument('command', choices=['add', 'delete', 'switch', 'list', 'browse'])
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
    elif args.command == 'browse':
        if args.version:
            try:
                bun_manager.browse(int(args.version))
            except:
                print("Please provide a valid page number")
        elif not args.version:
            bun_manager.browse(1)
if __name__ == "__main__":
    main()
