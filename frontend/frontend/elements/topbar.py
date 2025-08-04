from functools import partial
from PySide6.QtWidgets import (QWidget, QPushButton, QHBoxLayout,
                               QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal

from application.Enums.sub_page_enums import SubPageTypeEnum
from application.Styling.general_style_elements import GeneralStyleElements

# Define the default spacer width between buttons in the topbar
DEFAULT_SPACER_WIDTH = 60
SPACER_HEIGHT = 1


class TopBar(QWidget):
    """
    A dynamic top bar containing centered buttons. Information can be provided
    about the text the buttons should display, the number of buttons, the
    style of the buttons and the distance between the buttons.

    Signals
    ---------------
    sig_topbar_button_clicked : Signal(SubPageTypeEnum)
        Emits the SubPageTypeEnum that is related to the button that was
        clicked.
    """
    sig_topbar_button_clicked = Signal(SubPageTypeEnum)

    def __init__(self, parent: QWidget, buttons_data: list,
                 style_type: str = None,
                 spacer_width: int = DEFAULT_SPACER_WIDTH):
        """Initializes the topbar class and its elements.

        The number of buttons, their text, and their type (`SubPageTypeEnum`)
        can be dynamically set upon initialization.
        Buttons are automatically spaced with a specified spacer between them.
        If no spacer_width is specified, defaults to 60px.

        :param parent: The parent QWidget.
        :type parent: QWidget
        :param style_type: The style of the buttons in the topbar. Should be
            similar to a type option in the stylesheet
        :type style_type: str
        :param buttons_data: A list of tuples containing button text and a
                            `SubPageTypeEnum`.
        :type buttons_data: list[tuple[str, SubPageTypeEnum]]
        :param spacer_width: width of the spacer between the buttons, defaults
                                to 60 px
        :type spacer_width: int
        """
        super().__init__(parent)
        self.style_class = GeneralStyleElements()
        self.layout = QHBoxLayout(self)
        # Set margins and spacing to 0
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Store button references
        self.buttons = []

        # Add Buttons with Spacers
        for i, (text, btn_type) in enumerate(buttons_data):
            # Make button and set text based on input
            button = QPushButton(text)
            # Add the SubPageType property
            button.setProperty("SubPageTypeEnum", btn_type)
            button.clicked.connect(partial(self.on_btn_click,
                                           btn_type=btn_type))
            # Add the style to the button
            self.style_class.add_property_to_widget(button, "type",
                                                    style_type)
            # Add the button to the layout
            self.layout.addWidget(button)
            # Store reference
            self.buttons.append(button)

            # Spacer after each button except the last one
            if i < len(buttons_data) - 1:
                self.layout.addItem(QSpacerItem(
                    spacer_width, SPACER_HEIGHT, QSizePolicy.Policy.Fixed,
                    QSizePolicy.Policy.Minimum))

    def get_buttons_by_type(self, btn_type):
        """
        Get all buttons of a specific `SubPageTypeEnum`.

        :param btn_type: The `SubPageTypeEnum` value to filter buttons.
        :type btn_type: SubPageTypeEnum
        :return: A list of QPushButton instances with the given
                `SubPageTypeEnum`.
        :rtype: list[QPushButton]
        """
        return [btn for btn in self.buttons
                if btn.property("SubPageTypeEnum") == btn_type]

    def on_btn_click(self, btn_type):
        """ Emit a signal with the btn_type as output that a button has been
        clicked. Set the button to active UI state.

        :param btn_type: type of the button that has been clicked
        :type btn_type: SubPageTypeEnum
        """
        self.sig_topbar_button_clicked.emit(btn_type)
        self.set_btn_type_active(btn_type=btn_type)

    def set_btn_type_active(self, btn_type):
        """ Set the button of btn_type active for the user. This style
        should be defined in the stylesheet. Set the state of the other buttons
        to none so it does not appear to be active.

        :param btn_type: The `SubPageTypeEnum` type of the button that
            should be displayed as active
        :type btn_type: SubPageTypeEnum
        """
        # First de-activate all buttons
        for btn in self.buttons:
            btn.setProperty("state", "none")
            btn.setStyleSheet(self.style_class.get_style_sheet())
        # Get the button that corresponds to btn_type
        button = self.get_buttons_by_type(btn_type=btn_type)[0]
        # Make the button look active
        self.style_class.add_property_to_widget(button, "state", "active")
