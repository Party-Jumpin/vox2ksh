import xml.etree.ElementTree as ET
import glob
import os
from subprocess import Popen
from shutil import copyfile
import sys

def copyPNGs(path, dest, number):
    for file in glob.glob(path + "/*" + number + ".png"):
        copyfile(file, dest + "/" + number + ".png")

def getDifficultyList(diff):
    if (diff == "novice"):
        return "light"
    if (diff == "advanced"):
        return "challenge"
    if (diff == "exhaust"):
        return "extended"
    if (diff == "maximum"):
        return "infinite"
    return "infinite"

def getDifficultyKSHList(diff):
    if (diff == "novice"):
        return "nov"
    if (diff == "advanced"):
        return "adv"
    if (diff == "exhaust"):
        return "exh"
    if (diff == "maximum"):
        return "mxm"
    return "inf"

def getDifficultyToInteger(diff):
    if (diff == "novice"):
        return "1"
    if (diff == "advanced"):
        return "2"
    if (diff == "exhaust"):
        return "3"
    if (diff == "maximum"):
        return "5"
    return "4"


def createPrefixVox(title, artist, minBPM, maxBPM, effect, difficulty, level, diffSongExist, diffPngExist):
    kmap = ""
    kmap += "title=" + title
    kmap += "\nartist=" + artist
    kmap += "\neffect=" + effect
    kmap += "\nillustrator=-"
    kmap += "\ndifficulty=" + getDifficultyList(difficulty)
    kmap += "\nlevel=" + level
    kmap += "\nt=" + minBPM
    if (maxBPM != minBPM):
        kmap += "-" + maxBPM
    if (diffSongExist == 0):
        kmap += "\nm=music.ogg"
    else:
        kmap += "\nm=" + getDifficultyToInteger(difficulty) + ".ogg"
    kmap +="\nmvol=100\no=0\nbg=deepsea\nlayer=arrow\npo=90473\nplength=15000\nchokkakuvol=30\nver=1"
    if (diffPngExist == 0):
        kmap += "\njacket=1"
    else:
        kmap += "\njacket=" + getDifficultyToInteger(difficulty)
    kmap += ".png\nfiltertype=peak\n"
    return kmap

def createFolderIfNotExist(folder):
    if glob.glob(folder):
        return None
    else:
        os.makedirs(folder)
        return None
    
def createFileIfNotExist(filePath):
    if (glob.glob(filePath)):
        return None
    with open(filePath, 'w+'): pass
    return None

def runFFMPEGtoConvertSong(file, outputFile):
    #print("ffmpeg.exe -i " + file + outputFile)
    os.system("ffmpeg.exe -n -i " + file + " " + outputFile)

def getSpecificDifficultySongSound(file, number):
    if (number == 1):
        file += "_1n.s3v"
    elif (number == 2):
        file += "_2a.s3v"
    elif (number == 3):
        file += "_3e.s3v"
    elif (number == 4):
        file += "_4i.s3v"
    elif (number == 5):
        file += "_5m.s3v"
    return file

def checkIfSpecificOggExist(file, number):
    if glob.glob(getSpecificDifficultySongSound(file, number)):
        return 1
    return 0

def createOutputSong(file, outputFolder, xmls):
    songInfo = xmls.find("info")
    title = songInfo.find("title_name").text
    artist = songInfo.find("artist_name").text
    minBPM = songInfo.find("bpm_min").text
    maxBPM = songInfo.find("bpm_max").text
    outputFolder += "/" + songInfo.find("ascii").text
    diffName = "infinite"
    if ("n.vox" in file):
        diffName = "novice"
    if ("a.vox" in file):
        diffName = "advanced"
    if ("e.vox" in file):
        diffName = "exhaust"
    if ("m.vox" in file):
        diffName = "maximum"
    diffList = xmls.find("difficulty")
    currDiff = diffList.find(diffName)
    level = (currDiff.find("difnum").text)
    effector = (currDiff.find("effected_by").text)
    fileName = outputFolder + "/" + getDifficultyKSHList(diffName) + ".ksh"
    outputOggFile = outputFolder + "/" + getDifficultyToInteger(diffName) +".ogg"
    outputPngFile = outputFolder + "/" + getDifficultyToInteger(diffName) +".png"
    diffSongExist = 0
    diffPngExist = 0
    if glob.glob(outputOggFile):
        diffSongExist = 1
    if glob.glob(outputPngFile):
        diffPngExist = 1
    createFileIfNotExist(fileName)
    with open(fileName, 'w+', encoding="utf-8-sig") as f:
        f.write(createPrefixVox(title, artist, minBPM, maxBPM, effector, diffName, level, diffSongExist, diffPngExist))
    #os.system("python v2k.py " + file + " " + fileName)
    os.system("python v2k.py " + file + " " + fileName)

def program():
    with open('music_db.xml', 'rb') as fp:
        # This is gross, but elemtree won't do it for us so whatever
        xmldata = fp.read().decode('shift_jisx0213')
        root = ET.fromstring(xmldata)
        outputFolder = "kshoutput/"
    for music_id in root:
        s = music_id.attrib['id']
        while (len(s) < 4):
            s = "0" + s
        #print(s, music_id[0][5].text)
        outputSongName = music_id.find("info").find("ascii").text
        songFolder = s + "_" + outputSongName
        folderName = "data/music/" + songFolder
        version = music_id.find("info").find("version").text

        if glob.glob(folderName):
            if version == "3":
                createFolderIfNotExist(outputFolder + "/" + outputSongName)
                for x in range(1,6):
                   if checkIfSpecificOggExist(folderName + "/" + songFolder, x) == 1:
                     runFFMPEGtoConvertSong(getSpecificDifficultySongSound(folderName + "/" + songFolder, x), outputFolder + "/" + outputSongName +"/" + str(x) + ".ogg")
                for x in range(1,6):
                    copyPNGs(folderName, outputFolder + "/" + outputSongName , str(x))
                for file in glob.glob(folderName + "/*.vox"):
                    createOutputSong(file, outputFolder, music_id)
                    runFFMPEGtoConvertSong(folderName + "/" + songFolder + ".s3v", outputFolder + "/" + outputSongName +"/music.ogg")
                
                 #print(folderName + "/" + songFolder + ".s3v")
                 #print(outputFolder + "/" + outputSongName +"/music.ogg")
                else:
                    print(folderName + " not found")



if (__name__ == "__main__"):
    USAGE = f"Usage: python {sys.argv[0]} [--help] | Use a number Between 1 and 6 corelating to the game version]"
    DUMBFUCK = "DONT USE N-0 YOU IDIOT"

    args = sys.argv[1:]
    if not args:
        raise SystemExit(USAGE)
    if args[0] == "--help":
        print(USAGE)
    if int(sys.argv[1]) > 5:
        raise SystemExit(DUMBFUCK)
    else:
        program()