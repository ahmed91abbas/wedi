import subprocess
import os, sys, shutil
from os.path import join
from win32com.client import Dispatch
from environs import Env

def path_join(list_of_names):
    path = ""
    for name in list_of_names:
        path = join(path, name)
    return path

def remove_file(file):
    try:
        os.remove(file)
    except:
        pass

def remove_dir(dir):
    try:
        shutil.rmtree(dir)
    except:
        pass

def create_shourtcut(save_to, wDir, exe_name):
    target_file = os.path.join(wDir, exe_name)
    save_to = os.path.join(save_to, "WeDi.lnk")
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(save_to)
    shortcut.Targetpath = target_file
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = target_file
    shortcut.save()

def clean_up():
    file = "main.spec"
    remove_file(file)

    dirs = ["build", "dist"]
    for dir_ in dirs:
        remove_dir(dir_)

def call_process():
    icon = join("textures", "icon.ico")
    params = ['pyinstaller', '--icon=' + icon, '--noconsole', 'main.py']
    subprocess.call(params)

def add_files(root_path):
    shutil.copyfile("settings.sav", path_join([root_path, "dist", "main", "settings.sav"]))
    shutil.copyfile(join("certifi", "cacert.pem"), path_join([root_path, "dist", "main", "certifi", "cacert.pem"]))
    folders = ["textures", "drivers", "ffmpeg_win", "domains"]
    for folder in folders:
        dist = path_join([root_path, "dist", "main", folder])
        remove_dir(dist)
        shutil.copytree(folder, dist)

def replace_local_copy(parent_path, root_path):
    dist = join(parent_path, "wedi")
    remove_dir(dist)
    exe_path = join(dist, "exe_files")
    shutil.copytree(path_join([root_path, "dist", "main"]), exe_path)
    download_path = join(dist, "wedi_downloads")
    os.mkdir(download_path)
    create_shourtcut(dist, exe_path, "main.exe")

def remove_leading_slashes(path_str):
    while path_str[0] in ["/", "\\"]:
        path_str = path_str[1:]
    return path_str
if __name__ == '__main__':
    env = Env()
    env.read_env()
    save_to_parent_path = env("SAVE_TO_PARENT_PATH")
    root_path = env("ROOT_PATH")

    print("Cleaning up old files...\n")
    clean_up()
    print("\nCreating the exe...\n")
    call_process()
    print("\nAdding missing files...\n")
    add_files(root_path)
    print("\nReplacing local copy of wedi...\n")
    replace_local_copy(save_to_parent_path, root_path)
    print("\nDone.")
