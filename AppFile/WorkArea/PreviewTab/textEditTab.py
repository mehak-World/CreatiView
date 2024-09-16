from PySide6.QtWidgets import *
from PySide6.QtCore import *
import os
import subprocess

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]

class TextEditTab(QWidget):
    def __init__(self, file_path):
        super().__init__()

        self.file_path = file_path
        self.changes_saved = True  # Track whether changes have been saved initially
        hlayout = QHBoxLayout()
        open_in_other_app_btn = QPushButton("Open in third party application")
        add_metaData = QPushButton("Add MetaData")
        add_metaData.clicked.connect(self.addMetaData)
        font_style = QFontComboBox()
        font_style.currentFontChanged.connect(self.change_font_style)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])
        
        self.hide_label = QLabel("Hide MetaData: ")
        self.hide_meta_data = QCheckBox()
        self.hide_meta_data.stateChanged.connect(self.hideMetaData)
        hlayout.addWidget(self.hide_label)
        hlayout.addWidget(self.hide_meta_data)
        hlayout.addWidget(open_in_other_app_btn)
        hlayout.addWidget(add_metaData)
        hlayout.addWidget(font_style)
        hlayout.addWidget(self.fontsize)
        layout = QVBoxLayout(self)
        layout.addLayout(hlayout)
        self.label = QLabel(f"File: {os.path.basename(file_path)}", self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setFocus()
        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_content)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        try:
            with open(file_path, 'r') as file:
                self.text_edit.setPlainText(file.read())
        except Exception as e:
            print(f"Error reading file: {e}")

        self.text_edit.textChanged.connect(self.text_changed)
        open_in_other_app_btn.clicked.connect(self.open_in_other_application)
        self.fontsize.currentIndexChanged[int].connect(self.change_font_size)

        self.hidden = False
        self.enableOrDisable()
        

        #Let us create a variable to store the metadata section:
        self.metadata_section = ''

    def is_metadataAdded(self):
        text = self.text_edit.toPlainText()
        meta_start_index = text.find("#METADATA_START")
        meta_end_index = text.find("#METADATA_END")
        if((meta_start_index != -1 and meta_end_index != -1) or self.hidden == True):
            return True
        else:
            return False
        
    def enableOrDisable(self):
        if(self.is_metadataAdded() == False):
            self.hide_meta_data.setCheckable(False)
        else:
            self.hide_meta_data.setCheckable(True)
        
    def change_font_style(self, font):
        self.text_edit.selectAll()  # Select the entire text content
        self.text_edit.setFont(font)

    def change_font_size(self, index):
        font_size = FONT_SIZES[index]
        self.text_edit.selectAll()
        self.text_edit.setFontPointSize(font_size)

    def keyPressEvent(self, event):
        # Override keyPressEvent to handle keyboard shortcuts
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_S:
            # Ctrl+S pressed
            self.save_content()
        else:
            # Handle other key events
            super().keyPressEvent(event)

    def text_changed(self):
        self.changes_saved = False
        self.update_tab_title()

    def update_tab_title(self):
        tab_widget = self.parentWidget().parentWidget()  # Assuming TextEditTab is nested inside a QTabWidget
        index = tab_widget.indexOf(self)
        if self.changes_saved:
            tab_widget.setTabText(index, f"{os.path.basename(self.file_path)}")
        else:
            tab_widget.setTabText(index, f"*{os.path.basename(self.file_path)}")

    def save_content(self):
        try:
            
            with open(self.file_path, 'w') as file:
                file.write(self.text_edit.toPlainText())
            self.changes_saved = True
            self.update_tab_title()
            self.enableOrDisable()
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Error saving file: {e}")

    def open_in_other_application(self):
        tab_widget = self.parentWidget().parentWidget()  # Assuming TextEditTab is nested inside a QTabWidget
        index = tab_widget.indexOf(self)
        tab_widget.close_tab(index)
        try:
        # Get the path to the system's default application for opening files
            default_app_path = QStandardPaths.standardLocations(QStandardPaths.ApplicationsLocation)[0]
        
        # Construct the command to open the file with the default application
        # Note: On Windows, we use os.startfile() instead of subprocess.Popen() 
        #       as it can handle paths with spaces and special characters better.
            if os.name == 'nt':  # Windows
                os.startfile(self.file_path)
            else:  # Unix-like systems
                subprocess.Popen(["open", self.file_path])
        except Exception as e:
            QMessageBox.warning(self, "Open Error", f"Error opening file: {e}")

    def addMetaData(self):
        
            with open(self.file_path, 'r') as file:
                    content = file.read()

            meta_data = "#METADATA_START------------------------------------------------------------------ \n %Tag: \n\n %Note: \n ------------------------------------------------------------------#METADATA_END\n"
            
            if not (content.startswith("#METADATA_START")):
                new_content = meta_data + content
                try:
                    with open(self.file_path, 'w') as file:
                        file.write(new_content)
                    self.text_edit.setPlainText(new_content)    
                    self.save_content()
                    self.enableOrDisable()
                except Exception as e:
                    QMessageBox.warning(self, "Save Error", f"Error saving file: {e}")

    def hideMetaData(self):
        text = self.text_edit.toPlainText()
        meta_start_index = text.find("#METADATA_START")
        meta_end_index = text.find("#METADATA_END")

        if self.hide_meta_data.isChecked() and meta_start_index != -1 and meta_end_index != -1:
            # Hide metadata
            self.metadata_section = text[meta_start_index:meta_end_index + len("#METADATA_END")]
            text_without_metadata = text.replace(self.metadata_section, "")
            self.text_edit.setPlainText(text_without_metadata)
            self.hidden = True
            self.changes_saved = False  # Metadata is hidden, so changes are not saved
            self.update_tab_title()
        elif not self.hide_meta_data.isChecked() and meta_start_index == -1 and meta_end_index == -1:
            # Show metadata if it's not already present
            self.save_content()
            with open(self.file_path, 'r') as file:
                content = file.read()
                if content.startswith("#METADATA_START"):
                    self.text_edit.setPlainText(content)  
                    self.hidden = False 
                    self.changes_saved = False  # Metadata is shown, so changes are not saved
                    self.update_tab_title()
                else:
                    self.save_content()
                    # Add metadata back
                    new_content = self.metadata_section + content
                    self.text_edit.setPlainText(new_content)
                    self.hidden = False
                    self.changes_saved = False  # Metadata is shown, so changes are not saved
                    self.update_tab_title()

                
            