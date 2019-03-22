import subprocess
import os, sys, shutil

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

def clean_up():
    file = "main.spec"
    remove_file(file)

    dirs = ["build", "dist"]
    for dir_ in dirs:
        remove_dir(dir_)

def call_process():
    icon = os.path.join("textures", "icon.ico")
    params = ['pyinstaller', '--icon=' + icon, '--noconsole', 'main.py']
    subprocess.call(params)

def add_files():
    shutil.copyfile("settings.sav", "dist\\main\\settings.sav")
    shutil.copyfile("certifi\\cacert.pem", "dist\\main\\certifi\\cacert.pem")
    folders = ["textures", "drivers", "ffmpeg_win"]
    for folder in folders:
        dist = "dist\\main\\" + folder
        if os.path.exists(dist):
            shutil.rmtree(dist)
        shutil.copytree(folder, dist)

def replace_local_copy():
    dist = "C:\\Users\\Ahmed\\Desktop\\Others\\wedi"
    if os.path.exists(dist):
        shutil.rmtree(dist)
    exe_path = os.path.join(dist, "exe_files")
    shutil.copytree("dist\\main", exe_path)
    download_path = os.path.join(dist, "wedi_downloads")
    os.mkdir(download_path)

print("Cleaning up old files...\n")
clean_up()
print("\nCreating the exe...\n")
call_process()
print("\nAdding missing files...\n")
add_files()
print("\nReplacing local copy of wedi...\n")
replace_local_copy()
print("\nDone.")
