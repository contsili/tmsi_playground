from functools import partial

from PySide6.QtWidgets import QFileDialog

from application.Enums.workflow_enums import PageTypeEnum
from application.Views.designer._file_management_pageUI import (
    Ui_file_management_page)
from application.Views.classes.base_page_view import BasePageView

from application.Controllers.page_controllers.page_file_management_controller \
    import PageFileManagementController


class PageFileManagementView(BasePageView, Ui_file_management_page):
    """
    View class for the File Management page.

    This class displays file management functionality allowing users
    to browse, select, and manipulate files within the application.

    Attributes:
        - page_widget: The widget that contains the file management UI elements
    """

    def __init__(self, parent=None):
        """
        Initialize the PageFileManagementView.

        :param parent: Optional parent widget
        :type parent: QWidget, optional
        """
        super().__init__(
            page_type=PageTypeEnum.PageFileManagement,
            parent=parent
        )
        self.setupUi(self)
        # Define attributes
        self.controller = PageFileManagementController(parent=self)

        # Perform additional setup
        self.setup_local_ui_elements()
        self.connect_widgets_to_actions()
        self.connect_signals_to_actions()
        # Connect the deleting of the controller to the correct slot
        self.controller.destroyed.connect(self.on_controller_deleted)

    def load_page(self):
        """Performs the actions that are needed upon loading the page.

        Sends two signals: sends sig_full_screen_mode_changed(False) to update
        other classes that this page does not need to be displayed in full
        window mode but can be displayed in the normal way.
        Emits the sig_topbar_update_requested(False, None, None) to update
        other classes that no topbar is needed for this page view.
        Emits the sig_visible_frame_update_requested(True) to update other
        classes that the frame around the page needs to be shown.
        """
        self.sig_full_screen_mode_changed.emit(False)
        self.sig_topbar_update_requested.emit(False, None, None)
        self.sig_visible_frame_update_requested.emit(True)

    def on_controller_deleted(self):
        """ Define what the view should do if the controller is deleted while
        the view still exists
        """
        super().on_controller_deleted()

    def setup_local_ui_elements(self):
        """
        Set up the file management page UI elements.
        """
        self._setup_ui_elements_folder_information()
        self._setup_ui_elements_file_information()
        self._setup_ui_elements_automatic_save()

    def connect_widgets_to_actions(self):
        """
        Connect UI elements to their respective actions.
        """
        # Connect the browse button to the select_and_display_folder method
        self.btn_browse_folder.clicked.connect(
            self.select_and_display_folder
        )

        # Connect the filename line edit to the filename_editing_finished
        # method
        self.le_filename.editingFinished.connect(
            self.filename_editing_finished
        )

        # Connect the fileformat combo box to the file_format_selected
        # method
        self.cb_fileformat.activated.connect(
            self.file_format_selected
        )

        # Connect buttons to controller for toggling automatic/manual save mode
        self.btn_automatic_save.clicked.connect(
            partial(self.toggle_save_mode, is_automatic=True))
        self.btn_manual_save.clicked.connect(
            partial(self.toggle_save_mode, is_automatic=False))
        
        # Connect the controller's signals to the view's slots
        self.controller.sig_folder_changed.connect(
            self.le_current_folder.setText
        )
        
    def connect_signals_to_actions(self):
        """
        Connect signals received by this view to their corresponding actions.
        """
        pass

    def _setup_ui_elements_folder_information(self):
        """
        Set up the UI elements for folder information.

        """
        self.lbl_folder_info_title.setText(
            self.tr("Folder Information"))
        self.lbl_current_folder.setText(
            self.tr("Current storage folder:"))

        # Initialize the current folder display with the actual current folder
        current_folder = self.controller.get_current_folder()
        self.le_current_folder.setText(current_folder)
        self.btn_browse_folder.setText(self.tr("Browse"))

    def _setup_ui_elements_file_information(self):
        """
        Set up the UI elements for file information.
        """
        self._setup_ui_elements_file_name()
        self._setup_ui_elements_file_format()

    def _setup_ui_elements_file_name(self):
        """
        Set up the UI elements for file name.
        """
        self.lbl_file_info_title.setText(self.tr("File Information"))
        self.lbl_filename.setText(self.tr("File name:"))
        filename = self.controller.get_filename()
        self.le_filename.setText(filename)
        self.btn_filename_saved.setText(self.tr("Not Saved"))

    def _setup_ui_elements_file_format(self):
        """
        Set up the UI elements for file format.
        """
        self.lbl_fileformat.setText(self.tr("File format:"))
        self.btn_fileformat_saved.setText(self.tr("Not Saved"))
        self._setup_ui_elements_file_format_combobox()

    def _setup_ui_elements_file_format_combobox(self):
        """
        Set up the file format combo box with available formats.
        """
        # Clear the default already existing items from Qt Designer
        self.cb_fileformat.clear()

        # Add formats from the model
        file_formats = self.controller.get_supported_file_formats()
        for format_name in file_formats:
            self.cb_fileformat.addItem(
                format_name.value, format_name.value)
        # Set the current format to the frst element from the list of formats
        current_file_format = self.controller.get_current_file_format()
        index = self.cb_fileformat.findText(current_file_format)
        if index != -1:
            self.cb_fileformat.setCurrentIndex(index)
        else:
            print("Warning: The file format you are trying to add does "
                  "not belong the list of available file formats.")
        # TODO - change the default file format once the spire file format
        # is decided

    def _setup_ui_elements_automatic_save(self):
        """
        Set up the UI elements for automatic save options.
        """
        # Setup automatic/manual saving UI elements
        self.lbl_auto_save_title.setText(self.tr("Automatic Saving"))
        self.lbl_config_auto_save.setText(
            self.tr("Upon entering the acquisition page, start saving to file")
        )

        self.btn_automatic_save.setText(self.tr("Automatically"))
        self.btn_manual_save.setText(self.tr("Manually"))

        # Make the buttons checkable
        self.btn_automatic_save.setCheckable(True)
        self.btn_manual_save.setCheckable(True)

        # TODO - toggling method might change in the future (i.e. we might not
        # use buttons)
        is_automatic_save_enabled = (
            self.controller.get_automatic_save_enabled()
        )
        self.toggle_save_mode(is_automatic_save_enabled)

    def select_and_display_folder(self):
        """
        Open a file dialog to select a folder and display the selected folder
        in the UI.

        :param folder_path: The path of the selected folder
        :type folder_path: str
        """
        folder_path = QFileDialog.getExistingDirectory(
            parent=None,
            caption=self.tr("Select current storage folder"),
            dir=self.controller.get_current_folder()
        )

        # Only proceed if a folder was actually selected (not cancelled)
        if folder_path:
            self.le_current_folder.setText(folder_path)
            self.controller.set_current_folder(folder_path)
        else:
            # If no folder was selected, just keep the previously selected one
            pass

    def filename_editing_finished(self):
        """
        This function is called when the user finishes editing the filename.

        It give feedback to the user that the filename has been saved
        and passes the new filename to the controller.
        """
        # Update UI to indicate the filename has been saved
        self.btn_filename_saved.setText(self.tr("Saved"))
        # TODO - Replace with green checkmark icon for better visual feedback
        # (no need to add the word "Saved"). Also we want the checkmark to
        # appear each time the user selects a new file format. That can happen
        # many times before starting the recording.

        # Get the filename from the line edit
        filename = self.le_filename.text()
        # Update the controller with the new filename
        self.controller.set_filename(filename)

    def file_format_selected(self):
        """
        This function is called when the user selects a file format.

        It give feedback to the user that the file format has been saved and
        it passes the selected file format to the controller.
        """

        # Update UI to indicate the file format has been saved
        self.btn_fileformat_saved.setText(self.tr("Saved"))
        # TODO - Replace with green checkmark icon for better visual feedback
        # (no need to add the word "Saved"). Also we want the checkmark to
        # appear each time the user selects a new file format. That can happen
        # many times before starting the recording.

        # Get the selected file format from the combo box
        file_format = self.cb_fileformat.currentText()
        # Update the controller with the selected file format
        self.controller.set_current_file_format(file_format)

    def toggle_save_mode(self, is_automatic):
        """
        Toggle between automatic and manual save modes

        :param is_automatic: Whether to set automatic save mode (True) or
        manual (False)
        :type is_automatic: bool
        """
        # Update button states
        if is_automatic:
            self.btn_automatic_save.setProperty("state", "active")
            self.btn_manual_save.setProperty("state", "none")
        else:
            self.btn_automatic_save.setProperty("state", "none")
            self.btn_manual_save.setProperty("state", "active")

        style_sheet = self.style_class.get_style_sheet()
        self.btn_automatic_save.setStyleSheet(style_sheet)
        self.btn_manual_save.setStyleSheet(style_sheet)

        # Update the controller with the new setting
        self.controller.set_automatic_save_enabled(is_automatic)

    def disconnect_signals_from_actions(self):
        """
        Disconnect all signals when the view is being closed.
        """
        pass

    def close_widget(self):
        """
        Perform necessary actions to cleanly close the widget.
        """
        self.disconnect_signals_from_actions()
