from PySide6.QtCore import QSize

from application.Controllers.page_controllers. \
    sub_page_connection_recorder_controller import (
        SubPageConnectionRecorderController)
from application.Views.classes.connection_recorders_pairing_status_view \
    import ConnectionRecordersPairingStatusView
from application.Views.designer._sub_page_connection_recorderUI import (
    Ui_sub_page_connection_recorder
)
from application.Views.designer._discovered_recorderUI import (
    Ui_discovered_recorder
)

from application.Views.classes.base_page_view import BasePageView
from application.Enums.sub_page_enums import SubPageTypeEnum

# UI Constants
BUTTON_MIN_HEIGHT = 40
BUTTON_ICON_SIZE_SAVE = 18
BUTTON_ICON_SIZE_REVERT = 20


class SubPageConnectionRecorderView(BasePageView,
                                    Ui_sub_page_connection_recorder):
    """
    View for the Connection Recorder subpage.

    It provides an interface to pair discovered recorders to the available
    base stations.

    Attributes
    --------
        controller (SubPageConnectionRecorderController): The controller of
                                                          this subpage
        recorder_pairing_status_widgets (dict): Dictionary that maps the
                                                base station serial
                                                numbers to their recorder
                                                pairing status widgets
        discovered_recorder_widgets_dict (dict): Dictionary that maps the
                                                discovered recorder serial
                                                numbers to their widgets

    Signals
    --------
        None
    """

    def __init__(self, parent=None):
        """
        Initialize the subpage connection recorder view.

        :param parent: Parent widget
        :type parent: QWidget
        """
        super().__init__(page_type=SubPageTypeEnum.PageConnectionRecorders,
                         parent=parent)
        # Set up the UI from the designer file
        self.setupUi(self)

        # Instantiate the controller
        self.controller = SubPageConnectionRecorderController()
        # Store widgets for each base station
        self.recorder_pairing_status_widgets = {}

        # Set up the recorder pairing status UI
        self.setup_ui_recorders_pairing_status()

        # Store discovered recorder widgets by serial number
        self.discovered_recorder_widgets_dict = {}

        # Set up local UI elements
        self.setup_local_ui_elements()
        # Connect signals to actions
        self.connect_signals_to_actions()
        # Connect widgets to actions
        self.connect_widgets_to_actions()

    def setup_local_ui_elements(self) -> None:
        """
        Set up local UI elements for the subpage.
        """
        # Apply styling and configure UI elements
        self._setup_frame_styling()
        self._setup_button_styling()
        self._setup_font_styling()
        # Set up discovery info text
        self._setup_discovery_info_text()
        # Set up discover button text
        self._setup_discover_button_text()

    def _setup_frame_styling(self) -> None:
        """
        Apply styling to the frames in the UI.
        """
        # Add shadow to the discovered recorder frame
        self.style_class.add_property_to_widget(
            self.frame_visible_discovered_recorders, "type", "visible-frame")
        self.style_class.add_shadow_frame(
            self, self.frame_visible_discovered_recorders)

    def _setup_button_styling(self) -> None:
        """
        Apply styling and shadows to buttons.
        """
        # Set text for buttons
        self.btn_save.setText(self.tr("\t\tSave"))
        self.btn_save.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.btn_save.setIconSize(QSize(BUTTON_ICON_SIZE_SAVE,
                                        BUTTON_ICON_SIZE_SAVE))

        self.btn_revert_changes.setText(self.tr("\t\tRevert Changes"))
        self.btn_revert_changes.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.btn_revert_changes.setIconSize(QSize(BUTTON_ICON_SIZE_REVERT,
                                                  BUTTON_ICON_SIZE_REVERT))

        # Add shadows to action buttons
        self.style_class.add_shadow_pushbutton(self, self.btn_save)
        self.style_class.add_shadow_pushbutton(self, self.btn_revert_changes)

    def _setup_font_styling(self) -> None:
        """
        Configure fonts for labels and other text elements.
        """
        # Set translated text for main labels
        self.lbl_discovered_recorders.setText(
            self.tr("Discovered Recorders"))

        # Apply title font to section headers
        self.style_class.add_property_to_widget(
            self.lbl_discovered_recorders, "type", "title")

    def _setup_discovery_info_text(self) -> None:
        """
        Set the text describing to the user how to discover recorders.
        """
        self.lbl_user_discovery_info.setText(
            self.tr("Click 'Discover Recorders' to search for available "
                    "devices. When the blue light on the Hub Station blinks, "
                    "it means the discovery is in progress."))
        self.lbl_user_discovery_info.setWordWrap(True)

    def _setup_discover_button_text(self) -> None:
        """
        Set the text for the discover button.
        """
        self.btn_discover_recorders.setText(self.tr("Discover Recorders"))

    def setup_ui_recorders_pairing_status(self) -> None:
        """
        Add the UI elements for all the connected base stations and the
        recorders that the users selected to pair with them.

        This method creates a ConnectionRecordersPairingStatusView for
        each connected base station.

        """
        # Get base station information and pairing data from controller
        bs_to_recorders_dict = (
            self.controller.return_bs_to_recorders_dict())
        bs_to_recorders_dict = {
            "BS12345": ["REC001", "REC002"],
            "BS67890": ["REC003"]
        }
        # For each base station, create a widget
        for base_station_serial_number, recorder_pairing_list in (
                bs_to_recorders_dict.items()):
            self._create_recorders_pairing_status_widget(
                base_station_serial_number=base_station_serial_number,
                paired_recorders_list=recorder_pairing_list
            )

    def connect_signals_to_actions(self) -> None:
        """
        Connect signals to their corresponding actions.
        """
        # Connect the signals from the controller to the view when a BS is
        # connected or disconnected while the workflow is already selected
        self.controller.sig_base_station_connected.connect(
            self.on_base_station_connected)
        self.controller.sig_base_station_disconnected.connect(
            self.on_base_station_disconnected)

        # Connect the signals related to newly discovered recorder
        self.controller.sig_new_recorders_discovered.connect(
            self.on_new_recorder_discovered)
        self.controller.sig_recorder_moved_to_base_station.connect(
            self.add_selected_recorder_to_pairing_status_widget)

    def connect_recorder_pairing_status_widget_signals(
        self,
        recorder_pairing_status_widget: ConnectionRecordersPairingStatusView
    ) -> None:
        """
        Connect signals of the widget that shows the recorders paired to a
        specific base station.

        :param recorder_pairing_status_widget: The recorder pairing status
                                       widget to connect signals to
        :type recorder_pairing_status_widget:
                                          ConnectionRecordersPairingStatusView
        """
        (
            recorder_pairing_status_widget.sig_recorder_moved_in_pairing_list.
            connect(self.notify_controller_to_reorder_selected_recorder)
        )
        (
            recorder_pairing_status_widget.
            sig_recorder_removed_from_pairing_list.
            connect(self.notify_controller_to_remove_selected_recorder)
        )

    def connect_widgets_to_actions(self) -> None:
        """
        Connect widgets to their corresponding actions.
        """
        # Connect the save button to the controller save function
        # Connect the revert button to the controller revert function
        pass

    def on_base_station_connected(self, base_station_serial_number: str,
                                  paired_recorders_list: list) -> None:
        """
        Create the UI element for the connected base station and its paired
        recorders.

        :param base_station_serial_number: Serial number of the connected base
                                           station
        :type base_station_serial_number: str
        :param paired_recorders_list: List of recorders paired with this base
                                      station
        :type paired_recorders_list: list
        """
        self._create_recorders_pairing_status_widget(
            base_station_serial_number=base_station_serial_number,
            paired_recorders_list=paired_recorders_list
        )

    def on_base_station_disconnected(self,
                                     base_station_serial_number: str) -> None:
        """
        Remove the UI element for the disconnected base station

        :param base_station_serial_number: Serial number of the disconnected
                                           base station
        :type base_station_serial_number: str
        """
        # TODO - Remove the UI element for the disconnected base station
        # if base_station_serial_number in (
        # self.recorder_pairing_status_widgets):
        #     # Get the widget for this base station
        #     recorder_pairing_status_widget = (
        #       self.recorder_pairing_status_widgets[
        #       base_station_serial_number])
        #     # Disconnect signals for this widget
        #     # self.disconnect_recorder_pairing_status_widget_signals(
        #           recorder_pairing_status_widget)
        #     # Remove from layout
        #     # recorder_pairing_status_widget.setParent(None)
        #     # Delete the widget
        #     # recorder_pairing_status_widget.deleteLater()
        #     # Remove from dictionary
        #     # del self.recorder_pairing_status_widgets[
        # base_station_serial_number]

    def notify_controller_to_reorder_selected_recorder(
            self, base_station_serial_number: str, recorder_serial_number: str,
            new_position_in_pairing_list: int
    ) -> None:
        """
        Notify the controller to reorder the bs_to_user_selected_recorders_dict
        list

        :param base_station_serial_number: Serial number of the base station
        :type base_station_serial_number: str
        :param recorder_serial_number: Serial number of the recorder that was
                                       moved
        :type recorder_serial_number: str
        :param new_position_in_pairing_list: The new position that the recorder
                                             has in the list of recorders
                                             selected for pairing.
        :type new_position_in_pairing_list: int
        """
        # run something like:
        # self.controller.reorder_selected_recorder()

    def notify_controller_to_remove_selected_recorder(
            self, base_station_serial_number: str,
            recorder_serial_number: str) -> None:
        """
        Notify the controller to remove the selected recorder from
        bs_to_user_selected_recorders_dict and add it to
        discovered_and_unselected_recorders

        :param base_station_serial_number: Serial number of the base station
        :type base_station_serial_number: str
        :param recorder_serial_number: Serial number of the recorder that was
                                       removed
        :type recorder_serial_number: str
        """
        # run something like:
        # self.controller.unselect_recorder_and_restore_to_discovered()

    def on_new_recorder_discovered(self, recorder_serial_numbers_list: str
                                   ) -> None:
        """
        Create and display widgets for each discovered recorder.

        This function calls the helper function
        _setup_discovered_recorder_widget to create and display widgets
        for each discovered recorder that is in the
        recorder_serial_numbers_list.

        :param recorder_serial_numbers_list: List of discovered recorder serial
                                             numbers
        :type recorder_serial_numbers_list: list(str)
        """
        # Create widgets for each discovered recorder
        for recorder_serial_number in recorder_serial_numbers_list:
            self._setup_discovered_recorder_widget(recorder_serial_number)

    def add_selected_recorder_to_pairing_status_widget(
            self, base_station_serial_number: str,
            recorder_serial_number: str) -> None:
        """
        Add a user-selected recorder to the pairing status widget of a
        specific base station.

        :param base_station_serial_number: Serial number of the base station
        :type base_station_serial_number: str
        :param recorder_serial_number: Serial number of the paired recorder
        :type recorder_serial_number: str
        """
        # Remove the discovered recorder widget from the UI and the
        # dictionary
        self._remove_discovered_recorder_widget(
            recorder_serial_number)

        # Find the recorder pairing status widget based on the base station
        # serial number
        pairing_status_widget = self.recorder_pairing_status_widgets[
            base_station_serial_number]
        # Add the user selected recorder to the pairing status widget
        pairing_status_widget.add_selected_recorder_to_pairing_status_widget(
            recorder_serial_number)

    def disconnect_signals_from_actions(self) -> None:
        """
        Disconnect signals from their corresponding actions.
        """
        # Disconnect the signals from the controller to the view when a BS is
        # connected or disconnected while the workflow is already selected
        self.controller.sig_base_station_connected.disconnect(
            self.on_base_station_connected)
        self.controller.sig_base_station_disconnected.disconnect(
            self.on_base_station_disconnected)

        # Disconnect the signals related to newly discovered recorder
        self.controller.sig_new_recorders_discovered.disconnect(
            self.on_new_recorder_discovered)
        self.controller.sig_recorder_moved_to_base_station.disconnect(
            self.add_selected_recorder_to_pairing_status_widget)

    def disconnect_recorder_pairing_status_widget_signals(
        self,
        recorder_pairing_status_widget: ConnectionRecordersPairingStatusView
    ) -> None:
        """
        Disconnect signals of the widget that shows the recorders paired to a
        specific base station.

        :param recorder_pairing_status_widget: The recorder pairing status
                                               widget to disconnect signals
                                               from
        :type recorder_pairing_status_widget:
                                        ConnectionRecordersPairingStatusView
        """
        (
            recorder_pairing_status_widget.sig_recorder_moved_in_pairing_list.
            disconnect(self.notify_controller_to_reorder_selected_recorder)
        )
        (
            recorder_pairing_status_widget.
            sig_recorder_removed_from_pairing_list.
            disconnect(self.notify_controller_to_remove_selected_recorder)
        )

    def load_page(self) -> None:
        """
        Load the page and initialize any required data or UI elements.
        """
        pass

    def on_controller_deleted(self) -> None:
        """
        Handle cleanup when the controller is deleted.
        """
        return super().on_controller_deleted()

    def close_widget(self) -> None:
        """
        Close the widget and perform any necessary cleanup.
        """
        self.disconnect_signals_from_actions()

    def _create_recorders_pairing_status_widget(
            self, base_station_serial_number: str, paired_recorders_list: list
    ) -> ConnectionRecordersPairingStatusView:
        """
        Helper method to create a widget that includes that recorders paired
        to a specific base station

        :param base_station_serial_number: Serial number of the base station
        :type base_station_serial_number: str
        :param paired_recorders_list: List of recorders paired with this base
                                      station
        :type paired_recorders_list: list
        :return: The widget with the recorders paired to the base station
        :rtype: ConnectionRecordersPairingStatusView
        """
        # Get the appropriate name for this base station
        base_station_name = self._get_base_station_name(
            base_station_serial_number)

        # Create the widget for this base station
        recorder_pairing_status_widget = ConnectionRecordersPairingStatusView(
            base_station_name=base_station_name,
            base_station_serial_number=base_station_serial_number,
            recorder_pairing_list=paired_recorders_list
        )

        # Connect signals for this widget
        self.connect_recorder_pairing_status_widget_signals(
            recorder_pairing_status_widget)

        # Add the widget to the appropriate container in the layout
        self.layout_base_station_dynamic.addWidget(
            recorder_pairing_status_widget)

        # Store the widget in the dictionary using the serial number as key
        self.recorder_pairing_status_widgets[base_station_serial_number] = (
            recorder_pairing_status_widget)

        return recorder_pairing_status_widget

    def _get_base_station_name(self,
                               base_station_serial_number: str) -> str:
        """
        Helper method to determine the appropriate display name for a base
        station based on how many are connected.

        :param base_station_serial_number: Serial number of the base station
        :type base_station_serial_number: str
        :return: Base station name
        :rtype: str
        """
        # Get all base station information to determine naming
        bs_to_recorders_dict = (
            self.controller.return_bs_to_recorders_dict()
        )
        bs_to_recorders_dict = {
            "BS12345": ["REC001", "REC002"],
            "BS67890": ["REC003"]
        }
        total_base_stations = len(bs_to_recorders_dict)

        # Determine the appropriate base station name
        if total_base_stations == 1:
            return self.tr("Hub Station")
        else:
            # Get index of current base station
            index = list(bs_to_recorders_dict.keys()
                         ).index(base_station_serial_number)
            # Use 1-based numbering for multiple base stations
            base_station_number = index + 1

            return self.tr(f"Hub Station {base_station_number}")

    def _setup_discovered_recorder_widget(self,
                                          recorder_serial_number: str) -> None:
        """
        Create and add a discovered recorder widget to the subpage.

        :param recorder_serial_number: Serial number of the discovered recorder
        :type recorder_serial_number: str
        """
        # Instantiate the Ui_discovered_recorder from the designer file
        discovered_recorder_widget = Ui_discovered_recorder()
        # Add the recorder serial number to the label
        (
            discovered_recorder_widget.
            lbl_discovered_recorder_serial_number.setText(
                recorder_serial_number)
        )
        # Configure the buttons
        discovered_recorder_widget.btn_pair_recorder_to_first_bs.setText("+")
        discovered_recorder_widget.btn_pair_recorder_to_second_bs.setVisible(
            False)
        # TODO - Add gray background to the frame_main_content

        # Display the discovered recorder widget in the subpage
        self.listView_discovered_recorders.addItem(discovered_recorder_widget)

        # Store the discovered recorder widget in a dictionary
        self.discovered_recorder_widgets_dict[recorder_serial_number] = (
            discovered_recorder_widget)

        # Connect buttons to actions
        self._connect_discovered_recorder_buttons(discovered_recorder_widget)

    def _connect_discovered_recorder_buttons(
            self, discovered_recorder_widget: Ui_discovered_recorder) -> None:
        """
        Connect the buttons of a discovered recorder widget to its actions.

        This method connects the button that pairs the discovered recorder to
        the appropriate base station.

        :param discovered_recorder_widget: The discovered recorder widget
        :type discovered_recorder_widget: Ui_discovered_recorder
        """
        # Get the recorder serial number from the widget
        recorder_serial_number = (
            discovered_recorder_widget.
            lbl_discovered_recorder_serial_number.text()
        )

        # Connect the button that pairs the discovered recorder to the first
        # base station
        (
            discovered_recorder_widget.btn_pair_recorder_to_first_bs.clicked.
            connect(lambda: self._pair_recorder_to_first_bs(
                recorder_serial_number))
        )

        # TODO - In the future a second button can be implemented to pair
        # the discovered recorder to a second base station:
        # discovered_recorder_widget.btn_pair_recorder_to_second_bs.
        #   clicked.connect(lambda: self._pair_recorder_to_second_bs(
        #       recorder_serial_number))

    def _pair_recorder_to_first_bs(
            self, recorder_serial_number: str) -> None:
        """
        Pair the discovered recorder to the first available base station.

        :param recorder_serial_number: Serial number of the discovered recorder
        :type recorder_serial_number: str
        """
        # Get available base stations
        base_station_serials = list(
            self.controller.return_bs_to_recorders_dict().keys())
        bs_to_recorders_dict = {
            "BS12345": ["REC001", "REC002"],
            "BS67890": ["REC003"]
        }
        base_station_serials = list(
            bs_to_recorders_dict.keys())
        # Use the first base station
        base_station_serial_number = base_station_serials[0]

        # Inform the controller to mark the recorder as selected to pair
        self.controller.mark_recorder_as_selected_to_pair(
            base_station_serial_number, recorder_serial_number)

    def _remove_discovered_recorder_widget(
            self, recorder_serial_number: str) -> None:
        """
        Remove the discovered recorder widget from the UI and the
        dictionary.

        :param recorder_serial_number: Serial number of the discovered recorder
        :type recorder_serial_number: str
        """
        # Get the discovered recorder widget from the dictionary
        discovered_recorder_widget = self.discovered_recorder_widgets_dict[
            recorder_serial_number]

        # Remove the discovered recorder widget from the UI
        self.listView_discovered_recorders.removeItemWidget(
            discovered_recorder_widget)

        # Remove the widget from the dictionary
        del self.discovered_recorder_widgets_dict[recorder_serial_number]
