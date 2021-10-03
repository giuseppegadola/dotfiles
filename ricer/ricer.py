#!/usr/bin/python
import os
import shutil
import tempfile
import time


def get_available_files():
    """Get a list of the available configurations and display it"""
    # get files
    path = os.path.join(os.path.expanduser("~"), "ricer/configs")
    files = os.scandir(path)
    files = [str(i.name) for i in files if i.is_file()]

    # display available files
    print("index\tname\n-----\t----")
    for i in range(len(files)):
        print(f"{i}\t{files[i]}")
    return files


def select_file(files):
    """Select one of the files via user input in the list and return its index"""
    file_index = -1
    while file_index not in range(len(files)):
        file_index = input("Insert desired number (q to exit):")
        if file_index.lower() == "q":
            return -1
        try:
            file_index = int(file_index)
            if file_index not in range(len(files)):
                print("Input not in range")
        except ValueError:
            print("Input not valid")
    return file_index


def get_content(files_list, index):
    """parse the content of the file separated by '///'
    and return a list of lists of strings"""
    file = files_list[index]
    full_path = os.path.join(os.path.expanduser("~"), "ricer/configs", file)
    with open(full_path, "r") as f:
        content = f.read()
        content_list = content.split("///")
    for i in range(len(content_list)):
        lines = content_list[i].split("\n")
        # remove empty string as last item
        lines = [str(x) for x in lines if x != ""]
        content_list[i] = lines
    return content_list


def replace_block(file_path, pattern, subst, strict_equality=False, repetition=False):
    # create temp file and use it to write
    fh, abs_path = tempfile.mkstemp()
    with os.fdopen(fh, "w") as new_file:
        with open(file_path) as old_file:
            writing = False
            line_index = 0
            found = False
            for line in old_file:
                if strict_equality:
                    if line == pattern:
                        if not found or repetition:
                            writing = True
                            found = True
                else:
                    if pattern in line:
                        if not found or repetition:
                            writing = True
                            found = True
                if writing and line_index < len(subst):
                    new_file.write(subst[line_index] + "\n")
                    line_index += 1
                else:
                    new_file.write(line)
                    writing = False
                    line_index = 0
    # copy permissions (not sure if it's necessary)
    shutil.copymode(file_path, abs_path)
    # remove the old file and move the new one
    os.remove(file_path)
    shutil.move(abs_path, file_path)
    print("replaced", '"' + pattern.replace("\n", "") + '"', "in", file_path)


def replace_all(file_path, content):
    with open(file_path, "w") as file:
        for line in content:
            file.write(line + "\n")
        print("wrote file:", file_path)


def insert_content(content):
    config_path = os.path.join(
        os.path.expanduser("~"),
        ".config",
    )
    # create backup
    print("creating backup to ~/.config-ricer-backup...")
    os.system("mkdir .config-ricer-backup")
    os.system(
        "cp -r -t .config-ricer-backup/ ~/.config/{alacritty/, qtile/, nvim/, fish/, dunst/}"
    )
    print("done")

    # wallpaper
    replace_all(os.path.join(config_path, "qtile/scripts/wallpaper_path"), content[0])
    # alacritty
    alacritty_path = os.path.join(config_path, "alacritty/alacritty.yml")
    replace_block(alacritty_path, "colors:\n", content[1], strict_equality=True)
    replace_block(alacritty_path, "family:", content[2], repetition=True)
    # qtile
    qtile_path = os.path.join(config_path, "qtile/config.py")
    replace_block(qtile_path, "colors = [\n", content[3], strict_equality=True)
    replace_block(qtile_path, "font = ", content[4])
    # nvim
    nvim_path = os.path.join(config_path, "nvim/init.vim")
    replace_block(nvim_path, "colorscheme ", content[5])
    # fish
    fish_path = os.path.join(config_path, "fish/config.fish")
    replace_block(fish_path, "set fish_color_normal", content[6])
    # dunst
    dunst_path = os.path.join(config_path, "dunst/dunstrc")
    replace_block(dunst_path, "geometry = ", content[7])
    replace_block(dunst_path, "font = ", content[8])
    replace_block(dunst_path, "[urgency_low]", content[9])

    # reload
    print("reloading wallpaper...")
    os.system(
        "~/.scripts/live_wallpaper.sh $(cat ~/.config/qtile/scripts/wallpaper_path) &> /dev/null"
    )
    print("done\nreloading qtile...")
    os.system("qtile cmd-obj -o cmd -f restart")
    print("done")


def ending():
    redo = input("Do you want to choose another theme? [y/n]: ")
    if redo.lower() == "y" or redo.lower() == "yes":
        print("\n-----------\n")
        return True
    else:
        print("Delete backup if there were no errors")
        print("Program finished")
        return False


running = True
while running:
    files = get_available_files()
    file_index = select_file(files)
    if file_index < 0:
        running = ending()
        if not running:
            break
    confirm = input(f"Do you want to proceed applying {files[file_index]}? [y/n]: ")
    if confirm.lower() == "y" or confirm.lower() == "yes":
        # do the things
        content_list = get_content(files, file_index)
        insert_content(content_list)
        time.sleep(2)
        running = ending()
        if not running:
            break
    else:
        running = ending()
        if not running:
            break