from __future__ import print_function
import unittest
import os


# Capsul import
from capsul.api import Process, Pipeline, JoinStrNode, CallbackNode
#import capsul

# Trait import
from traits.api import Float, File, Int, List, String, Undefined

# Capsul import
#from capsul.api import Process
#from capsul.api import Pipeline
from capsul.pipeline import pipeline_workflow

# other imports
import six

class ByteCopy(Process):

    input = File(input=True)
    output = File(input=True, output=True)
        
    def _run_process(self):
        command = 'cp -rf \'' + self.input.fullPath() + \
                   ' ' + self.output.fullPath()+ '\''
        print('launched : ' + command)
        os.system(command)
        
class CreateOffsets(CallbackNode):
  
    def __init__(self, pipeline, name, **kwargs):     
      super(CreateOffsets, self).__init__(pipeline, name, 
                                                ['input'],
                                                ['offsets'],
                                                input_types=[String],
                                                output_types=[List(String, output=True)])
      self.add_trait("input", String())
      self.add_trait("offsets", List(String, output=True))
    
    def callback(self):
        if self.input is not Undefined and os.path.exists(self.input):
            self.offsets = ['_1', '_2', '_3', '_4']

class FileCreation(CallbackNode):
    """ File creation
    """
    
    def __init__(self, pipeline, name, **kwargs):     
        super(FileCreation, self).__init__(pipeline, name, 
                                                ['input'],
                                                ['output'],
                                                input_types=[String],
                                                output_types=[String(output=True)])
        self.add_trait("input", String(optional=True))
        self.add_trait("output", String(output=True, optional=True))
        
    def callback(self):
        if self.input is not Undefined and os.path.exists(self.input):
            self.output = '/tmp/output_file'
        
class CheckOutput(Process):
    """ Output file checking
    """
    
    def __init__(self):
        super(CheckOutput, self).__init__()
        self.add_trait("input", String(optional=True))
        self.add_trait("output", String(output=True, optional=True))
        
    def _run_process(self):
        os.system('cp -rf '+ str(self.input) + ' ' + str(self.output))
 
class BlockIteration(Pipeline):
    """ Simple Pipeline to test the Callback Node
    """
    def pipeline_definition(self):
      
        join_node = JoinStrNode(ByteCopy,  \
                                {'input':'input_file','output':'output_file'},\
                                {'input':'?x12','output':'?x12'})
        self.add_iterative_process( 'iterative_byte_copy', join_node, ['offset'])

        self.add_callback('create_output', FileCreation,
                         do_not_export=['output'])
        self.add_link('create_output.output->iterative_byte_copy.output')
        self.add_callback('create_offsets', CreateOffsets,
                           do_not_export=['offsets'],)
        self.add_link('create_offsets.offsets->iterative_byte_copy.offset')
#        print('\nExport create_offset as input')
        self.export_parameter('create_offsets', 'input')
        self.add_link('input->iterative_byte_copy.input')
        self.add_link('input->create_output.input')
#        print('\nExport create_output as output')
        self.export_parameter('iterative_byte_copy', 'output', export_type='output')


class TestPipeline(unittest.TestCase):

    def setUp(self):
        os.system('rm -rf /tmp/input_file*')
        os.system('rm -rf /tmp/output_file*')
        self.pipeline = BlockIteration()
        input_path = '/tmp/input_file'
        os.system('touch ' + str(input_path))
        for i in range (1,5) :
          os.system('touch ' + str(input_path) + '_' + str(i))
#        print('system update input path in definition')
        self.pipeline.input = input_path

    def test_workflow(self):
        self.pipeline.workflow_ordered_nodes()
        self.assertTrue(
                self.pipeline.workflow_repr ==
                "create_output->create_offsets->iterative_byte_copy")

    def test_outputCreation(self):
        self.assertTrue( self.pipeline.output == "/tmp/output_file")
        self.assertFalse(os.path.exists('/tmp/output_file') )

        print("NODES : \n" + str(self.pipeline.nodes))
        
#        graph = self.pipeline.workflow_graph()
#        ordered_list = graph.topological_sort()
        self.pipeline.workflow_ordered_nodes()
        print("REPR : \n" + str(self.pipeline.workflow_repr))
        
#        self.pipeline()
#        workflow = pipeline_workflow.workflow_from_pipeline(
#            self.pipeline)
        
        self.assertTrue(os.path.exists('/tmp/output_file') )

    def test_partialInputCreation(self):
        for i in range (1,4):
          self.assertTrue( 
              os.path.exists('/tmp/input_file_' + str(i) ) )


def test():
    """ Function to execute unitest
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPipeline)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()

if __name__ == "__main__":
    print("RETURNCODE: ", test())

    if 0:
        import sys
        from soma.qt_gui.qt_backend import QtGui
        app = QtGui.QApplication(sys.argv)
        from capsul.qt_gui.widgets import PipelineDevelopperView
        
        os.system('rm -rf /tmp/input_file*')
        os.system('rm -rf /tmp/output_file*')
        pipeline = BlockIteration()
        input_path = '/tmp/input_file'
        os.system('touch ' + str(input_path))
        for i in range (1,5) :
          os.system('touch ' + str(input_path) + '_' + str(i))
#        print('system update input path in definition')
        pipeline.input = input_path
        
        view1 = PipelineDevelopperView(pipeline, show_sub_pipelines=True,
                                       allow_open_controller=True)
        view1.show()
        app.exec_()
        del view1
