# -*- coding: utf-8 -*-
"""
Tests instance of JoinStrNode class
"""

from __future__ import print_function
import unittest
import tempfile
import os


# Capsul import
from capsul.api import Process, Pipeline, JoinStrNode
# Trait import
from traits.api import Float, File, Int, List, Str, Undefined

class TestProcess(Process):

    input = File()
    output = File(input=True, output=True)
        
    def _run_process(self):
        
        output = tempfile.TemporaryFile(prefix='tmpOut', dir=str(self.directory))
        
        
#class TestPipeline(Pipeline):
class TestPipeline(unittest.TestCase):
  
    def setUp(self):
        print('Pipeline setup')
        print('Create input files')
        self.directory = tempfile.mkdtemp("join_test")
        self.tmpIn = tempfile.TemporaryFile(prefix='tmpIn', dir=str(self.directory))
        self.tmpInOr = self.tmpIn[:-2]
        self.tmpOut = tempfile.TemporaryFile(suffix='_1',prefix='tmpOut', dir=str(self.directory))
        self.tmpOutOr = self.tmpOut[:-2]
        self.offset = '_1'
                
        self.pipeline = JoinStrNode(TestProcess,  \
                                {self.tmpInOr:self.offset,\
                                 self.tmpOutOr:self.offset})
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

        pipeline = JoinStrNode(ByteCopy,  \
                                {'input':'offset','output':'offset'})
        
        view1 = PipelineDevelopperView(pipeline, show_sub_pipelines=True,
                                       allow_open_controller=True)
        view1.show()
        app.exec_()
        del view1
