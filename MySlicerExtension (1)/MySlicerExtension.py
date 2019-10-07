import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import slicer
import SimpleITK as sitk
global sitkUtils
import sitkUtils
import numpy


#
# MySlicerExtension
#

class MySlicerExtension(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Keychain Extension" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Henry Pehr (UNC-Chapel Hill)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Henry Pehr
""" # replace with organization, grant and thanks.

#
# MySlicerExtensionWidget
#

class MySlicerExtensionWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputLeft = slicer.qMRMLNodeComboBox()
    self.inputLeft.nodeTypes = ["vtkMRMLModelNode"]
    self.inputLeft.selectNodeUponCreation = True
    self.inputLeft.addEnabled = False
    self.inputLeft.removeEnabled = False
    self.inputLeft.noneEnabled = False
    self.inputLeft.showHidden = False
    self.inputLeft.showChildNodeTypes = True
    self.inputLeft.setMRMLScene( slicer.mrmlScene )
    self.inputLeft.setToolTip( "Pick the input to the algorithm." )
    self.inputRight = slicer.qMRMLNodeComboBox()
    self.inputRight.nodeTypes = ["vtkMRMLModelNode"]
    self.inputRight.selectNodeUponCreation = True
    self.inputRight.addEnabled = False
    self.inputRight.removeEnabled = False
    self.inputRight.noneEnabled = False
    self.inputRight.showHidden = False
    self.inputRight.showChildNodeTypes = True
    self.inputRight.setMRMLScene( slicer.mrmlScene )
    self.inputRight.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Left Side: ", self.inputLeft)
    parametersFormLayout.addRow("Input Right Side: ", self.inputRight)

    #
    # no output volume selector
    #



    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputLeft.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputRight.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    # self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputLeft.currentNode() and self.inputRight.currentNode()

  def onApplyButton(self):
    logic = MySlicerExtensionLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked

    logic.run(self.inputLeft.currentNode(), self.inputRight.currentNode(), enableScreenshotsFlag)

#
# MySlicerExtensionLogic
#

class MySlicerExtensionLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, leftVol, rightVol, enableScreenshots=0):
    """
    Run the actual algorithm
    """
    logging.info('Processing started')

    nodeName = "BlankVolume"
    imageSize = [390, 466, 318]
    voxelType=vtk.VTK_UNSIGNED_CHAR
    imageOrigin = [98, 98, -72]
    imageSpacing = [0.5, 0.5, 0.5]
    imageDirections = [[-1,0,0], [0,-1,0], [0,0,1]]
    fillVoxelValue = 255
    # Create an empty image volume, filled with fillVoxelValue
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(voxelType, 1)
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetInputData(imageData)
    thresholder.SetInValue(fillVoxelValue)
    thresholder.SetOutValue(fillVoxelValue)
    thresholder.Update()
    # Create volume node
    blankVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
    blankVolumeNode.SetOrigin(imageOrigin)
    blankVolumeNode.SetSpacing(imageSpacing)
    blankVolumeNode.SetIJKToRASDirections(imageDirections)
    blankVolumeNode.SetAndObserveImageData(thresholder.GetOutput())
    blankVolumeNode.CreateDefaultDisplayNodes()
    blankVolumeNode.CreateDefaultStorageNode()
    logging.info('Created empty volume Blank Volume')


    # left right front back bottom top
    leftData = leftVol.GetPolyData().GetPoints().GetBounds()
    rightData = rightVol.GetPolyData().GetPoints().GetBounds()
    leftBound = leftData[0]
    rightBound = rightData[1]
    topBound = max(leftData[5],rightData[5])
    frontBound = min(leftData[2],rightData[2])
    backBound = max(leftData[3],rightData[3])
    midline = (leftBound+rightBound)/2
    halfway = -(backBound+frontBound)/1.7
    print(leftBound, rightBound)
    print("Midline:", midline)
    print(frontBound,backBound)
    print("Halfway:", halfway)
    print("Top:", topBound)




    # handleNode.SetAndObservePolyData(handle.GetOutput())
    # handleNode.CreateDefaultDisplayNodes()
    def makeHandle():
        fn = vtk.vtkParametricTorus()
        fn.SetRingRadius((rightBound-leftBound)/5)
        fn.SetCrossSectionRadius((rightBound-leftBound)/15)
        #vtk.FlipNormalsOn()
        source = vtk.vtkParametricFunctionSource()
        source.SetParametricFunction(fn)
        source.Update()

        trans = vtk.vtkTransform()
        trans.RotateX(90)
        trans.Translate(midline,topBound+5,halfway)
        # vtk generate normals
        # communicate with SLACK
        rotate = vtk.vtkTransformPolyDataFilter()
        rotate.SetTransform(trans)
        rotate.SetInputConnection(source.GetOutputPort())
        rotate.Update()

        return rotate.GetOutput()


    handleVol = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', "handle")
    handle = makeHandle()
    handleVol.SetAndObservePolyData(handle)
    handleVol.CreateDefaultDisplayNodes()
    handleVol.CreateDefaultStorageNode()

    leftBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "leftBLM")
    # leftBLM.CreateDefaultDisplayNodes()
    # leftBLM.CreateDefaultStorageNode()

    rightBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "rightBLM")
    # rightBLM.CreateDefaultDisplayNodes()
    # rightBLM.CreateDefaultStorageNode()

    handleBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "handleBLM")
    # handleBLM.CreateDefaultDisplayNodes()
    # handleBLM.CreateDefaultStorageNode()

    leftParams = {'sampleDistance' : 0.1, 'InputVolume' : blankVolumeNode.GetID(), 'surface' : leftVol.GetID(), 'OutputVolume': leftBLM.GetID()}
    process = slicer.cli.run(slicer.modules.modeltolabelmap, None, leftParams, wait_for_completion=True)

    rightParams = {'sampleDistance' : 0.1, 'InputVolume' : blankVolumeNode.GetID(), 'surface' : rightVol.GetID(), 'OutputVolume': rightBLM.GetID()}
    process = slicer.cli.run(slicer.modules.modeltolabelmap, None, rightParams, wait_for_completion=True)

    # we have leftBLM, rightBLM, and handleBLM; all are binary label maps
    brainBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "brainBLM")
    # brainBLM.CreateDefaultDisplayNodes()
    # brainBLM.CreateDefaultStorageNode()

    path = slicer.util.tempDirectory("saves")
    leftPath = path + "/left.nrrd"
    rightPath = path + "/right.nrrd"

    slicer.util.saveNode(leftBLM,leftPath)
    slicer.util.saveNode(rightBLM,rightPath)

    left = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(leftBLM.GetName()))
    right = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(rightBLM.GetName()))

    orFilter = sitk.OrImageFilter()
    brain = orFilter.Execute(right,left)

    dilateFilter = sitk.BinaryDilateImageFilter()
    rad = round((rightBound-leftBound)/30)
    dilateFilter.SetKernelRadius(rad)
    dilateFilter.SetBackgroundValue(0)
    dilateFilter.SetForegroundValue(255)
    print(dilateFilter.GetKernelType(), dilateFilter.GetKernelRadius())

    brain_dilated = dilateFilter.Execute(brain)

    holesFilter = sitk.BinaryFillholeImageFilter()
    brain_dilated_fixed = holesFilter.Execute(brain_dilated, True, 255)
    #output = orFilter.Execute(intermediate, handle)


    sitkUtils.PushToSlicer(brain_dilated_fixed, "combined sides", compositeView=0, overwrite=False)
    slicer.mrmlScene.RemoveNode(leftBLM)
    slicer.mrmlScene.RemoveNode(rightBLM)
    slicer.mrmlScene.RemoveNode(handleBLM)
    slicer.mrmlScene.RemoveNode(brainBLM)
    slicer.mrmlScene.RemoveNode(blankVolumeNode)



    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('MySlicerExtensionTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class MySlicerExtensionTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_MySlicerExtension1()

  def test_MySlicerExtension1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """


    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    nodeName = "BlankVolume"
    imageSize = [390, 466, 318]
    voxelType=vtk.VTK_UNSIGNED_CHAR
    imageOrigin = [98, 98, -72]
    imageSpacing = [0.5, 0.5, 0.5]
    imageDirections = [[-1,0,0], [0,-1,0], [0,0,1]]
    fillVoxelValue = 255
    # Create an empty image volume, filled with fillVoxelValue
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(voxelType, 1)
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetInputData(imageData)
    thresholder.SetInValue(fillVoxelValue)
    thresholder.SetOutValue(fillVoxelValue)
    thresholder.Update()
    # Create volume node
    blankVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
    blankVolumeNode.SetOrigin(imageOrigin)
    blankVolumeNode.SetSpacing(imageSpacing)
    blankVolumeNode.SetIJKToRASDirections(imageDirections)
    blankVolumeNode.SetAndObserveImageData(thresholder.GetOutput())
    blankVolumeNode.CreateDefaultDisplayNodes()
    blankVolumeNode.CreateDefaultStorageNode()
    logging.info('Created empty volume Blank Volume')

    def makeHandle():
        fn = vtk.vtkParametricTorus()
        fn.SetRingRadius(20)
        fn.SetCrossSectionRadius(7)



        source = vtk.vtkParametricFunctionSource()
        source.SetParametricFunction(fn)
        source.Update()

        trans = vtk.vtkTransform()
        trans.RotateX(90)
        trans.Translate(-8,52,25)
        rotate = vtk.vtkTransformPolyDataFilter()
        rotate.SetTransform(trans)
        rotate.SetInputConnection(source.GetOutputPort())
        rotate.Update()



        return rotate.GetOutput()

    handleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', "handle")
    handle = makeHandle()

    handleNode.SetAndObservePolyData(handle)
    handleNode.CreateDefaultDisplayNodes()
    handleNode.CreateDefaultStorageNode()


    self.delayDisplay('Test passed!')
