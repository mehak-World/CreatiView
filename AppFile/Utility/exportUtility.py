import configparser
import os
from typing import Mapping

BRANCH_TAGS = "tags"
FILE_TAGS = "%Tag"
TAG_DELIMINATOR = ","
INI_NAME = ".context.ini"
META_START_SIGNAL = "#METADATA_START"
META_END_SIGNAL = "#METADATA_END"
CONFIG_HEADER = "Context Folder Configuration"
CONFIG_PRIORITY_NAME = "priority"


def get_priority(directory: str) -> int:
    assert os.path.isdir(directory)
    settings_path = os.path.join(directory, INI_NAME)
    if os.path.isfile(settings_path):
        config = configparser.ConfigParser()
        config.read(settings_path)
         
        priority = config[CONFIG_HEADER][CONFIG_PRIORITY_NAME]

        return int(priority)
    else:
        return -1


def get_branch_tags(directory: str) -> list[str]:
    assert os.path.isdir(directory)
    settings_path = os.path.join(directory, INI_NAME)
    if os.path.isfile(settings_path):
        config = configparser.ConfigParser()
        config.read(settings_path)
        tags = config["Context Folder Configuration"][BRANCH_TAGS].split(TAG_DELIMINATOR)
        return list(map(lambda tag: tag.strip("\n "), tags))
    else:
        return None


def get_file_tags(file_path: str) -> list[str]:

    with open(file_path, "r") as f:
        first_line = f.readline().rstrip("\n")
        has_metadata = first_line.strip("- ") == META_START_SIGNAL
        if not has_metadata:
            return []

        tags = []
        while True:
            next_line = f.readline().split(":", 1)
            next_line[0] = next_line[0].strip(" -\n")

            if next_line[0] == META_END_SIGNAL:
                break

            next_data, value = next_line[0], next_line[1]
            if next_data == FILE_TAGS:
                tags = list(map(lambda tag: tag.strip("\n "), value.split(TAG_DELIMINATOR)))
                break

        return tags


def parse_tag_filter(tag_filters: list[str]) -> tuple[list[str], list[str], Mapping[str, str]]:
    file_whitelist = [] # tag : dir/file/all
    dir_whitelist = []
    blacklist = {}

    print(tag_filters)

    for filter_item in tag_filters:
        filter_item = filter_item.strip()
        filter_params = str.split(filter_item, ":")

        if len(filter_params) == 0:
            continue

        if len(filter_params) > 2 and filter_params[2] == "not":
            if filter_params[0] in blacklist:
                blacklist[filter_params[0]] = "all"
            else:
                blacklist[filter_params[0]] = len(filter_params) > 1 and filter_params[1] or "all"

        else:
            filter_object = len(filter_params) > 1 and filter_params[1] or "all"
            if filter_object == "file" or filter_object == "all":
                file_whitelist.append(filter_params[0])
            if filter_object == "dir" or filter_object == "all":
                dir_whitelist.append(filter_params[0])

    return file_whitelist, dir_whitelist, blacklist

def export_file(source_file: str, target_file: str) -> None:
    with open(source_file, "r") as sf, open(target_file, 'a') as tf:
        source_content = sf.read()

        tf.write(f"{source_content}\n")

def _organize_dir_list(dir_list: list[str]) -> list[str]:
    return sorted(dir_list, key=get_priority)


class Exporter:
    def __init__(self, source_dir: str, target_file: str, tag_filter: list[str] = None, include_meta: bool = False):
        """
        :param source_dir: Directory path to export
        :param target_file: File path to export to
        :param tag_filter: List of tags to filter in the form "<tag>:<dir_type>:<not?>"
        :param include_meta: Whether to include metadata in export
        """

        assert os.path.isdir(source_dir)

        self.source_dir = source_dir
        self.target_file = target_file

        self.include_meta = include_meta

        if tag_filter:
            self._file_whitelist, self._dir_whitelist, self._blacklist = parse_tag_filter(tag_filter)
        else:
            self._file_whitelist = []
            self._dir_whitelist = []
            self._blacklist = {}

    def set_tag_filter(self, tag_filter: list[str]) -> None:
        self._file_whitelist, self._dir_whitelist, self._blacklist = parse_tag_filter(tag_filter)

    def export(self) -> None:
        assert os.path.isdir(self.source_dir)

        if os.path.exists(self.target_file) and os.path.isfile(self.target_file):
            os.remove(self.target_file)

        self._export_recursive(self.source_dir)

    def _export_recursive(self, exported_dir: str) -> None:
        child_dirs = list(map((lambda child_dir: os.path.join(exported_dir, child_dir)), os.listdir(exported_dir)))
        file_paths = [path for path in child_dirs if os.path.isfile(path)
                      and path.endswith(".txt") and not self._in_blacklist(path) and self._in_whitelist(path)]
        dir_paths = [path for path in child_dirs if os.path.isdir(path) and get_priority(path) != -1
                     and not self._in_blacklist(path) and self._in_whitelist(path)]

        for file_path in file_paths:
            if os.path.splitext(file_path)[1] == ".txt":
                self._export_file(file_path)

        dir_paths = _organize_dir_list(dir_paths)

        for dir_path in dir_paths:
            child_path = os.path.join(exported_dir, dir_path)
            self._export_recursive(child_path)

    def _export_file(self, source_file: str) -> None:

        with open(source_file, "r") as sf, open(self.target_file, 'a') as tf:
            source_content = sf.read()

            if not self.include_meta and source_content.startswith(META_START_SIGNAL):
                meta_end_index = source_content.find(META_END_SIGNAL)
                source_content = source_content[source_content.find("\n", meta_end_index)+1:]

                tf.write(f"{source_content}\n")

            else:
                tf.write(f"{source_content}\n")

                return 

    def _in_blacklist(self, item_path: str) -> bool:
        
        if os.path.isfile(item_path):
            print(f"————————{item_path}————————")
            for tag in get_file_tags(item_path):
                print(tag)
                if tag in self._blacklist and (self._blacklist[tag] == "file" or self._blacklist[tag] == "all"):
                    return True

            return False

        elif os.path.isdir(item_path):
            for tag in get_branch_tags(item_path):
                if tag in self._blacklist and (self._blacklist[tag] == "dir" or self._blacklist[tag] == "all"):
                    return True

            return False

    def _in_whitelist(self, item_path: str) -> bool:

        if os.path.isfile(item_path):
            if not self._file_whitelist:
                return True
            
            for tag in get_file_tags(item_path):
                if tag in self._file_whitelist:
                    return True

            return False

        elif os.path.isdir(item_path):
            if not self._dir_whitelist:
                return True
            
            for tag in get_branch_tags(item_path):
                if tag in self._dir_whitelist:
                    return True

            return False
        

# export_dir = '/Users/robert/Desktop/UFV/COMP370/Project/Testing_folder'
# target_file_test = '/Users/robert/Desktop/UFV/COMP370/Project/ExportedProject.txt'

# if __name__ == "__main__":

#     file_path = os.path.join(export_dir, "indigo.txt")
#     folder_path = os.path.join(export_dir, "Red")

#     #tag_filter_test = ["stopped", "archived:all:not"]

#     exporter = Exporter(export_dir, target_file_test, include_meta=False)
#     exporter.export()
