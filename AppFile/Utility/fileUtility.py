import configparser
import os
import shutil
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from AppFile import singleton
from AppFile.WorkArea.PreviewTab.textEditTab import TextEditTab

CONFIG_FILE_NAME = '.context.ini'


def open_folder():
    main_win = singleton.SingletonMainWin()
    
    file_dialog = QFileDialog()
    path = file_dialog.getExistingDirectory(main_win, 'open directory', QDir.homePath())

    if path:
        if main_win.preview_area:
            main_win.preview_area.clear()
        root_dir = singleton.SingletonRootDir()
        current_dir = singleton.SingletonCurrentDir()

        root_dir.cd(path)
        main_win.delegate_root_dir_changed()
        current_dir.cd(path)


def new_folder():
    main_win = singleton.SingletonMainWin()
    current_dir = singleton.SingletonCurrentDir()
    sys_model = singleton.SingletonSysModel()

    parent_path = current_dir.absolutePath()
    parent_index = sys_model.index(parent_path)

    folder_name, ok = QInputDialog.getText(main_win, "Create folder in %s" % parent_path, "Enter folder name:")

    if ok and folder_name:
        index = sys_model.mkdir(parent_index, folder_name)
        return sys_model.filePath(index)
    else:
        return None


def new_context_folder():
    new_dir = new_folder()
    create_config_file_at_path(new_dir)


def create_config_file_at_path(path, prio=0):
    file_path = os.path.join(path, CONFIG_FILE_NAME)

    config = configparser.ConfigParser()
    config['Context Folder Configuration'] = {
        'priority': str(prio),
        'tags': '',  # comma separated
    }
    with open(file_path, 'w') as file:
        config.write(file)


def is_path_context_folder(path):
    return os.path.exists(os.path.join(path, CONFIG_FILE_NAME))


def new_file():
    main_win = singleton.SingletonMainWin()
    current_dir = singleton.SingletonCurrentDir()

    parent_path = current_dir.absolutePath()

    file_name, ok = QInputDialog.getText(main_win, "Create text file in %s" % parent_path, "Enter file name:")

    if ok and file_name:
        file_name = file_name_in_txt(file_name)
        file_path = os.path.join(parent_path, file_name)
        open(file_path, 'w').close()


def import_dir():
    pass


def rename(current_file_path=None):
    main_win = singleton.SingletonMainWin()

    if current_file_path is None:
        current_dir = singleton.SingletonCurrentDir()
        current_file_path = current_dir.absolutePath()

    new_name, ok = QInputDialog.getText(main_win, "Renaming %s" % current_file_path, "Enter file name:")

    if ok and new_name:
        new_file_path = os.path.join(os.path.dirname(current_file_path), new_name)
        shutil.move(current_file_path, new_file_path)


def remove(current_file_path=None):
    main_win = singleton.SingletonMainWin()
    current_dir = singleton.SingletonCurrentDir()
    sys_model = singleton.SingletonSysModel()

    if current_file_path is None:
        current_file_path = current_dir.absolutePath

    index = sys_model.index(current_file_path)

    if os.path.isdir(current_file_path):
        if os.listdir(current_dir.absolutePath()):
            ok = QMessageBox.warning(main_win, 'Delete non empty directory %s' % current_file_path, 'confirm?', QMessageBox.Yes | QMessageBox.No)
            if ok:
                sys_model.remove(index)
        else:
            ok = QMessageBox.question(main_win, 'Delete empty directory %s' % current_file_path, 'confirm?', QMessageBox.Yes | QMessageBox.No)
            if ok:
                sys_model.rmdir(index)
    else:
        ok = QMessageBox.warning(main_win, 'Delete file at %s' % current_file_path, 'confirm?', QMessageBox.Yes | QMessageBox.No)
        if ok:
            sys_model.remove(index)


def move_to(current_file_path=None):
    main_win = singleton.SingletonMainWin()
    current_dir = singleton.SingletonCurrentDir()

    if current_file_path is None:
        current_file_path = current_dir.absolutePath

    file_dialog = QFileDialog()
    target_path = file_dialog.getExistingDirectory(main_win, 'Destination directory', current_dir.absolutePath())

    if target_path:
        shutil.move(current_file_path, target_path)


def file_name_in_txt(file_name):
    if file_name.endswith('.txt'):
        return file_name
    else:
        return file_name + '.txt'


def open_file(current_file_path):
    main_win = singleton.SingletonMainWin()

    # Safety check, if Preview_Area exist
    if main_win.preview_area:
        preview_area = main_win.preview_area

        if not os.path.isdir(current_file_path):
            if check_file_opened_in_tab(preview_area, current_file_path):
                pass
            else:
                new_tab = TextEditTab(current_file_path)
                preview_area.addTab(new_tab, os.path.basename(current_file_path))
                preview_area.setCurrentWidget(new_tab)


def check_file_opened_in_tab(preview_area, path):
    for index in range(preview_area.count()):
        widget_at_index = preview_area.widget(index)

        if isinstance(widget_at_index, TextEditTab):
            if widget_at_index.file_path == path:
                # File is already open, highlight the existing tab
                preview_area.setCurrentIndex(index)
                return True

    return False
