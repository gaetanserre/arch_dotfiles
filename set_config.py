#
# Created in 2023 by Gaëtan Serré
#

import os
import shutil
import argparse
import json
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser(description="Set config file")
    parser.add_argument(
        "-s", "--save", action="store_true", default=False, help="save config files."
    )
    parser.add_argument(
        "-hd", "--home-dir", default="/home/gaetan", help="home directory."
    )

    parser.add_argument(
        "-ch",
        "--chroot",
        action="store_true",
        default=False,
        help="Execute chroot commands.",
    )
    parser.add_argument(
        "-p", "--packages", action="store_true", default=False, help="install packages."
    )
    parser.add_argument(
        "-l",
        "--load",
        action="store_true",
        default=False,
        help="load config files and commands.",
    )
    return parser.parse_args()


def print_red(text):
    print(f"\033[91m{text}\033[00m")


def print_green(text):
    print(f"\033[92m{text}\033[00m")


def copy(src, dest):
    print_green(f"+ cp {src} -> {dest}")
    if os.path.isfile(src):
        shutil.copy(src, dest)
    elif os.path.isdir(src):
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest, copy_function=shutil.copy)
    else:
        return False
    return True


def exec_command(command):
    print_green(f"+ {command}")
    os.system(command)


def install_package(package, aur_manager):
    exec_command(f"{aur_manager} -S --noconfirm {package}")


def chroot():
    json_config = json.loads(open("config.json", "r").read())
    for command in json_config["chroot"]:
        exec_command(command)


def install_packages():
    json_config = json.loads(open("config.json", "r").read())

    # install aur manager
    for command in json_config["aur_manager"]["commands"]:
        exec_command(command)

    # install packages
    for package in json_config["packages"]:
        install_package(package, json_config["aur_manager"]["name"])

    # execute packages related commands
    for command in json_config["pkg_commands"]:
        exec_command(command)


def load_config():
    json_config = json.loads(open("config.json", "r").read())

    # copy config files
    files_info = json.loads(open("files_location.json", "r").read())
    for file_name, file_info in files_info.items():
        try:
            file_dest  = file_info["dest"]
            file_owner = file_info["owner"]
            file_group = file_info["group"]

            file = os.path.join("dotfiles", file_name)
            success = copy(file, file_dest)
            if not success:
                print_red(f"File {file} not found, skipping.")
                continue
            exec_command(f"chown -R {file_owner}:{file_group} {file_dest}")

        except Exception as e:
            print(file)
            print_red(e)

    # execute commands
    for command in json_config["commands"]:
        exec_command(command)


def get_group_owner(path):
    file = Path(path)
    return file.owner(), file.group()

def save_config(home_dir):
    # create folder to save config files
    if os.path.isdir("dotfiles"):
        shutil.rmtree("dotfiles")
    os.mkdir("dotfiles")

    json_config = json.loads(open("config.json", "r").read())

    # copy files and folders to dotfiles and save their absolute path
    files_location = {}
    for file in json_config["files"]:
        # copy file to dotfiles
        try:
            file = os.path.join(home_dir, file.replace("$HOME/", ""))

            dir_name = file.split("/")[-1]
            success = copy(
                file, f"dotfiles/{dir_name}" if os.path.isdir(file) else "dotfiles/"
            )
            if not success:
                print_red(f"File {file} not found, skipping.")
                continue

            owner, group = get_group_owner(file)
            file_name = file.split("/")[-1]
            files_location[file_name] = {
                "dest": file,
                "owner": owner,
                "group": group
            }

        except Exception as e:
            print(file)
            print_red(e)

    # save files absolute path for loading and give permissions
    location = open("files_location.json", "w")
    location.write(json.dumps(files_location, indent=4))


if __name__ == "__main__":
    args = cli()

    if args.save:
        save_config(args.home_dir)
    elif args.chroot:
        chroot()
    elif args.packages:
        install_packages()
    elif args.load:
        load_config()
    else:
        raise ValueError("Please specify an action.")
