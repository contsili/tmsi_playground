from PySide6.QtWidgets import QStackedWidget

from application.Views.designer._page_connection_mainUI import (
    Ui_page_connection_mainUI)
from application.Views.classes.base_page_view import BasePageView

from application.Controllers.page_controllers import PageConnectionController

from application.Factories.sub_page_view_factory import SubPageViewFactory

from application.Enums.workflow_enums import PageTypeEnum
from application.Enums.sub_page_enums import (SubPageTypeEnum,
                                              SUB_PAGE_MAP)


class PageConnectionView(BasePageView, Ui_page_connection_mainUI):
    """ Page Connection View consists of subpages,
    as defined in SUB_PAGE_MAP, and handles UI switching between the
    subpages. The subpages give the functionality to connect and disconnect
    basestations and recorders to the application.

    Attributes
    ---------------
    connection_pages: dictionary with all (sub)pages (view classes) that
        belong to the connection page.
    """

    def __init__(self):
        """ Initialize the PageConnectionView

        Initialize the super class with the PageTypeEnum.PageConnection as
        pagetype, setup the UI from the Ui_page_connection_mainUI, define
        the attributes of this class, setup the local UI elements and connect
        all signals and widgets to their actions.
        """
        # Initialize super classes and UI
        super().__init__(page_type=PageTypeEnum.PageConnection)
        self.setupUi(self)
        # Define attributes
        self.controller = PageConnectionController(parent=self)
        self.connection_pages: dict[PageTypeEnum, BasePageView] = {}
        # Additional graphics for this view
        self.setup_local_ui_elements()
        # Add widgets and signals to actions
        self.connect_widgets_to_actions()
        self.connect_signals_to_actions()
        # Connect the deleting of the controller to the correct slot
        self.controller.destroyed.connect(self.on_controller_deleted)

    def on_controller_deleted(self):
        """ Define what the view should do if the controller is deleted while
        the view still exists
        """
        super().on_controller_deleted()

    def setup_local_ui_elements(self):
        """ Add the additional UI elements for this view.

        Add the topbar representing the buttons to switch between the
        subpages. Add a stacked widget to the dynamic layout and add the
        subpages to the stacked widget.
        """
        # Define the information about the topbar buttons
        self.topbar_buttons_information = [
            (self.tr("Overview"), SubPageTypeEnum.PageConnectionOverview),
            (self.tr("Base Station"),
             SubPageTypeEnum.PageConnectionBaseStation),
            (self.tr("Recorders"), SubPageTypeEnum.PageConnectionRecorders)
        ]
        # Add stacked widget to the dynamic layout
        self.add_stacked_widget()
        # Add pages to the stacked widget
        self.add_sub_pages_to_stacked_widget()

    def connect_signals_to_actions(self):
        """Connects signals received by the class to their
        respective actions. As this class does not receive signals from
        other classes, it has no signals to connect to, and just
        passes.
        """
        pass

    def connect_sub_page_signals_to_actions(self, page_view: BasePageView):
        """Connects signals of the subpages to the actions needed to performed
        by this view.
        """
        if not isinstance(page_view, BasePageView):
            return None
        page_view.sig_show_splash_screen_requested.connect(
            self.propagate_sig_show_splash_screen_requested)
        page_view.sig_stop_splash_screen_requested.connect(
            self.propagate_sig_stop_splash_screen_requested)

    def disconnect_signals_from_actions(self):
        """Disconnects signals received by the class from their
        respective actions.

        Checks if there are still entries in the connection_pages dict,
        and disconnects the signals of all pages in the dict.
        """
        # If the connection_pages is None, just return
        if self.connection_pages is None:
            return None
        # If the connection_pages has no entries, just return
        if not self.connection_pages:
            return None

        # For every entry in the connection_pages, disconnect the signals if
        # if the entry is of the correct, expected class. If not, just skip
        # that entry
        for page_view in self.connection_pages.values():
            # Check if the page_view is of the expected class, if not just
            # skip this entry
            if not isinstance(page_view, BasePageView):
                break
            # Disconnect the signals from their actions for this entry
            page_view.sig_show_splash_screen_requested.disconnect(
                self.propagate_sig_show_splash_screen_requested)
            page_view.sig_stop_splash_screen_requested.disconnect(
                self.propagate_sig_stop_splash_screen_requested)

    def propagate_sig_show_splash_screen_requested(self, text_to_display: str):
        """ Propagate the sig_show_splash_screen_requested of one of the child
        views by emitting the sig_show_splash_screen_requested of this class.
        Forward the text_to_display.

        :param text_to_display: the text to display on the splash screen
        :type text_to_disply: str
        """
        self.sig_show_splash_screen_requested.emit(text_to_display)

    def propagate_sig_stop_splash_screen_requested(self, page_type=None):
        """ Propagate the sig_stop_splash_screen_requested of one of the child
        views by emitting the sig_stop_splash_screen of this view.

        Does not forward the page_type as we want the end view to display
        this page, not only the sub page.

        :param page_type: page type of the page to be displayed
        :type page_type: PageTypeEnum
        """
        # Ignore the page_type from the subpage, and send current page instead
        self.sig_stop_splash_screen_requested.emit(self.page_type)

    def connect_widgets_to_actions(self):
        """ Connects widgets to their actions.

        TO DO - implement this function later (if needed)
        """
        pass

    def load_page(self):
        """Performs the actions that are needed upon loading the page.

        Sends two signals: sends sig_full_screen_mode_changed(False) to update
        other classes that this page should be displayed in a normal way and
        does not need to be the full window.
        Emits the sig_topbar_update_requested(True, information, current_page)
        to update other classes that a topbar is needed for this page, with
        the information and current page selected as emitted by the signal.
        Emits the sig_visible_frame_update_requested(True) to update other
        classes that the frame around the page needs to be shown.
        """
        self.sig_full_screen_mode_changed.emit(False)
        self.sig_topbar_update_requested.emit(
            True, self.topbar_buttons_information,
            self.stackedWidget.currentWidget().page_type)
        self.sig_visible_frame_update_requested.emit(True)

    def add_stacked_widget(self):
        """ Create a stacked widget and add it to the dynamic layout
        """
        # Create stacked widget
        self.stackedWidget = QStackedWidget(self.frame_page_connection_main)
        self.stackedWidget.setObjectName(u"stackedWidget")
        # Set margins to 0 for alignment
        self.stackedWidget.setContentsMargins(0, 0, 0, 0)
        # Add widget to the intended layout
        self.layout_page_connection_main_dynamic.addWidget(self.stackedWidget)

    def add_sub_pages_to_stacked_widget(self):
        """ Add subpages to the stacked widget and add them to the
        self.connection_pages dictionairy. Shows the overview page.
        """
        # Find the subpages defined for the connection page
        for sub_page_type in SUB_PAGE_MAP[self.page_type]:
            # Check if subpage is not None, and of the correct input type
            if sub_page_type is not None:
                if isinstance(sub_page_type, SubPageTypeEnum):
                    try:
                        # Initialize the view
                        view = SubPageViewFactory.create_view(sub_page_type)
                        # Connect to the signals of this view
                        self.connect_sub_page_signals_to_actions(view)
                        # Add view to the dictionary
                        self.connection_pages[sub_page_type] = view
                        # Add widget to the stacked widget
                        self.stackedWidget.addWidget(view)
                    except Exception:
                        raise Exception(self.tr('Connection sub pages could '
                                                'not be added to stacked '
                                                'widget'))
                else:
                    raise TypeError(self.tr('Received type '
                                            f'{type(sub_page_type)} '
                                            'where SubPageTypeEnum was '
                                            'expected'))
            else:
                # If there are no sub pages defined in SUB_PAGE_MAP
                # for this page type, return empty
                return None

        try:
            # Set the overview page to be the visible page
            if self.connection_pages:
                # Retrieve the widget of the overview subpage
                start_page = self.connection_pages[
                    SubPageTypeEnum.PageConnectionOverview]
                # Show the overview subpage
                self.stackedWidget.setCurrentWidget(start_page)
                # Store the overview subpage as current page to the controller
                self.controller.update_current_sub_page(
                    SubPageTypeEnum.PageConnectionOverview
                )
        except Exception:
            raise Exception(self.tr('Connection Overview subpage could not be '
                                    'set as visible page'))

    def switch_sub_page(self, page: SubPageTypeEnum):
        """ Switch the subpage displayed by the stacked widget

        Switch to a new page as defined by page

        :param page: new page to switch to
        :type page: SubPageTypeEnum
        """
        if page is not None:
            # Check if page is of the correct type
            if isinstance(page, SubPageTypeEnum):
                # TO DO - inform controller current page needs to be closed
                # down
                self.controller.leave_current_sub_page()
                # Load the new page selected by the user
                self.controller.load_sub_page(sub_page_type=page)
                # Get the page to display based on the page input
                page_to_display = self.connection_pages[page]
                if page_to_display is not None:
                    # Let stacked widget display the page_to_display
                    self.stackedWidget.setCurrentWidget(page_to_display)
                else:
                    # Raise error that page_to_display is not defined
                    raise AttributeError(
                        self.tr(f'Sub page {page_to_display} not defined.'))
            else:
                # Raise error that input is of the wrong type
                raise TypeError(self.tr(f'Input page is of type {type(page)} '
                                        'instead of SubPageTypeEnum.'))
        else:
            # Raise error that page is not defined
            raise AttributeError(self.tr('Input is not defined'))

    def close_widget(self):
        """ Performs necessary actions to close down correctly.
        """
        # Disconnect all signals connected to this widget
        self.disconnect_signals_from_actions()
