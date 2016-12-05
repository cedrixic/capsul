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
      Possible cases : 
      	.input	.output		result
      	 True	         True		 True
      	 True	         False		 True
      	 True	         None		 True
      	 False	   True		 False
      	 False         False		 True
      	 False	   None		 True
      	 None	         True		 False
      	 None          False		 True
      	 None 	   None		 True
    """
    
    if trait.output and not bool(trait.input) :
    	return False
    else:
        return True


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
      Possible cases : 
      	.input	.output		result
      	 True	 True		 True
      	 True	 False		 False
      	 True	 None		 False
      	 False	 True		 True
      	 False   False		 False
      	 False	 None		 False
      	 None	 True		 True
      	 None    False		 False
      	 None 	 None		 False
    """
    
    return bool(trait.output)