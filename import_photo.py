# Копирует фото и видео-файлы из нескольких каталогов (не рекурсивно) в один.
# Переименовывает каждый файл согласно дате и времени съемки (EXIF) или изменения.
# Если файл с таким именем уже существует, добавляет к имени цифру.
# Сохраняет список скопированных файлов чтобы не копировать их повторно.
# Метаданные (в том числе дата изменения файла) при копировании не сохраняются.
# Python 2.7.

import exifread
import shutil
import os
import sys
import subprocess
from datetime import datetime

# Исходные каталоги
sources = [
    '/share/CACHEDEV1_DATA/homes/roman/Camera Uploads',
    '/share/CACHEDEV1_DATA/homes/natalia/Camera Uploads'
    ]

# Каталог назначения
destination = '/share/CACHEDEV1_DATA/Multimedia/Фото/Импорт'

# Типы файлов, которые будут копироваться
file_types = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.mp4', '.MP4', '.mov', '.MOV', '.3gp', '.3GP']

# Лог-файл для хранения имен скопированных файлов
import_log = os.path.join(sys.path[0], 'import.log')

# Лог-файл для записи ошибок
error_log = os.path.join(sys.path[0], 'error.log')

# Добавляет строку в лог-файл.
# Возвращет 0 при успешной записи, 1 - при ошибке.
def write_log(file_name, string):
    try:
        f = open(file_name, 'a')
        f.write(string + '\n')
        f.close()
        return 0
    except Exception as ex:
        print ex
        return 1

# Возвращает дату съемки из EXIF, дату изменения файла если EXIF отсутствует,
# None если не удалось открыть файл.
def get_file_date(file_name):
    try:
        f = open(file_name, 'rb')
        tags = exifread.process_file(f, details=False, stop_tag='DateTimeOriginal')
        f.close()
    except Exception as ex:
        print ex
        return None
    
    if 'EXIF DateTimeOriginal' in tags.keys():
        return datetime.strptime(tags['EXIF DateTimeOriginal'].values, '%Y:%m:%d %H:%M:%S')
    
    return datetime.fromtimestamp(os.path.getmtime(file_name))

# Возвращает полный путь к файлу.
# Имя файла генерируется из даты и расширения.
# Если файл с таким именем существует, к имени добавляется цифра.
def create_file_name(directory, date, extension):
    new_full_name = os.path.join(directory, date.strftime('%Y-%m-%d %H.%M.%S') + extension)
    num = 0
    while True:
        if os.path.isfile(new_full_name):
            num = num + 1
            new_full_name = os.path.join(directory, date.strftime('%Y-%m-%d %H.%M.%S_') + str(num) + extension)
        else:
            return new_full_name

# Возвращает текущие дату и время.
def get_current_date_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Читаем список скопированных ранее файлов
try:
    log_file = open(import_log, 'r')
    imported_files = log_file.readlines()
except:
    imported_files = []

# Для каждого файла в исходных каталогах (не рекурсивно)
for source in sources:
    for item in os.listdir(source):
		# Получаем полный путь к файлу
        full_name = os.path.join(source, item)
		
		# Если это файл
        if os.path.isfile(full_name):
		    # Получаем расширение
            extension = os.path.splitext(item)[1]
            
			# Если расширение входит в список и если файл ранее не копировался 
            if (extension in file_types) and not ((full_name + '\n') in imported_files): 
                # Получаем дату съемки/изменения файла
                file_date = get_file_date(full_name)

                # Если не удалось получить дату, записываем ошибку в лог и переходим к следующему файлу
                if file_date == None:
                    write_log(error_log, get_current_date_time() + ' Ошибка чтения даты ' + full_name)
                    continue
                
                # Генерируем новое имя файла
                new_full_name = create_file_name(destination, file_date, extension)      
                
                # Копируем файл, записываем полный путь к исходному файлу в лог
                try:
                    shutil.copyfile(full_name, new_full_name)
                    write_log(import_log, full_name)
                except Exception as ex:
                    print ex
                    write_log(error_log, get_current_date_time() + ' Ошибка копирования ' + full_name)
