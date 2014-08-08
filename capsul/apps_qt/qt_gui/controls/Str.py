#! /usr/bin/env python
##########################################################################
# CAPSUL - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import logging
from functools import partial

# Soma import
from soma.qt_gui.qt_backend import QtGui, QtCore
from soma.utils.functiontools import SomaPartial


class StrControlWidget(object):
    """ Control to enter a string.
    """

    @staticmethod
    def is_valid(control_instance, *args, **kwargs):
        """ Method to check if the new control value is correct.

        If the new entered value is not correct, the backroung control color
        will be red.

        Parameters
        ----------
        control_instance: QLineEdit (mandatory)
            the control widget we want to validate
        """
        # Get the current control palette
        control_palette = control_instance.palette()

        # Get the control current value
        control_value = control_instance.text()

        # If the control value is not empty, the control is valid and the
        # backgound color of the control is white
        is_valid = False 
        if control_value != "":
            control_palette.setColor(
                control_instance.backgroundRole(), QtCore.Qt.white)
            is_valid = True

        # If the control value is empty, the control is not valid and the
        # backgound color of the control is red
        else:
            control_palette.setColor(
                control_instance.backgroundRole(), QtCore.Qt.red)

        # Set the new palette to the control instance
        control_instance.setPalette(control_palette)

        return is_valid

    @classmethod
    def check(cls, control_instance):
        """ Check if a controller widget control is filled correctly.

        Parameters
        ----------
        cls: StrControlWidget (mandatory)
            a StrControlWidget control
        control_instance: QLineEdit (mandatory)
            the control widget we want to validate
        """
        # Hook: function that will be called to check for typo 
        # when a 'textEdited' qt signal is emited
        widget_callback = partial(cls.is_valid, control_instance)

        # Execute manually the first time the control check method
        widget_callback()

        # When a qt 'textEdited' signal is emited, check if the new
        # user value is correct
        control_instance.textChanged.connect(widget_callback)


    @staticmethod
    def create_widget(parent, control_name, control_value, trait):
        """ Method to create the widget.

        Parameters
        ----------
        parent: QWidget (mandatory)
            the parent widget
        control_name: str (mandatory)
            the name of the control we want to create
        control_value: str (mandatory)
            the default control value
        trait: Tait (mandatory)
            the trait associated to the control

        Returns
        -------
        out: 2-uplet
            a two element tuple of the form (control widget: QLineEdit,
            associated label: QLabel)
        """
        # Create the widget that will be used to fill a string
        widget = QtGui.QLineEdit(parent)

        # Create the label associated with the string widget
        control_label = trait.label
        if control_label is None:
            control_label = control_name
        if control_label is not None:
            label = QtGui.QLabel(control_label, parent)
        else:
            label = None

        return (widget, label)

    @staticmethod
    def update_controller(controller_widget, control_name, control_instance):
        """ Update one element of the controller.

        At the end the controller trait value with the name 'control_name'
        will match the controller widget user parameters defined in
        'control_instance'.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: StrControlWidget (mandatory)
            the instance of the controller widget control we want to synchronize
            with the controller
        """
        setattr(controller_widget.controller, control_name, unicode(
                control_instance.text()))

    @staticmethod
    def update_controller_widget(controller_widget, control_name,
                                 control_instance):
        """ Update one element of the controller widget.

        At the end the controller widget user editable parameter with the
        name 'control_name' will match the controller trait value with the same
        name.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: StrControlWidget (mandatory)
            the instance of the controller widget control we want to synchronize
            with the controller
        """
        control_instance.setText(
            unicode(getattr(controller_widget.controller, control_name, "")))

    @classmethod
    def connect(cls, controller_widget, control_name, control_instance):
        """ Connect a 'Str' or 'String' controller trait and a
        'StrControlWidget' controller widget control.

        Parameters
        ----------
        cls: StrControlWidget (mandatory)
            a StrControlWidget control
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str (mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QLineEdit (mandatory)
            the instance of the controller widget control we want to synchronize
            with the controller
        """
        # Update one element of the controller.
        # Hook: function that will be called to update a specific 
        # controller trait when a 'userModification' qt signal is emited
        widget_hook = partial(cls.update_controller, controller_widget,
                              control_name, control_instance)

        # When a qt 'userModification' signal is emited, update the 
        # 'control_name' controller trait value
        control_instance.connect(
            control_instance, QtCore.SIGNAL('userModification'),
            widget_hook)

        # Update one element of the controller widget.
        # Hook: function that will be called to update the specific widget 
        # when a trait event is detected.
        controller_hook = SomaPartial(
            cls.update_controller_widget, controller_widget, control_name,
            control_instance)

        # When the 'control_name' controller trait value is modified, update
        # the corresponding control
        controller_widget.controller.on_trait_change(
            controller_hook, name=control_name)

        # Store the trait - control connection we just build
        control_instance._controller_connections = (
            widget_hook, controller_hook)

    @staticmethod
    def disconnect(controller_widget, control_name, control_instance):
        """ Disconnect a 'Str' or 'String' controller trait and a
        'StrControlWidget' controller widget control.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QLineEdit (mandatory)
            the instance of the controller widget control we want to synchronize
            with the controller
        """
        # Get the stored widget and controller hooks
        widget_hook, controller_hook = attribute_widget._controller_connections

        # Remove the controller hook from the 'control_name' trait
        controller_widget.controller.on_trait_change(
            controller_hook, name=control_name, remove=True)

        # Remove the widget hook associated with the qt 'userModification'
        # signal
        attribute_widget.disconnect(
            control_instance, QtCore.SIGNAL('userModification'),
            widget_hook)

        # Delete the trait - control connection we just remove
        del attribute_widget._controller_connections