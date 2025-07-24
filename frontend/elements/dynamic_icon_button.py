from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QEvent, Property, QObject
from PySide6.QtGui import QIcon, QPixmap


class DynamicIconButton(QPushButton):
    """
    A QPushButton subclass that supports separate icons for enabled, hover,
    and disabled states, settable via Qt Designer using custom properties.

    This allows icon state transitions without relying on QSS.

    :param parent: The parent widget, typically set by Qt Designer.
    :type parent: QWidget
    """

    def __init__(self, parent=None):
        """
        Initializes the DynamicIconButton instance with event filtering and
        empty icon paths.

        :param parent: Optional parent widget.
        :type parent: QWidget or None
        """
        super().__init__(parent)

        # Internal dictionary to store paths for different icon states
        self._icon_paths = {"enabled": "", "hover": "", "disabled": ""}

        # QIcon instance used for default state (enabled + disabled)
        self._icon = QIcon()

        # Track whether the mouse is currently hovering over the button
        self._is_hovering = False

        # Install event filter to detect hover events
        self.installEventFilter(self)

    def _set_enabled_or_disabled_icon(self):
        """ Updates the QIcon instance with the appropriate icons for
        disabled and enabled states using SVG (or any scalable format) paths.

        This method ensures that:
        - The enabled icon is always used for the default (enabled) state.
        - The disabled icon is used if available; otherwise, it falls back to
            the enabled icon.
        """
        # Create a new empty icon
        self._icon = QIcon()

        # Get the icon paths for enabled and disabled states
        path_enabled = self._icon_paths["enabled"]
        # Fallback if no disabled provided
        path_disabled = self._icon_paths["disabled"] or path_enabled

        # Add the enabled icon to the QIcon under the Normal mode
        if path_enabled:
            self._icon.addFile(path_enabled, mode=QIcon.Mode.Normal)

        # Add the disabled icon (or fallback) under the Disabled mode
        if path_disabled:
            self._icon.addFile(path_disabled, mode=QIcon.Mode.Disabled)

        # Apply the constructed icon to the button
        self.setIcon(self._icon)

    def eventFilter(self, obj: QObject, event: QEvent):
        """
        Intercepts hover-related events to dynamically update the button's
        icon based on state.

        This method allows the button to visually switch to a hover icon when
        the mouse enters and revert back to the enabled icon when the mouse
        leaves — but only if the button is enabled.

        :param obj: The object that is receiving the event (usually `self`).
        :type obj: QObject
        :param event: The event being processed (e.g. QEvent.Enter,
            QEvent.Leave).
        :type event: QEvent
        :return: True if the event is handled here, otherwise defer to the
            parent implementation.
        :rtype: bool

        Internal behavior:
        - Sets `_is_hovering` to True or False depending on the event type.
        - If the button is enabled and a hover icon is defined, it applies the
            hover icon on enter.
        - Reverts to the enabled icon (self._icon) on leave.
        """
        if event.type() == QEvent.Type.Enter and self.isEnabled():
            self._is_hovering = True
            if self._icon_paths["hover"]:
                # Show hover icon
                self.setIcon(QIcon(self._icon_paths["hover"]))

        elif event.type() == QEvent.Type.Leave and self.isEnabled():
            self._is_hovering = False
            self.setIcon(self._icon)  # Revert to enabled icon

        # Let the base class handle any other event types
        return super().eventFilter(obj, event)

    def setEnabled(self, enabled: bool):
        """ Overrides the default setEnabled method to change the icon when
        disabled.

        :param enabled: True to enable the button, False to disable it.
        :type enabled: bool
        """
        super().setEnabled(enabled)

        if enabled:
            if self._is_hovering and self._icon_paths["hover"]:
                # Restore hover icon
                self.setIcon(QIcon(self._icon_paths["hover"]))
            else:
                self.setIcon(self._icon)  # Restore default icon
        else:
            # Apply disabled icon, or fallback
            if self._icon_paths["disabled"]:
                # Create a pixmap from the image path
                pixmap = QPixmap(self._icon_paths["disabled"])
                # Add the pixmap to the icon for the Disabled mode. If this is
                # not done separately, the icon will have a grey effect and
                # not display the intended image correctly
                self._icon.addPixmap(pixmap, QIcon.Mode.Disabled)
                # Set the icon to Disabled mode to display the added pixmap
                self.setIcon(QIcon(self._icon, mode=QIcon.Mode.Disabled))
            else:
                self.setIcon(self._icon)

    # ----- Qt Designer Properties (exposed in Designer's Property Editor) ----

    def get_icon_enabled(self) -> str:
        """
        :return: Path to the icon used for the enabled state.
        :rtype: str
        """
        return self._icon_paths["enabled"]

    def set_icon_enabled(self, path: str):
        """
        :param path: Resource or file path for the enabled icon.
        :type path: str
        """
        if path != self._icon_paths["enabled"]:
            self._icon_paths["enabled"] = path
            self._set_enabled_or_disabled_icon()

    icon_enabled = Property(str, get_icon_enabled, set_icon_enabled)

    def get_icon_hover(self) -> str:
        """
        :return: Path to the icon used when hovered.
        :rtype: str
        """
        return self._icon_paths["hover"]

    def set_icon_hover(self, path: str):
        """
        :param path: Resource or file path for the hover icon.
        :type path: str
        """
        self._icon_paths["hover"] = path

    icon_hover = Property(str, get_icon_hover, set_icon_hover)

    def get_icon_disabled(self) -> str:
        """
        :return: Path to the icon used when disabled.
        :rtype: str
        """
        return self._icon_paths["disabled"]

    def set_icon_disabled(self, path: str):
        """
        :param path: Resource or file path for the disabled icon.
        :type path: str
        """
        self._icon_paths["disabled"] = path
        self._set_enabled_or_disabled_icon()

    icon_disabled = Property(str, get_icon_disabled, set_icon_disabled)
