import os
import shutil
import argparse
import json


def cli():
    parser = argparse.ArgumentParser(description="Set config file")
    parser.add_argument(
        "-s", "--save", action="store_true", default=False, help="save config files."
    )
    parser.add_argument(
        "-hd", "--home-dir", default="/home/gaetan", help="home directory"
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


def load_config():
    json_config = json.loads(open("config.json", "r").read())

    # copy config files
    files_dest = json.loads(open("files_location.json", "r").read())
    for file_name, file_dest in files_dest.items():
        try:
            file = os.path.join("dotfiles", file_name)

            if os.path.isfile(file):
                shutil.copy(file, file_dest)
            elif os.path.isdir(file):
                if os.path.isdir(file_dest):
                    shutil.rmtree(file_dest)
                shutil.copytree(file, file_dest, copy_function=shutil.copy)

        except Exception as e:
            print(file)
            print_red(e)

    # execute commands
    for command in json_config["commands"]:
        exec_command(command)


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

            if os.path.isfile(file):
                shutil.copy(file, "dotfiles/")
            elif os.path.isdir(file):
                dir_name = file.split("/")[-1]
                shutil.copytree(file, f"dotfiles/{dir_name}", copy_function=shutil.copy)
            else:
                print_red(f"File {file} not found, skipping.")
                continue

            file_name = file.split("/")[-1]
            files_location[file_name] = file

        except Exception as e:
            print(file)
            print_red(e)

    # save files absolute path for loading and give permissions
    location = open("files_location.json", "w")
    location.write(json.dumps(files_location, indent=4))
    exec_command("chmod 777 dotfiles files_location.json")


if __name__ == "__main__":
    args = cli()

    if args.save:
        save_config(args.home_dir)
    elif args.chroot:
        chroot()
    elif args.packages:
        install_packages()
    if args.load:
        load_config()
    else:
        raise ValueError("Please specify an action.")
