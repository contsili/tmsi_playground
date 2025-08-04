from PySide6.QtWidgets import (
    QLabel, QSizePolicy, QHBoxLayout, QVBoxLayout, QSpacerItem)
from PySide6.QtCore import Qt
from typing import Dict, List

from application.Views.classes.connection_recorder_info_view import \
    ConnectionRecorderInfoView
from application.Views.designer._sub_page_connection_overviewUI import (
    Ui_sub_page_connection_overview)
from application.Views.classes.base_page_view import BasePageView
from application.Controllers.page_controllers import (
    SubPageConnectionOverviewController)

from application.Enums.sub_page_enums import SubPageTypeEnum
from application.Constants.device_constants import (
    MAX_RECORDERS_PER_BASE_STATION)

# For 1 base station: show recorder 1 and 3 in the left column, 2 and 4 in the
# right column.
UI_ORDER_ONE_BASE_STATION = [1, 3, 2, 4]

# For 2 base stations: first 4 recorders (1–4) from base station 1 go in the
# left column, next 4 recorders (1–4) from base station 2 go in the right
# column.
UI_ORDER_TWO_BASE_STATIONS = [1, 2, 3, 4,
                              1, 2, 3, 4]


class SubPageConnectionOverviewView(BasePageView,
                                    Ui_sub_page_connection_overview):
    """
    Displays the connection overview subpage.

    This class displays the recorder info UI element for all recorders,
    sorted per base station.

    Attributes
    ----------
    overview_devices_dict_extended : Dict[str, List[Dict[str, object]]]
        Maps base station serial numbers to their four recorders.
    num_base_stations : int
        Number of connected base stations.
    recorder_info_ui_elements : Dict[str, ConnectionRecorderInfoView]
        Stores UI elements (i.e. recorder info widgets) for each recorder.
    """

    def __init__(self, parent=None) -> None:
        """
        Initialize the connection overview subpage.

        :param parent: Parent widget
        :type parent: QWidget
        """
        super().__init__(page_type=SubPageTypeEnum.PageConnectionOverview,
                         parent=parent)
        # Set up the UI
        self.setupUi(self)

        # Initialize the controller
        self.controller = SubPageConnectionOverviewController(parent=self)

        # Retrieve the overview_devices_dict_extended from the controller.
        # This dictionary maps base station serial numbers to paired recorders.
        self.overview_devices_dict_extended: Dict[
            str, List[Dict[str, object]]] = (
            self.controller.get_overview_devices_dict_extended()
        )

        # Get the number of base stations that are connected
        self.num_base_stations: int = len(self.overview_devices_dict_extended)

        # Reorder the device dictionary based on UI order constants
        self.overview_devices_dict_extended = (
            self._reorder_overview_devices_dict()
        )

        # This dictionary maps each base station serial number to its UI
        # element.
        self.recorder_info_ui_elements: Dict[str,
                                             ConnectionRecorderInfoView] = {}

        self.setup_local_ui_elements()

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

    def setup_local_ui_elements(self) -> None:
        """
        Set up the UI elements for the connection overview subpage.
        """
        # Header labels for 1 base station
        if self.num_base_stations == 1:
            self.setup_header_single_base_station()
        # Header labels for 2 base stations
        elif self.num_base_stations == 2:
            self.setup_header_two_base_stations()

        # Add recorder info UI elements to the base station they belong
        self.add_recorder_ui_elements_to_their_base_station()

    def setup_header_single_base_station(self) -> None:
        """
        Configure header labels for a single base station.
        """
        # Get the first (and only) base station serial number
        serial_number_base_station1: str = list(
            self.overview_devices_dict_extended.keys())[0]
        # Add header labels for base station
        self._add_base_station_header_labels_to_layout(
            self.tr("Connected to Base Station"), self.tr(
                "Serial number:"), serial_number_base_station1,
            self.layout_bs_header)

    def setup_header_two_base_stations(self) -> None:
        """
        Configure header labels for two base stations.
        """
        # Get the serial numbers of the two base stations
        serial_numbers: List[str] = list(
            self.overview_devices_dict_extended.keys())

        # Add header labels for base station 1
        serial_number_base_station1: str = serial_numbers[0]
        self._add_base_station_header_labels_to_layout(
            self.tr("Base station 1"), self.tr(
                "Serial number:"), serial_number_base_station1,
            self.layout_recorder_ui_dynamic_left)

        # Add header labels for base station 2
        serial_number_base_station2: str = serial_numbers[1]
        self._add_base_station_header_labels_to_layout(
            self.tr("Base station 2"), self.tr(
                "Serial number:"), serial_number_base_station2,
            self.layout_recorder_ui_dynamic_right)

    def add_recorder_ui_elements_to_their_base_station(self) -> None:
        """
        Create and add UI elements for each recorder to their base station.
        """
        # Remove any existing recorder UI elements that are no longer needed
        self._remove_redundant_recorder_ui_elements()

        # Collect all recorder serial numbers
        all_recorders_info: List[str] = self._collect_all_recorders()

        # Collect the newly added recorder serial numbers
        new_serials: set = self._get_new_recorder_serials()

        # Calculate the total number of recorders (i.e. 4 or 8)
        total_number_of_recorders: int = len(all_recorders_info)

        # For each recorder, create a recorder info widget
        for idx_recorder, recorder_info in enumerate(all_recorders_info):

            # Get the serial number of the recorder
            serial_number_recorder: str = recorder_info[
                'serial_number_recorder']

            if serial_number_recorder in new_serials:
                # Get the pairing status of the recorder
                is_paired: bool = recorder_info['is_paired']
                # Get the name of the recorder
                recorder_name: str = self._get_recorder_name(idx_recorder)

                # Create the recorder info widget for this recorder
                recorder_info_widget: ConnectionRecorderInfoView = (
                    self.setup_ui_recorder_info(
                        recorder_name,
                        serial_number_recorder,
                        is_paired)
                )

                # Add the recorder info widget to the appropriate column
                self._add_recorder_widget_to_column(
                    idx_recorder, recorder_info_widget,
                    total_number_of_recorders)

    def setup_ui_recorder_info(self, recorder_name: str, serial_number: str,
                               is_paired: bool) -> ConnectionRecorderInfoView:
        """
        Create and store a recorder info widget for the specified serial
        number.

        :param recorder_name: Name of the recorder
        :type recorder_name: str
        :param serial_number: Serial number of the recorder
        :type serial_number: str
        :param is_paired: Whether the recorder is paired
        :type is_paired: bool
        :return: Recorder info widget
        :rtype: ConnectionRecorderInfoView
        """
        # Create the recorder info widget
        recorder_info_widget: ConnectionRecorderInfoView = (
            ConnectionRecorderInfoView(
                recorder_name=recorder_name,
                serial_number=serial_number,
                is_paired=is_paired,
                parent=self
            )
        )

        # Store the recorder info widget for later access
        self.recorder_info_ui_elements[serial_number] = recorder_info_widget

        return recorder_info_widget

    def connect_signals_to_actions(self) -> None:
        """
        Connect signal handlers to actions.
        """
        # TODO - self.controller.sig_overview_devices_dict_updated.connect(
        #       self.update_overview_devices_dict)
        pass

    def update_overview_devices_dict(self) -> None:
        """
        Handle changes in base stations and their recorders.
        """
        # Get the new overview dict (already reordered if needed)
        self.overview_devices_dict_extended = (
            self.controller.get_overview_devices_dict_extended()
        )
        self.overview_devices_dict_extended = (
            self._reorder_overview_devices_dict(
                self.overview_devices_dict_extended)
        )

        # Add UI elements for new recorders only
        self.add_recorder_ui_elements_to_their_base_station()

    def _reorder_overview_devices_dict(self) -> Dict[str, List[
            Dict[str, object]]]:
        """
        Reorder the overview devices dictionary based on UI order constants.

        :return: Reordered devices dictionary
        :rtype: Dict[str, List[Dict[str, object]]]
        """
        # Get all base station serial numbers
        base_station_serial_numbers: List[str] = list(
            self.overview_devices_dict_extended.keys())
        # Create a new dictionary to hold the reordered devices
        reordered_overview_devices_dict_extended: Dict[str,
                                                       List[Dict[str, object]]
                                                       ] = {}

        # Process each base station
        for bs_index, bs_key in enumerate(base_station_serial_numbers):

            # Get the recorders for this base station
            recorders: List[str] = self.overview_devices_dict_extended[bs_key]
            reordered_recorders: List[str] = []

            if self.num_base_stations == 1:
                # For single base station, use UI_ORDER_ONE_BASE_STATION
                for idx in UI_ORDER_ONE_BASE_STATION:
                    if idx <= len(recorders):
                        reordered_recorders.append(recorders[idx - 1])
            else:
                # For multiple base stations, each base station uses the first
                # 4 indices of UI_ORDER_TWO_BASE_STATIONS
                order_indices: List[int] = UI_ORDER_TWO_BASE_STATIONS[
                    :MAX_RECORDERS_PER_BASE_STATION]
                for idx in order_indices:
                    if idx <= len(recorders):
                        reordered_recorders.append(recorders[idx - 1])

            # Store the reordered recorders in the dictionary for this base
            # station
            reordered_overview_devices_dict_extended[bs_key] = (
                reordered_recorders)

        return reordered_overview_devices_dict_extended

    def _add_base_station_header_labels_to_layout(self, header_text: str,
                                                  serial_label_text: str,
                                                  serial_value_text: str,
                                                  layout: QVBoxLayout) -> None:
        """
        Add header labels for the base station and its serial number.

        :param header_text: Header label text (e.g., "Base station 1")
        :type header_text: str
        :param serial_label_text: Serial label text (e.g., "Serial number:")
        :type serial_label_text: str
        :param serial_value_text: Serial number value (e.g., "SN1-XXXX")
        :type serial_value_text: str
        :param layout: Target layout for the labels
        :type layout: QVBoxLayout
        """
        # Header label
        self.lbl_bs_name: QLabel = QLabel(header_text)
        self.lbl_bs_name.setAlignment(Qt.AlignCenter)
        self.style_class.add_property_to_widget(
            self.lbl_bs_name, "type", "header1")
        self.lbl_bs_name.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum))
        layout.addWidget(self.lbl_bs_name)

        # Add vertical spacer between header and serial number
        spacer_between_header_and_sn: QSpacerItem = QSpacerItem(
            0, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        layout.addItem(spacer_between_header_and_sn)

        # Serial number (text + numerical value)
        self.lbl_serial_number_text: QLabel = QLabel(serial_label_text)
        self.lbl_serial_number_text.setAlignment(Qt.AlignCenter)
        self.lbl_serial_number_text.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))

        self.lbl_serial_number_value: QLabel = QLabel(serial_value_text)
        self.lbl_serial_number_value.setAlignment(Qt.AlignCenter)
        self.lbl_serial_number_value.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))

        layout_bs_serial_number: QHBoxLayout = QHBoxLayout()
        layout_bs_serial_number.setAlignment(Qt.AlignCenter)
        layout_bs_serial_number.addWidget(self.lbl_serial_number_text)
        layout_bs_serial_number.addWidget(self.lbl_serial_number_value)

        # Add serial number text and numerical value next to each other
        layout.addLayout(layout_bs_serial_number)

        # Add vertical spacer after serial number row
        spacer_after_sn: QSpacerItem = QSpacerItem(
            0, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        layout.addItem(spacer_after_sn)

    def _remove_redundant_recorder_ui_elements(self) -> None:
        """
        Remove UI elements (i.e. recorder info widgets)
        for recorders that are no longer present.
        """
        # Collect all serial numbers known to the view and need to get UI
        # elements
        serials_ui_needed: set = set()
        for recorders in self.overview_devices_dict_extended.values():
            for recorder_info in recorders:
                serials_ui_needed.add(recorder_info['serial_number_recorder'])
        # Get serials that already have recorder info widgets
        serials_ui_existing: set = set(self.recorder_info_ui_elements.keys())
        # Find redundant serials that are present in the UI but are no longer
        # needed
        redundant_serials = serials_ui_existing - serials_ui_needed

        # Remove each redundant recorder info widget
        for serial in redundant_serials:
            # Remove the widget from the dictionary
            recorder_info_widget = self.recorder_info_ui_elements.pop(serial)
            # Remove the widget from the layout
            parent_layout = recorder_info_widget.parentWidget().layout()
            parent_layout.removeWidget(recorder_info_widget)
            # Close the widget
            recorder_info_widget.close_widget()
            # Schedule the widget for deletion from the UI
            recorder_info_widget.deleteLater()

    def _collect_all_recorders(self) -> List[Dict[str, object]]:
        """
        Collect recorder info dictionaries for all base stations.
        Info dictionaries contain serial numbers and pairing status.

        :return: List of recorder info dicts
        :rtype: List[Dict[str, object]]
        """
        all_recorders_info: List[Dict[str, object]] = []
        for recorders in self.overview_devices_dict_extended.values():
            all_recorders_info.extend(recorders)
        return all_recorders_info

    def _get_new_recorder_serials(self) -> set:
        """
        Determine which recorder serial numbers are new and need UI elements
        (i.e. recorder info widgets).

        :return: Set of new recorder serial numbers
        :rtype: set
        """
        # Collect all serial numbers known to the view and need to get UI
        # elements
        serials_ui_needed: set = set()
        for recorders in self.overview_devices_dict_extended.values():
            for recorder_info in recorders:
                serials_ui_needed.add(recorder_info['serial_number_recorder'])
        # Get serials that already have recorder info widgets
        serials_ui_existing: set = set(self.recorder_info_ui_elements.keys())
        # Return only the serials that are new (not yet in UI)
        return serials_ui_needed - serials_ui_existing

    def _get_recorder_name(self, idx_recorder: int) -> str:
        """
        Get the display name for a recorder based on its index and number of
        base stations.

        :param idx_recorder: Index of the recorder
        :type idx_recorder: int
        :return: Display name for the recorder
        :rtype: str
        """
        # Use different naming orders depending on number of base stations
        if self.num_base_stations == 1:
            return self.tr(
                f"Recorder {UI_ORDER_ONE_BASE_STATION[idx_recorder]}")
        elif self.num_base_stations == 2:
            return self.tr(
                f"Recorder {UI_ORDER_TWO_BASE_STATIONS[idx_recorder]}")

    def _add_recorder_widget_to_column(
        self, idx_recorder: int,
        recorder_info_widget: ConnectionRecorderInfoView,
        total_number_of_recorders: int
    ) -> None:
        """
        Add the recorder widget to the left or right column and add spacers
        between the widgets. Adds the first half of the recorders (2 or 4
        recorders) to the left column and the second half (2 or 4 recorders)
        to the right column.

        :param idx_recorder: Index of the recorder
        :type idx_recorder: int
        :param total_number_of_recorders: The total number of recorders. It is
                                         4 if one base station is connected,
                                         or 8 if two base stations are
                                         connected.
        :type total_number_of_recorders: int
        """
        # Calculate half of the total number of recorders
        half: int = total_number_of_recorders // 2

        # Place the first half of the recorder in the left column
        if idx_recorder < half:
            self.layout_recorder_ui_dynamic_left.addWidget(
                recorder_info_widget)
            # Add spacer below widget unless it's the last in the column
            if idx_recorder < half - 1:
                spacer: QSpacerItem = QSpacerItem(
                    0, 50, QSizePolicy.Policy.Minimum,
                    QSizePolicy.Policy.Maximum)
                self.layout_recorder_ui_dynamic_left.addItem(spacer)
        else:
            # Place the second half of the recorder in the right column
            self.layout_recorder_ui_dynamic_right.addWidget(
                recorder_info_widget)
            # Add spacer below widget unless it's the last in the column
            if idx_recorder < total_number_of_recorders - 1:
                spacer: QSpacerItem = QSpacerItem(
                    0, 50, QSizePolicy.Policy.Minimum,
                    QSizePolicy.Policy.Maximum)
                self.layout_recorder_ui_dynamic_right.addItem(spacer)

    def on_controller_deleted(self):
        return super().on_controller_deleted()

    def connect_widgets_to_actions(self) -> None:
        """
        Connect widget events to actions.
        """
        pass

    def disconnect_signals_from_actions(self) -> None:
        """
        Disconnect all signal handlers.
        """
        # TODO - self.controller.sig_overview_devices_dict_updated.disconnect(
        #       self.update_overview_devices_dict)
        pass

    def close_widget(self) -> None:
        """
        Clean up resources when widget is closed.
        """
        self.disconnect_signals_from_actions()
