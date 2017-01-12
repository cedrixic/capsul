from __future__ import print_function
import unittest
import os


# Capsul import
from capsul.api import Process, Pipeline, JoinStrNode, CallbackNode

# Trait import
from traits.api import Float, File, Int, List, Str, Undefined

class ByteCopy(Process):

    input = File()
    output = File(input=True, output=True)
        
    def _run_process(self):
        filename, offset = self.input.split('?')
        offset = int(offset)
        file = open(filename, 'rb')
        file.seek(offset)
        v = file.read(1)
        
        filename, offset = self.output.split('?')
        offset = int(offset)
        file = open(filename, 'rb+')
        file.seek(offset)
        file.write(v)
        
class CreateOffsets(CallbackNode):
    input = File()
#    processors = Int()
    offsets = List(Str, output=True)
    def __init__(self, pipeline, name, **kwargs):     
      super(CreateOffsets, self).__init__(pipeline, name, 
                                                ['input'],
                                                ['offsets'],
                                                input_types=[File],
                                                output_types=[List(Str, output=True)])
    def callback(self):
        if self.input is not Undefined and os.path.exists(self.input):
            file = open(self.input,'rb')
            file.seek(0, 2)
            file_size = file.tell()
            self.offsets = ['?%d' % i for i in range(file_size)]

class FileCreation(Process):
    """ File creation
    """
    input = File(optional=True)
    output = File(output=True, optional=True)
    
    def __init__(self):
        super(FileCreation, self).__init__()
        
    def _run_process(self):
        file = open(self.input, 'rb')
        file.seek(0, 2)
        size = file.tell()
        file = open(self.output,'wb')
        file.seek(size-1)
        file.write('\0')
 
class BlockIteration(Pipeline):
    """ Simple Pipeline to test the Callback Node
    """
    def pipeline_definition(self):
        join_node = JoinStrNode(ByteCopy,  \
                                {'input':'offset','output':'offset'})
#                                {'input.ima':'&ox=1','output.ima':'&ox=1'})
        self.add_iterative_process( 'iterative_byte_copy', join_node, ['offset'])
        #self.declare_inout_parameter('iterative_byte_copy.output')
#        self.export_parameter('iterative_byte_copy','output')
        
        self.add_process('create_output', 'FileCreation')
#        self.add_process('create_output', 'capsul.pipeline.test.test_uri.FileCreation')
#        self.export_parameter('create_output', 'input')
#        self.export_parameter('create_output', 'output')
        self.add_callback('create_offsets', CreateOffsets)
        self.add_link('create_offsets.offsets->iterative_byte_copy.offset')
        print('\nExport creat_offset as input')
        self.export_parameter('create_offsets', 'input')
        self.add_link('input->iterative_byte_copy.input')
        self.add_link('input->create_output.input')
        print('\nExport create_output as output')
        #a remettre - pour passer ctest en cours de dev
#        self.export_parameter('create_output', 'output')
#        self.add_link('iterative_byte_copy.output->output')
        

class TestPipeline(unittest.TestCase):

    def setUp(self):
#        print('\n')
        self.pipeline = BlockIteration()

    def test_uri(self):
        print('Nodes dic size : '+ str(len(self.pipeline.nodes)) )
        for nodename, nodeinst in self.pipeline.nodes.items():
          if nodename is '' : 
              nodename = 'Pipeline'
          print('NODE '+str(nodename) +' :' )
          for plugname, pluginst in nodeinst.plugs.items():
#            print(str(nodeinst.plugs.get(plugname, None).links_to))
            for destnodename, destplugname, destnodeinst, destpluginst, active \
                in nodeinst.plugs.get(plugname, None).links_to:
              if destnodename is '' : 
                destnodename = 'Pipeline'
              print(str(nodename) + '.'+str(plugname)+' links to ' +
                    str(destnodename) + '.'+str(destplugname) )
        graph = self.pipeline.workflow_graph()
        print("GRAPH : \n" + str(graph))
        print("NODES : \n" + str(self.pipeline.nodes))
        print("REPR : \n" + str(self.pipeline.workflow_repr))
        print("LIST : \n" + str(self.pipeline.workflow_list))

        
def test():
    """ Function to execute unitest
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPipeline)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()

if __name__ == "__main__":
    print("RETURNCODE: ", test())

    if 1:
        import sys
        from soma.qt_gui.qt_backend import QtGui
        app = QtGui.QApplication(sys.argv)
        from capsul.qt_gui.widgets import PipelineDevelopperView

        pipeline = BlockIteration()
        view1 = PipelineDevelopperView(pipeline, show_sub_pipelines=True,
                                       allow_open_controller=True)
        view1.show()
        app.exec_()
        del view1
