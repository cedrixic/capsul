# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
#


def is_trait_input(trait):
  
    """ Check if the trait is defined as an input

    Parameters
    ----------
    trait: trait (mandatory)
        the trait instance we want to test.

    Returns
    -------
    out: bool
      True if trait is an input,
      False if trait's parameter is defined as False, or is not defined (None).
    """
  
    return bool(trait.input)


def is_trait_output(trait):
  
    """ Check if the trait is defined as an input

    Parameters
    ----------
    trait: trait (mandatory)
        the trait instance we want to test.

    Returns
    -------
    out: bool
      True if trait is an input,
      False if trait's parameter is defined as False, or is not defined (None).
    """
    
    return bool(trait.output)