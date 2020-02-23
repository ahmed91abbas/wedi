import subprocess
import os, sys, shutil
from os.path import join
import zipfile
from environs import Env


def path_join(list_of_names):
    path = ''
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

def clean_up():
    file = 'wedi.spec'
    remove_file(file)

    dirs = ['build', 'dist']
    for dir_ in dirs:
        remove_dir(dir_)

def upgrade_packages():
    params = ['pip', 'install', '-U', '-r', 'requirements.txt']
    subprocess.call(params)

def call_process(root_path):
    icon = join('textures', 'icon.ico')
    site_packages = path_join([root_path, 'env', 'Lib', 'site-packages'])
    params = ['pyinstaller3',
              '--icon=' + icon,
              '--onefile',
              '--noconsole',
              '--paths', site_packages,
              '--add-data', 'domains;.\\domains',
              'wedi.py']
    subprocess.call(params)

def add_files(root_path):
    shutil.copyfile('settings.json', path_join([root_path, 'dist', 'settings.json']))
    folders = ['textures', 'drivers', 'domains', 'certifi']
    if sys.platform == 'win32' or sys.platform == 'win64':
        folders.append('ffmpeg_win')
    for folder in folders:
        dist = path_join([root_path, 'dist', folder])
        remove_dir(dist)
        shutil.copytree(folder, dist)

def replace_local_copy(parent_path, root_path):
    dist = join(parent_path, 'wedi')
    remove_dir(dist)
    shutil.copytree(path_join([root_path, 'dist']), dist)
    download_path = join(dist, 'wedi_downloads')
    os.mkdir(download_path)

def remove_leading_slashes(path_str):
    while path_str[0] in ['/', '\\']:
        path_str = path_str[1:]
    return path_str

def create_release_zip(parent_path):
    local_copy = join(parent_path, 'wedi')
    release_target = join(local_copy, 'wedi-win.zip')

    empty_dirs = []
    zipf = zipfile.ZipFile(release_target, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(local_copy):
        target_folder = remove_leading_slashes(root.replace(parent_path, ''))
        empty_dirs.extend([dir for dir in dirs if os.listdir(join(root, dir)) == []])
        for filename in files:
            if filename == 'wedi-win.zip':
                continue
            zipf.write(join(root, filename), join(target_folder, filename))

        for dirname in empty_dirs:
            zipinfo = zipfile.ZipInfo(join(target_folder, dirname) + '/')
            zipf.writestr(zipinfo, '')
        empty_dirs = []
    zipf.close()

def call_linux_process(root_path):
    icon = join('textures', 'icon.ico')
    params = ['pyinstaller',
              '--icon=' + icon,
              '--onefile',
              '--noconsole',
              '--hidden-import', 'PIL._tkinter_finder',
              '--add-data', 'domains/*:domains/',
              'wedi.py']
    subprocess.call(params)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    save_to_parent_path = env('SAVE_TO_PARENT_PATH')
    root_path = env('ROOT_PATH')

    _platform = sys.platform
    if _platform == 'linux' or _platform == 'linux2':
        print('Cleaning up old files...\n')
        clean_up()
        print('\nCreating the exe...\n')
        call_linux_process(root_path)
        print('\nAdding missing files...\n')
        add_files(root_path)
        print('\nDone.')
    elif _platform == 'win32' or _platform == 'win64':
        print('Cleaning up old files...\n')
        clean_up()
        print('\nUpgrading python packages...\n')
        upgrade_packages()
        print('\nCreating the exe...\n')
        call_process(root_path)
        print('\nAdding missing files...\n')
        add_files(root_path)
        print('\nReplacing local copy of wedi...\n')
        replace_local_copy(save_to_parent_path, root_path)
        print('\nCreating release zip file...\n')
        create_release_zip(save_to_parent_path)
        print('\nDone.')
