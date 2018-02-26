import subprocess
import os
import sys
import SimpleITK as sitk

# in order to find the metamorphosis binary
ndregDirPath = os.path.dirname(os.path.realpath(__file__)) + "/"
dimension = 3

def is_iterable(variable):
    """
    Returns True if variable is a list, tuple or any other iterable object
    """
    return hasattr(variable, '__iter__')


def is_number(variable):
    """
    Returns True if varible is is a number
    """
    try:
        float(variable)
    except TypeError:
        return False
    return True

def run_shell_command(command, checkReturnValue=True, verbose=False):
    """
    Runs a shell command and returns the output.
    """
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1)
    outText = ""

    for line in iter(process.stdout.readline, ''):
        if verbose:
            sys.stdout.write(line)
        outText += line
    # process.wait()
    process.communicate()[0]
    returnValue = process.returncode
    if checkReturnValue and (returnValue != 0):
        raise Exception(outText)

    return (returnValue, outText)

def txt_write(text, path, mode="w"):
    """
    Conveinence function to write text to a file at specified path
    """
    dir_make(os.path.dirname(path))
    textFile = open(path, mode)
    textFile.write(text)
    textFile.close()


def txt_read(path):
    """
    Conveinence function to read text from file at specified path
    """
    textFile = open(path, "r")
    text = textFile.read()
    textFile.close()
    return text


def txt_read_list(path):
    return map(float, txt_read(path).split())


def txt_write_list(parameterList, path):
    txt_write(" ".join(map(str, parameterList)), path)


def dir_make(dirPath):
    """
    Convenience function to create a directory at the given path
    """
    if dirPath != "":
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        return os.path.normpath(dirPath) + "/"
    else:
        return dirPath

def imgCopy(img):
    """
    Returns a copy of the input image
    """
    return sitk.Image(img)


def imgWrite(img, path):
    """
    Write sitk image to path.
    """
    dir_make(os.path.dirname(path))
    sitk.WriteImage(img, path)

def vtkReformat(inPath, outPath):
    """
    Reformats vtk file so that it can be read by CIS software.
    """
    # Get size of map
    inFile = open(inPath, "rb")
    lineList = inFile.readlines()
    for line in lineList:
        if line.lower().strip().startswith("dimensions"):
            size = map(int, line.split(" ")[1:dimension + 1])
            break
    inFile.close()

    if dimension == 2:
        size += [0]

    outFile = open(outPath, "wb")
    for (i, line) in enumerate(lineList):
        if i == 1:
            newline = line.lstrip(line.rstrip("\n"))
            line = "lddmm 8 0 0 {0} {0} 0 0 {1} {1} 0 0 {2} {2}".format(
                size[2] - 1, size[1] - 1, size[0] - 1) + newline
        outFile.write(line)

def imgCollapseDimension(inImg):
    inSize = inImg.GetSize()

    if inImg.GetDimension() == dimension and inSize[dimension - 1] == 1:
        outSize = list(inSize)
        outSize[dimension - 1] = 0
        outIndex = [0] * dimension
        inImg = sitk.Extract(inImg, outSize, outIndex, 1)

    return inImg

def imgRead(path):
    """
    Alias for sitk.ReadImage
    """

    inImg = sitk.ReadImage(path)
    inImg = imgCollapseDimension(inImg)
    # if(inImg.GetDimension() == 2): inImg =
    # sitk.JoinSeriesImageFilter().Execute(inImg)

    inDimension = inImg.GetDimension()
    inImg.SetDirection(sitk.AffineTransform(inDimension).GetMatrix())
    inImg.SetOrigin([0] * inDimension)

    return inImg