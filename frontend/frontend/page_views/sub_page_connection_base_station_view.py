from PySide6.QtWidgets import QWidget
from typing import Dict, List

from application.Views.classes.base_page_view import BasePageView
from application.Views.classes.connection_base_station_info_view import (
    ConnectionBaseStationInfoView)
from application.Views.designer._sub_page_connection_base_stationUI import (
    Ui_sub_page_connection_base_station)
from application.Controllers.page_controllers. \
    sub_page_connection_base_station_controller import (
        SubPageConnectionBaseStationController)

from application.Enums.sub_page_enums import SubPageTypeEnum
from application.Constants.device_constants import MAX_BASE_STATIONS_SUPPORTED





class SubPageConnectionBaseStationView(BasePageView,
                                       Ui_sub_page_connection_base_station):
    """
    View for the Connection Base Station subpage.

    It creates UI elements for each detected base station, providing
    an interface for users to interact with connected base stations.

    Attributes:
        base_station_list_extended : List[Dict[str, str | None | bool]]
            #TODO - docstring explanation
        connection_bs_info_widgets : dict[str, ConnectionBaseStationInfoView]
            Dictionary keeping track of the corresponding
            ConnectionBaseStationInfoView widget to a specific device serial
            number
    Signals:
        None
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        Initialize the subpage for managing base station UI elements.

        :param parent: Parent widget for this view.
        :type parent: QWidget
        """
        super().__init__(page_type=SubPageTypeEnum.PageConnectionBaseStation,
                         parent=parent)

        # Set up the UI from the Qt Designer file
        self.setupUi(self)

        self.controller = SubPageConnectionBaseStationController()

        # Initialize the base_station_list_extended with info from the
        # controller
        self.base_station_list_extended: List[Dict[str, str | None | bool]] = (
            self.controller.get_base_station_list_extended()
        )

        # Initialize the connection_bs_info_widgets dictionary.
        # It maps each base station serial number to its UI element.
        self.connection_bs_info_widgets: Dict[
            str, ConnectionBaseStationInfoView] = {}

        # Create UI elements for each base station and connect actions.
        self.setup_local_ui_elements()

    def setup_local_ui_elements(self) -> None:
        """
        Initialize the base station list and create an empty dictionary to
        store the base station UI elements.
        """
        # Set up the base station UI elements.
        self.add_new_connection_bs_info_widgets()

    def add_new_connection_bs_info_widgets(self) -> None:
        """
        Iterate through the max number of supported base stations, create
        a ConnectionBaseStationInfoView widget for each, and add it to the
        layout. Store each widget for later access.
        """
        for base_station_index in range(MAX_BASE_STATIONS_SUPPORTED):
            # Get the connection status dictionary for the current base station
            base_station_connection_status_dict: Dict[
                str, str | None | bool] = (
                self.base_station_list_extended[base_station_index]
            )

            # Get base station name
            base_station_name: str = self._get_base_station_name(
                base_station_index)
            # Get base station serial number
            base_station_serial_number: str | None = (
                base_station_connection_status_dict[
                    "base_station_serial_number"]
            )
            # Get base station connection status
            is_connected: bool = base_station_connection_status_dict[
                "is_connected"]

            # Create the info widget for this base station.
            connection_bs_info_widget: ConnectionBaseStationInfoView = (
                ConnectionBaseStationInfoView(
                    base_station_name=base_station_name,
                    serial_number=base_station_serial_number,
                    is_connected=is_connected,
                    parent=self
                )
            )

            # Connect the signals of this info view to the corresponding
            # actions
            self.connect_info_signals_to_actions(connection_bs_info_widget)

            # Add the widget to the main horizontal layout.
            self.layout_base_station_ui_elements.addWidget(
                connection_bs_info_widget)

            # For each BS serial number store its UI element
            self.connection_bs_info_widgets[base_station_name] = (
                connection_bs_info_widget)

    def connect_widgets_to_actions(self) -> None:
        """
        Connect all widget signals to their respective actions.
        """
        pass

    def connect_signals_to_actions(self) -> None:
        """
        Connect signal handlers to actions.
        """

    def connect_info_signals_to_actions(
            self, connection_bs_info_widget: ConnectionBaseStationInfoView):
        """ Connect the signals from the ConnectionBaseStationInfoView to their
        actions
        """
        connection_bs_info_widget.sig_discover_started.connect(
            self._on_sig_discover_started)
        connection_bs_info_widget.sig_discover_finished.connect(
            self._on_sig_discover_finished)
        connection_bs_info_widget.sig_connection_finished.connect(
            self._on_sig_connection_finished)
        connection_bs_info_widget.sig_connection_started.connect(
            self._on_sig_connection_started)

    def disconnect_signals_from_actions(self) -> None:
        """
        Disconnect all signal handlers.
        This method is typically called before destroying the widget.
        """
        pass

    def _get_base_station_name(self, base_station_index: int) -> str:
        """
        Get the name of the base station based on its serial number.

        If there is only one base station, returns "Hub Station".
        If there are multiple, returns "Hub Station X" where X is the number
        of the base station.

        :param base_station_serial_number: Serial number of the base station.
        :type base_station_serial_number: str
        :return: Name of the base station.
        :rtype: str
        """
        if MAX_BASE_STATIONS_SUPPORTED == 1:
            # Set the base station name to "Hub Station" if only one
            # base station is supported.
            base_station_name: str = self.tr("Hub Station")
        else:
            # Calculate the 1-based base station number based on its 0-based
            # index.
            base_station_number: int = base_station_index + 1
            # Set the base station name to "Hub Station X" where X is the
            # base station number, if multiple base stations are supported.
            base_station_name: str = self.tr(
                f"Hub Station {base_station_number}")
        return base_station_name

    def _on_sig_discover_started(self):
        """ When discovery of devices has started, start the splash screen
        """
        self._start_splash_screen(
            text_to_display=self.tr("Searching for Hub Stations"))

    def _on_sig_discover_finished(self):
        """ When a signal comes in the discovery is finished, stop the splash
        screen
        """
        self._stop_splash_screen()

    def _on_sig_connection_started(self, serial_number: str):
        """ Start the splash screen with the text connection is starting to
        the device with the serial number

        :param serial_number: the serial number of the device to connect to
        :type serial_number: str
        """
        self._start_splash_screen(text_to_display=self.tr(
            f"Connecting to device {str(serial_number)}"))

    def _on_sig_connection_finished(self):
        """ Stop the splash screen when the connection is finished
        """
        self._stop_splash_screen()

    def _start_splash_screen(self, text_to_display: str):
        """ Request the start of the splash screen and display the text

        :param text_to_display: the text to display on the splash screen
        :type text_to_display: str
        """
        self.sig_show_splash_screen_requested.emit(text_to_display)

    def _stop_splash_screen(self):
        """ Request to stop the splash screen and return to the original page
        """
        # Emit None
        self.sig_stop_splash_screen_requested.emit(None)

    def load_page(self):
        return super().load_page()

    def close_widget(self) -> None:
        """
        Clean up resources when widget is closed.
        """
        self.disconnect_signals_from_actions()

    def on_controller_deleted(self) -> None:
        """
        Handle logic when the controller is deleted.

        This method is called when the controller is no longer needed and
        should clean up resources or connections.
        """
        # TODO - implement this function
        return super().on_controller_deleted()
