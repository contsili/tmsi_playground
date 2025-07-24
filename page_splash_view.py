from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QIcon
# Import this QtSvg only for correct rendering of the svg images, no need to
# use it.
from PySide6 import QtSvg

from application.Enums.workflow_enums import PageTypeEnum
from application.Views.classes.base_page_view import BasePageView
from application.Views.designer._page_splashUI import Ui_splash_screen

# height of the icon for the animation blocks
ANIMATION_BLOCKS_HEIGHT: int = 164
# width of the icon for the animation blocks
ANIMATION_BLOCKS_WIDTH: int = 20
# interval time in miliseconds
ANIMATION_TIME_INTERVAL: int = 800
# initial index of the icon to display
INITIAL_ANIMATION_INDEX: int = 0
# the increment of the index for the icon
INCREMENT_ANIMATION_INDEX: int = 1
# the path of the images and the order in which they need to be shown
LOADING_IMAGE_PATHS: list[str] = [":/media/loading_highlighted_1",
                                  ":/media/loading_highlighted_2",
                                  ":/media/loading_highlighted_3",
                                  ":/media/loading_highlighted_4",
                                  ":/media/loading_highlighted_5",
                                  ":/media/loading_highlighted_4",
                                  ":/media/loading_highlighted_3",
                                  ":/media/loading_highlighted_2"]


class PageSplashView(BasePageView, Ui_splash_screen):
    """PageSplashView is the View for a page that is displayed upon a task
    running in the background the customer has to wait for.

    The text label can be changed dynamically and can display any text the
    user should be informed of. The dynamic animation starts upon loading the
    page and stops upon leaving the page.

    Attributes
    -----------------------
    timer : QTimer
        The QTimer object that is connected to the function that needs to be
        called once in an interval time
    current_image_index : int
        The index of the current image file path that needs to be displayed in
        the btn_animation_waiting button
    """

    def __init__(self, parent: QWidget = None):
        """ Initialize the PageSplashView

        Set the timer attribute, set the current_image_index attribute and
        connect the timer to the targeted function.

        :param parent: the parent of the view
        :type parent: QWidget
        """
        # Initialize the page
        super().__init__(page_type=PageTypeEnum.PageSplash, parent=parent)
        self.setupUi(self)

        # Define the attributes of this class
        self.timer = QTimer()
        self.current_image_index = INITIAL_ANIMATION_INDEX

        # Perform the setup functions
        self.setup_local_ui_elements()
        self.connect_signals_to_actions()
        self.connect_widgets_to_actions()

        # Connect the timer to its timeout function
        self.timer.timeout.connect(self._loop_shown_icon)

    def setup_local_ui_elements(self):
        """ Setup the UI of the label and button that are displayed on the
        PageSplashView
        """
        # Add the title property to the label
        self.style_class.add_property_to_widget(self.lbl_dynamic_splash,
                                                property="type",
                                                value="splash-title")
        # Set the UI of the animation button
        self.set_ui_btn_animation()

    def connect_widgets_to_actions(self):
        """ Connects widgets defined by the view to the actions that
        they should perform

        This class does not have any widgets that can perform an action.
        """
        pass

    def connect_signals_to_actions(self):
        """ Connects all signals that can be received by this view to
        the actions that they should perform

        This class does not receive any signals.
        """
        pass

    def disconnect_signals_from_actions(self):
        """ Disconnects all signals that can be received by this view
        from the actions that they should perform
        """
        pass

    def close_widget(self):
        """ Functions that need to be called to close the view correctly
        """
        # Perform the leave_page function so that the timer is stopped in case
        # the loop is running
        self.leave_page()

    def set_text_dynamic_label(self, text_to_display: str = None):
        """Set the text of the dynamic label to display the desired text

        :param text_to_display: the text to disply on the label
        :type text_to_display: str
        """
        # if text_to_display is not defined, set empty label
        if text_to_display is None:
            self.lbl_dynamic_splash.setText("")
        # Set the text to the label
        self.lbl_dynamic_splash.setText(text_to_display)

    def load_page(self):
        """Start the interval of the loop_shown_icon function
        """
        self.timer.start(ANIMATION_TIME_INTERVAL)

    def leave_page(self):
        """ Stop the interval of calling the play_icon function and reset the
        image to the first image.
        """
        # Stop the timer
        self.timer.stop()
        # Update the index to the initial index
        self.current_image_index = INITIAL_ANIMATION_INDEX
        # Set the icon of the button animation back to the initial image
        self.set_icon_btn_animation(icon_path=LOADING_IMAGE_PATHS[
            self.current_image_index])

    def on_controller_deleted(self):
        """ The steps that need to be taken when the controller is deleted.

        This view does not have its own controller, so the function can just
        pass.
        """
        pass

    def set_ui_btn_animation(self):
        """ Convert the button into an icon and display the initial image of
        the animation blocks
        """
        # Add the property icon-type to the button
        self.style_class.add_property_to_widget(self.btn_animation_waiting,
                                                property="type",
                                                value="icon")
        # Remove all text from the button
        self.btn_animation_waiting.setText("")
        # Set the icon to the button based on the current image
        self.set_icon_btn_animation(icon_path=LOADING_IMAGE_PATHS[
            self.current_image_index])

    def set_icon_btn_animation(self, icon_path: str):
        """Create a QIcon based on the icon_path and set it to the
        btn_animation_waiting.

        This function creates the QIcon based on the input icon_path, sets it
        to the btn_animation_waiting and sets the correct icon size.

        :param icon_path: path of the icon to display
        :type icon_path: str
        """
        icon = QIcon()
        icon.addFile(icon_path,
                     QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        # Set the icon to the button
        self.btn_animation_waiting.setIcon(icon)
        # Set the size of the icon on the button
        self.btn_animation_waiting.setIconSize(QSize(ANIMATION_BLOCKS_HEIGHT,
                                                     ANIMATION_BLOCKS_WIDTH))

    def _loop_shown_icon(self):
        """ Increments the current_image_index, and adds a new icon to the
        button based on the current_image_index.

        This function is connected to the timer and is called once during the
        animation_time_interval. It loops through all images in the
        LOADING_IMAGE_PATHS list by incrementing the current_image_index. If
        it exceeds the index of the list, it resets the current_image_index to
        the INITIAL_ANIMATION_INDEX. It adds the icon to the button to display
        the new image.
        """
        # Increment the current_image_index to display the next image
        self.current_image_index += INCREMENT_ANIMATION_INDEX

        # Check if the index is still within the list entries, otherwise reset
        # it to the initial index
        if self.current_image_index >= len(LOADING_IMAGE_PATHS):
            self.current_image_index = INITIAL_ANIMATION_INDEX

        # Set the icon to the button based on the path defined by the
        # current_image_index
        self.set_icon_btn_animation(icon_path=LOADING_IMAGE_PATHS[
            self.current_image_index])
