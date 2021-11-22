import xml.etree.ElementTree as ET

with open('music_db.xml', 'rb') as fp:
        # This is gross, but elemtree won't do it for us so whatever
        xmldata = fp.read().decode('shift_jisx0213')
        root = ET.fromstring(xmldata)

for music_id in root:
    s = music_id.attrib['id']
    while (len(s) < 4):
        s = "0" + s
    #print(s, music_id[0][5].text)
    outputSongName = music_id.find("info").find("ascii").text
    print(outputSongName)