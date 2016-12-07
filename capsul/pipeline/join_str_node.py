from __future__ import print_function
import unittest


# Capsul import
from capsul.api import Pipeline
from capsul.pipeline.pipeline_nodes import CallbackNode
from capsul.process.traits_utils import is_trait_input, is_trait_output

# Trait import
from traits.api import Float, File, Int, List, String, Undefined, Dict
import six

'''
Add a class JoinStrNode that concatenates input values together.
It could be written:
JoinStrNode(Process, {'param1': 'param2', 'param3':'param2'})

That means:
- JoinStrNode derive Pipeline and contains a CallbackNode and a ProcessNode
- It creates a trait for 'param1', 'param2', 'param3' as Input of CallbackNode
- Create traits for 'param1' and 'param3' as Output of CallbackNode. 
  These output parameters could be named 'param1_out' and 'param3_out'
- Define the callback method to concatenate:
param1 value + param2 value to param1_out and param3 value + param2 value to param3_out
- Add links 'CallbackNode.param1_out->Process.param1' and 'CallbackNode.param3_out->Process.param3'


TODO :

- output must be delared as input/output to propagate value


'''
class JoinStrCallbackNode(CallbackNode):
    def __init__(self, pipeline, name, **kwargs):     
      super(JoinStrCallbackNode, self).__init__(pipeline, name, 
                                                ['str_in1', 'str_in2'],
                                                ['str_out'],
                                                input_types=[String, String],
                                                output_types=[String])

        
    def callback(self, *args, **kwargs):
#      print('JoinStrCallbackNode->callback: ', 'str_in1:', self.str_in1, ', ', 
#                                               'str_in2:', self.str_in2)
      if self.str_in1 is not Undefined and self.str_in2 is not Undefined :   
        self.str_out = self.str_in1 + self.str_in2
#        print('JoinStrCallbackNode->callback: str_out:', self.str_out)
        
class RemoveStrCallbackNode(CallbackNode):
    def __init__(self, pipeline, name, **kwargs):     
      super(RemoveStrCallbackNode, self).__init__(pipeline, name, 
                                                ['str_in1', 'str_in2'],
                                                ['str_out'],
                                                input_types=[String, String],
                                                output_types=[String])
                                                

        
    def callback(self, *args, **kwargs):
#      print('JoinStrCallbackNode->callback: ', 'str_in1:', self.str_in1, ', ', 
#                                               'str_in2:', self.str_in2)
      if self.str_in1 is not Undefined and \
         self.str_in2 is not Undefined and \
         self.str_in1.endswith(self.str_in2):   
        
        self.str_out = self.str_in1[:-len(self.str_in2)]
#        print('JoinStrCallbackNode->callback: str_out:', self.str_out)
  
class JoinStrNode(Pipeline):
    
    def __init__(self, process, param_dict):
        super(JoinStrNode, self).__init__()
        
        print ('param_dict:', param_dict)
        #self.process = process
        self.add_process('internal_process', process)
                
        verbose = False
#        verbose = True
        
        i = 0
        t = False
        print('Iterate through parameters dictionary...')
        for param_name, param_val in six.iteritems(param_dict) :
          print('\nParameter : ', param_name, ' - Value : ', param_val)
          
          # Get process traits for param_name to determine direction
#          output = process.class_traits()[param_name].output
#          input = process.class_traits()[param_name].input
          optional = process.class_traits()[param_name].optional
#          optional = 'youpi'
          
          input = is_trait_input(process.class_traits()[param_name])
          output = is_trait_output(process.class_traits()[param_name])
          
          if verbose : 
            print('TEST INPUT : ', input)
            print('TEST OUTPUT : ', output)
          
          # Add pippeline new param_name trait
            print('!!ADDING TRAIT!!')
          self.add_trait(param_name, String(output = output, 
                                            input = True,
                                            optional = optional))
#          process.class_traits()[param_name].input = True
          if verbose : 
            print('After adding\n\tTEST INPUT : ',
                  is_trait_input(self.traits()[param_name]),
                  '\n\tTEST OUTPUT : ',
                  is_trait_output(self.traits()[param_name]),
                  '\n\tTEST OPTIONAL : ',
                  process.class_traits()[param_name].optional)

#          print('export_parameter:', 'self', param_name)
#          self.export_parameter( self, param_name)

#          if not param_val in process.class_traits():
#          print(self.traits())
#          print(str(self.traits()))

#          Adding offset as a trait only if does not exists yet (to check!!)

          if not self.traits().get(param_val) :
            self.add_trait(param_val, String(output = False, 
                                              input = True,
                                              optional = True))
            
            
          param_val = param_dict[param_name]
          callback_node_name = "JoinStrCallbackNode_" + str(i)
          callback_remove_node_name = "RemoveStrCallbackNode_" + str(i)
#          self.add_callback(callback_node_name, JoinStrCallbackNode)
#          self.add_callback(callback_remove_node_name, RemoveStrCallbackNode)
          if output:
            #add removeCallback
            self.add_callback(callback_remove_node_name, RemoveStrCallbackNode)
            self.add_link('internal_process.' + param_name + '->' + callback_remove_node_name + '.str_in1')
            self.add_link( callback_remove_node_name + '.str_out->' + param_name)
            self.add_link(param_val + '->' + callback_remove_node_name + '.str_in2')
            #addJoinCallback
            self.add_callback(callback_node_name, JoinStrCallbackNode)
            self.add_link(param_name + '->' + callback_node_name + '.str_in1')
            self.add_link( callback_node_name + '.str_out->' + callback_remove_node_name + '.str_in1')
            self.add_link(param_val + '->' + callback_node_name + '.str_in2')
            
            if verbose :
              print('\tplug type : output')
              print('\tadd_link:', 'internal_process.' + param_name + '->' + callback_remove_node_name + '.str_in1')
              print('\tadd_link:', callback_remove_node_name + '.str_out->' + param_name)
              print('\tadd_link:', param_val + '->' + callback_remove_node_name + '.str_in2')
              print('\tplug type : output, creating joinCallback')
              print('\tadd_link:', param_name + '->' + callback_node_name + '.str_in1')
              print('\tadd_link:', callback_node_name + '.str_out->' + callback_remove_node_name + '.str_in1')
              print('\tadd_link:', param_val + '->' + callback_node_name + '.str_in2')
            
            
#          else:
          if input:
            self.add_callback(callback_node_name, JoinStrCallbackNode)
            self.add_link(param_name + '->' + callback_node_name + '.str_in1')
            self.add_link( callback_node_name + '.str_out->internal_process.' + param_name)
            self.add_link(param_val + '->' + callback_node_name + '.str_in2')
            
            if verbose :
              
              print('\tplug type : input')
              print('\tadd_link:', param_name + '->' + callback_node_name + '.str_in1')
              print('\tadd_link:', callback_node_name + '.str_out->internal_process.' + param_name)
              print('\tadd_link:', param_val + '->' + callback_node_name + '.str_in2')

#          
#          print('\tadd_link:', param_val + '->' + callback_node_name + '.str_in2')
#          self.add_link(param_val + '->' + callback_node_name + '.str_in2')
          i += 1
            
#           # Update pipeline Traits
#          param_out_name = "{}_out".format(str(param_name))
#          self.add_trait(param_name, String(output = False))
#          self.add_trait(param_out_name, String(output = True))
#          self.trait(param_name) = param_val
#          
#          # update callback Traits
#          param_callback_name = "{}_cbk_in".format(str(param_name))
#          param_callback_out_name = "{}_cbk_out".format(str(param_name))
#          self.c.add_trait(param_callback_name, String(output=False))
#          self.c.add_trait(param_callback_out_name, String(output=True))
#        
#        
##        self.c.add_trait('param_dict', Dict())
#                  
#        self.c.callback = self.joinTraitChange(process)
#        self.add_process("Callback", self.c)
##        self.param1.on_trait_change(self.joinTraitChange)
    
#    def joinTraitChange(self) :
#      
#      for name, value in self.get_inputs():
#        
#        param_out_value = str.join(str(param1), str(param2))
#        param_out_name = "{}_out".format(str(param1))
#      
##      out_list = []
#      for param1 in self.c.param_dict :
#        param2 = self.c.param_dict[param1]
#        
#        param_out_value = str.join(str(param1), str(param2))
#        param_out_name = "{}_out".format(str(param1))
#        
#        #Inputs and outputs creation for CallbackNode (i.e. process)
#        self.process.add_trait(param_out_name, String())
        
        
#        #Creation of links between callback and joinStrNode
#        self.process.trait(param_out_name).output = True
#        self.process.trait(param_out_name).value = param_out_value
#        self.trait(param_out_name).output = True
#        self.trait(param_out_name).value = param_out_value
#        self.add_link("{0}->{1}".format(str(param1), param_out_name))
#        #-------
        