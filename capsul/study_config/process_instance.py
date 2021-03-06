##########################################################################
# CAPSUL - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import sys
import os.path as osp
import importlib
import types
import re
import six

# Caspul import
from capsul.process.process import Process
from capsul.process.nipype_process import nipype_factory
from capsul.process.xml import create_xml_process
from capsul.pipeline.xml import create_xml_pipeline

# Nipype import
try:
    from nipype.interfaces.base import Interface
# If nipype is not found create a dummy Interface class
except ImportError:
    Interface = type("Interface", (object, ), {})

if sys.version_info[0] >= 3:
    basestring = str
    unicode = str


process_xml_re = re.compile(r'<process.*</process>', re.DOTALL)

def get_process_instance(process_or_id, study_config=None, **kwargs):
    """ Return a Process instance given an identifier.

    Note that it is convenient to create a process from a StudyConfig instance:
    StudyConfig.get_process_instance()

    The identifier is either:

        * a derived Process class.
        * a derived Process class instance.
        * a Nipype Interface instance.
        * a Nipype Interface class.
        * a string description of the class `<module>.<class>`.
        * a string description of a function to warp `<module>.<function>`.
        * a string description of a pipeline `<module>.<fname>.xml`.
        * an XML filename for a pipeline

    Default values of the process instance are passed as additional parameters.

    .. note:

        If no process is found an ImportError is raised.

    .. note:

        If the 'process_or_id' parameter is not valid a ValueError is raised.

    .. note:

        If the function to warp does not contain a process description in its
        docstring ('<process>...</process>') a ValueError is raised.

    Parameters
    ----------
    process_or_id: instance or class description (mandatory)
        a process/nipype interface instance/class or a string description.
    study_config: StudyConfig instance (optional)
        A Process instance belongs to a StudyConfig framework. If not specified
        the study_config can be set afterwards.
    kwargs:
        default values of the process instance parameters.

    Returns
    -------
    result: Process
        an initialized process instance.
    """
    # NOTE
    # here we make a bidouille to make study_config accessible from processes
    # constructors. It is used for instance in ProcessIteration.
    # This is not elegant, not thread-safe, and forbids to have one pipeline
    # build a second one in a different study_config context.
    # I don't have a better solution, however.
    set_study_config = not hasattr(Process, '_study_config')
    try:
        if set_study_config:
            Process._study_config = study_config
        return _get_process_instance(process_or_id, study_config=study_config,
                                     **kwargs)
    finally:
        if set_study_config:
            del Process._study_config


def _get_process_instance(process_or_id, study_config=None, **kwargs):

    result = None
    # If the function 'process_or_id' parameter is already a Process
    # instance.
    if isinstance(process_or_id, Process):
        result = process_or_id

    # If the function 'process_or_id' parameter is a Process class.
    elif (isinstance(process_or_id, type) and
          issubclass(process_or_id, Process)):
        result = process_or_id()

    # If the function 'process_or_id' parameter is already a Nipye
    # interface instance, wrap this structure in a Process class
    elif isinstance(process_or_id, Interface):
        result = nipype_factory(process_or_id)

    # If the function 'process_or_id' parameter is an Interface class.
    elif (isinstance(process_or_id, type) and
          issubclass(process_or_id, Interface)):
        result = nipype_factory(process_or_id())

    # If the function 'process_or_id' parameter is a function.
    elif isinstance(process_or_id, types.FunctionType):
        xml = getattr(process_or_id, 'capsul_xml', None)
        if xml is None:
            # Check docstring
            if process_or_id.__doc__:
                match = process_xml_re.search(
                    process_or_id.__doc__)
                if match:
                    xml = match.group(0)
        if xml:
            result = create_xml_process(process_or_id.__module__,
                                        process_or_id.__name__, 
                                        process_or_id, xml)()
        else:
            raise ValueError('Cannot find XML description to make function {0} a process'.format(process_or_id))
        
    # If the function 'process_or_id' parameter is a class string
    # description
    elif isinstance(process_or_id, basestring):
        elements = process_or_id.rsplit('.', 1)
        if len(elements) < 2:
            module_name, object_name = elements[0], elements[0]
        else:
            module_name, object_name = elements
        as_xml = False
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            # maybe XML filename or URL
            xml_url = process_or_id + '.xml'
            if osp.exists(xml_url):
                object_name = None
            elif process_or_id.endswith('.xml') and osp.exists(process_or_id):
                xml_url = process_or_id
                object_name = None
            else:
                # maybe XML file with pipeline name in it
                xml_url = module_name + '.xml'
                if not osp.exists(xml_url) and module_name.endswith('.xml') \
                        and osp.exists(module_name):
                    xml_url = module_name
                if not osp.exists(xml_url):
                    # try XML file in a module directory + class name
                    elements = module_name.rsplit('.', 1)
                    if len(elements) == 2:
                        module_name2, basename = elements
                        try:
                            importlib.import_module(module_name2)
                            mod_dirname = osp.dirname(
                                sys.modules[module_name2].__file__)
                            xml_url = osp.join(mod_dirname, basename + '.xml')
                            if not osp.exists(xml_url):
                                # if basename includes .xml extension
                                xml_url = osp.join(mod_dirname, basename)
                        except ImportError as e:
                            raise ImportError('Cannot import %s: %s'
                                              % (module_name, str(e)))
            as_xml = True
            if osp.exists(xml_url):
                result = create_xml_pipeline(module_name, object_name,
                                             xml_url)()

        if result is None and not as_xml:
            module = sys.modules[module_name]
            module_object = getattr(module, object_name, None)
            if module_object is not None:
                if (isinstance(module_object, type) and
                    issubclass(module_object, Process)):
                    result = module_object()
                elif isinstance(module_object, Interface):
                    # If we have a Nipype interface, wrap this structure in a Process
                    # class
                    result = nipype_factory(result)
                elif (isinstance(module_object, type) and
                    issubclass(module_object, Interface)):
                    result = nipype_factory(module_object())
                elif isinstance(module_object, types.FunctionType):
                    xml = getattr(module_object, 'capsul_xml', None)
                    if xml is None:
                        # Check docstring
                        if module_object.__doc__:
                            match = process_xml_re.search(
                                module_object.__doc__)
                            if match:
                                xml = match.group(0)
                    if xml:
                        result = create_xml_process(module_name, object_name,
                                                    module_object, xml)()
            if result is None:
                xml_file = osp.join(osp.dirname(module.__file__),
                                    object_name + '.xml')
                if osp.exists(xml_file):
                    result = create_xml_pipeline(module_name, None,
                                                 xml_file)()

    if result is None:
        raise ValueError("Invalid process_or_id argument. "
                         "Got '{0}' and expect a Process instance/string "
                         "description or an Interface instance/string "
                         "description".format(process_or_id))

    # Set the instance default parameters
    for name, value in six.iteritems(kwargs):
        result.set_parameter(name, value)

    if study_config is not None:
        if result.study_config is not None \
                and result.study_config is not study_config:
            raise ValueError("StudyConfig mismatch in get_process_instance "
                             "for process %s" % result)
        result.set_study_config(study_config)
    return result
