from pathlib import Path
import time
import pathlib
import shutil
import fnmatch


folder_extension = {'Images': ['.jpeg', '.png', '.jpg', '.svg', '.bmp'],
                    'Video': ['.avi', '.mp4', '.mov', '.mkv'],
                    'Documents': ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'],
                    'Audio': ['.mp3', '.ogg', '.wav', '.amr'],
                    'Archives': ['.zip', '.gz', '.tar'],
                    'Other': []}

exception_lst = []
images_count = 0
video_count = 0
documents_count = 0
audio_count = 0
archives_count = 0
other_files_count = 0

def create_sort_folder(path: Path, folder_name: str):
    '''Create folders for sorted files, if the names are occupied - rename the existing ones and create new'''

    try:
        path.joinpath(folder_name).mkdir()
                
    except FileExistsError:
        old_path = path / folder_name
        target = 'Old_' + folder_name + '_' + time.strftime('%Y%m%d%H%M%S')
        old_path.rename(path / target)
        
        create_sort_folder(path, folder_name)

def exception_search(path: Path, target_path: Path) -> bool:
    
    for name in exception_lst:
        if fnmatch.fnmatch(target_path, path / name / '**/*') or \
            fnmatch.fnmatch(target_path, path / name / '**') or \
            fnmatch.fnmatch(target_path, path / name):
            return True
        
    return False

def sort_process(path: Path, path_target: Path, name_file: str, extension: str) -> Path:
    '''sort by extension into folders.
        Return the new file StrPath'''
    for folder, folder_key in folder_extension.items():
        if extension in folder_key:
            
            if folder == 'Archives':
                target = path / 'Archives' / pathlib.PurePath(path / 'Archives' / name_file).stem
                shutil.unpack_archive(path_target, target)
                path_target.unlink()
                count_files(folder)
                return(target)                
            
            target = path / folder / name_file
            path_target.replace(target)
            count_files(folder)
            return(target)
    
    else:
        target = path / 'Other' / name_file
        path_target.replace(target)
        count_files('Other')
        return(target)
    
def normalize(name: str, count: int) -> str:
    ''' replace with '_' all characters except Latin and numbers.
        also add the files count and time'''
    new_name = ''
    for chr in name:
        if len(new_name) > 15:
            break
        if 65 <= ord(chr) <= 90 or 97 <= ord(chr) <= 122 or 48 <= ord(chr) <= 57:
            new_name += chr
        else:
            new_name += '_'   
    new_name += '_' + str(count) + '_' + time.strftime('%Y_%m_%d_%H_%M_%S')
             
    return new_name

def count_files(type_file: str):
    '''count files by type'''

    if type_file == 'Images':
        global images_count
        images_count += 1
    if type_file == 'Video':
        global video_count
        video_count += 1
    if type_file == 'Documents':
        global documents_count
        documents_count += 1
    if type_file == 'Audio':
        global audio_count
        audio_count += 1
    if type_file == 'Archives':
        global archives_count
        archives_count += 1
    if type_file == 'Other':
        global other_files_count
        other_files_count += 1

def sorter() -> str:

    print('Please write main path for sorting files, for example: C:\\Users\\User name')
    path = input('>>> ')
    path = Path(path)
    result = 'result.txt' 
    count_files = 0
    folders_lst = []
    changing_files = ''
    changing_folders = ''       
    print("Sorting files DONE")

    for folder_name in folder_extension:
        create_sort_folder(path, folder_name)
        exception_lst.append(folder_name)
        exception_lst.append(result)
    
    for item in path.glob('**/*'):
        
        if exception_search(path, item):
            continue
        
        if item.is_dir():
            if exception_search(path, item):
                continue
            folders_lst.append(item)
            
        if item.is_file():
            extension = pathlib.PurePath(item).suffix
            name = normalize(pathlib.PurePath(item).stem, count_files) + extension
            count_files += 1
            p = sort_process(path, item, name, extension)
            changing_files += '  ' + str(item) + ' --->    ' + str(p) + '\n'
                    
    for folder in reversed(folders_lst):
        folder.rmdir()
        changing_folders += '  ' + str(folder) + '---> deleted\n'


    with open(path / result, 'w') as fb:
        fb.write(f'Sort result:\n\nFound folders:\n{changing_folders}\nFound files {count_files}:\n\
Images = {images_count}\nVideo = {video_count}\nDocuments = {documents_count}\n\
Audio = {audio_count}\nArchives = {archives_count}\nOther = {other_files_count}\n\n\
Remove to:\n{changing_files}')
    
    return f'Found files {count_files}:\n\
Images = {images_count}\nVideo = {video_count}\nDocuments = {documents_count}\n\
Audio = {audio_count}\nArchives = {archives_count}\nOther = {other_files_count}\nMore info in {path / result}'

