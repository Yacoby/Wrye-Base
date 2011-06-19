import re
import os
import locale
import cPickle

import conf

from util import Encode

reTrans = re.compile(r'^([ :=\.]*)(.+?)([ :=\.]*$)')
def compileTranslator(txtPath,pklPath):
    """Compiles specified txtFile into pklFile."""
    reSource = re.compile(r'^=== ')
    reValue = re.compile(r'^>>>>\s*$')
    #--Scan text file
    translator = {}
    def addTranslation(key,value):
        key,value   = key[:-1],value[:-1]
        if key and value:
            key = reTrans.match(key).group(2)
            value = reTrans.match(value).group(2)
            translator[key] = value
    key,value,mode = '','',0
    textFile = file(txtPath)
    for line in textFile:
        #--Begin key input?
        if reSource.match(line):
            addTranslation(key,value)
            key,value,mode = '','',1
        #--Begin value input?
        elif reValue.match(line):
            mode = 2
        elif mode == 1:
            key += line
        elif mode == 2:
            value += line
    addTranslation(key,value) #--In case missed last pair
    textFile.close()
    #--Write translator to pickle
    filePath = pklPath
    tempPath = filePath+'.tmp'
    cPickle.dump(translator,open(tempPath,'w'))
    if os.path.exists(filePath): os.remove(filePath)
    os.rename(tempPath,filePath)

#--Do translator test and set
if locale.getlocale() == (None,None):
    locale.setlocale(locale.LC_ALL,'')
language = locale.getlocale()[0].split('_',1)[0]
if language.lower() == 'german': language = 'de' #--Hack for German speakers who aren't 'DE'.
languagePkl, languageTxt = (os.path.join('data',language+ext) for ext in ('.pkl','.txt'))
#--Recompile pkl file?
if os.path.exists(languageTxt) and (
    not os.path.exists(languagePkl) or (
        os.path.getmtime(languageTxt) > os.path.getmtime(languagePkl)
        )
    ):
    compileTranslator(languageTxt,languagePkl)
#--Use dictionary from pickle as translator
if os.path.exists(languagePkl):
    pklFile = open(languagePkl)
    reEscQuote = re.compile(r"\\'")
    _translator = cPickle.load(pklFile)
    pklFile.close()
    def _(text,encode=True):
        text = Encode(text,'mbcs')
        if encode: text = reEscQuote.sub("'",text.encode('string_escape'))
        head,core,tail = reTrans.match(text).groups()
        if core and core in _translator:
            text = head+_translator[core]+tail
        if encode: text = text.decode('string_escape')
        if conf.useUnicode: text = unicode(text,'mbcs')
        return text
else:
    def _(text,encode=True): return text
