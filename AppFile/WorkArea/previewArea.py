from PySide6.QtWidgets import *
from AppFile.WorkArea.PreviewTab.textEditTab import TextEditTab


class PreviewArea(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.close_tab)

    def close_tab(self, index):
        # Check if changes are saved
        widget = self.widget(index)
        if isinstance(widget, TextEditTab):
            if not widget.changes_saved:
                # Changes are not saved, prompt user
                reply = QMessageBox.question(self, 'Unsaved Changes',
                                             'You have unsaved changes. Do you want to save before closing?',
                                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                             QMessageBox.Save)

                if reply == QMessageBox.Save:
                    # User chose to save changes
                    widget.save_content()
                elif reply == QMessageBox.Cancel:
                    # User chose to cancel closing the tab
                    return

        # Close the tab when the close button is clicked
        self.removeTab(index)