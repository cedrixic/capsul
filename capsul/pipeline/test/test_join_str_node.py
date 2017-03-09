# -*- coding: utf-8 -*-
"""
Tests instance of JoinStrNode class
"""

from __future__ import print_function
import unittest
import tempfile
import os, os.path


# Capsul import
from capsul.api import Process, Pipeline, JoinStrNode
# Trait import
from traits.api import Float, File, Int, List, String, Undefined

class TestProcess(Process):

#    input = File()
#    output = File(input=True, output=True)
#    kernel_radius = Float(input=True, output=False)
#    kernel = Int(input=True, output=False)

    input = String()
    output = String(input=True, output=True)
    kernel_radius = String(input=True, output=False)
    kernel = String(input=True, output=False)
    mode = String(input=True,output=False)
        
    def _run_process(self):
#        self.output = tempfile.TemporaryFile(prefix='tmpOut', dir=str(self.directory))
        command = ( 'AimsMorphoMath ' + 
                     ' -m ' + str(self.mode) +
                     ' -r ' + str(self.kernel_radius) +
                     ' -x ' + str(self.kernel) +
                     ' -y ' + str(self.kernel) +
                     ' -z ' + str(self.kernel) )
          
        command += ' -i \'' + self.input.fullPath() + \
                   '\' -o \'' + self.output.fullPath()+ '\''
        print('launched : ' + command)
        os.system(command)
        
#class TestPipeline(Pipeline):
class TestPipeline(unittest.TestCase):
  
    def setUp(self):
        print('Pipeline setup')
        print('Create input files')
        self.directory = tempfile.mkdtemp("join_test")
        self.offset = '_1'
        self.tmpIn = tempfile.NamedTemporaryFile(\
            suffix=str(self.offset),prefix='tmpIn', dir=str(self.directory))
        self.tmpInOr = self.tmpIn.name[:-2]
        self.tmpOut = tempfile.NamedTemporaryFile(\
            suffix=str(self.offset),prefix='tmpOut', dir=str(self.directory))
        self.tmpOutOr = self.tmpOut.name[:-2]

        self.mode = 'ero'
        self.kernel = 3
        self.kernel_redius = 0.5
        
        print('tmpIn : ' + str(self.tmpIn.name))
        print('tmpInOr : ' + str(self.tmpInOr))
        print('tmpOut : ' + str(self.tmpOut.name))
        print('tmpOutOr : ' + str(self.tmpOutOr))
        print('offset : ' + str(self.offset))
        print('mode : ' + str(self.mode))
        print('kernel : ' + str(self.kernel))
        print('kernel_redius : ' + str(self.kernel_redius))
                
#        self.pipeline = JoinStrNode(TestProcess,  \
#                                {self.tmpInOr:self.offset,\
#                                 self.tmpOutOr:self.offset})
                
        self.pipeline = JoinStrNode(TestProcess,  \
                                {'input':self.tmpInOr,\
                                 'output':self.tmpOutOr,
                                 'mode':self.mode,
                                 'kernel':self.kernel,
                                 'kernel_radius':self.kernel_redius},\
                                {'input':self.offset,\
                                 'output':self.offset})
                                 
        print("NODES : \n" + str(self.pipeline.nodes))
        print("REPR : \n" + str(self.pipeline.workflow_repr))
        print("LIST : \n" + str(self.pipeline.workflow_list))
        
        
    def test_pipe(self):
#        graph = self.pipeline.workflow_graph()
#        print("GRAPH : \n" + str(graph))
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

#        pipeline = JoinStrNode(TestProcess,  \
#                                {'input':'offset','output':'offset'})
        

        directory = tempfile.mkdtemp("join_test")
        offset = '_1'
        tmpIn = tempfile.NamedTemporaryFile(\
            suffix=str(offset),prefix='tmpIn', dir=str(directory))
        tmpInOr = tmpIn.name[:-2]
        tmpOut = tempfile.NamedTemporaryFile(\
            suffix=str(offset),prefix='tmpOut', dir=str(directory))
        tmpOutOr = tmpOut.name[:-2]

        mode = 'ero'
        kernel = 3
        kernel_redius = 0.5
                
        pipeline = JoinStrNode(TestProcess,  \
                                {'input':tmpInOr,\
                                 'output':tmpOutOr,
                                 'mode':mode,
                                 'kernel':kernel,
                                 'kernel_radius':kernel_redius},\
                                {'input':offset,\
                                 'output':offset})        
        
        
        
        view1 = PipelineDevelopperView(pipeline, show_sub_pipelines=True,
                                       allow_open_controller=True)
        view1.show()
        app.exec_()
        del view1
