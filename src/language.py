'''
Created on 23.01.2010

@author: Iman Karim (ikarim2s@smail.inf.fh-brs.de)
'''

import xml.dom.minidom
import base64
import sys, os
from baseClass import baseClass
from baseTools import baseTools
import random

def getXMLNode(item, nodename):
    for child in item.childNodes:
        if (child.nodeName != "#text"):
            if (child.nodeName == nodename):
                return(child)
    return(None)

def getXMLNodes(item, nodename):
    ret = []
    for child in item.childNodes:
        if (child.nodeName != "#text"):
            if (child.nodeName == nodename):
                ret.append(child)
    return(ret)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc


class XML2Config(baseClass):

    def _load(self):
        self.langsets = {}
        self.xmlfile = os.path.join(sys.path[0], "config", "generic.xml")
        print self.xmlfile
        self.XML_Generic = None
        self.XML_Rootitem = None


        self.relative_files = []
        self.absolute_files = []
        self.remote_files   = []
        self.log_files      = []
    
        self.shellquiz_code = None
    
        self.__init_xmlresult()
   
        #sys.exit(0)
    
    def __init_xmlresult(self):
        xmlfile = self.xmlfile
        if (os.path.exists(xmlfile)):
            self.XML_Generic = xml.dom.minidom.parse(xmlfile)
            self.XML_Rootitem = self.XML_Generic.firstChild
            
            rel_node = getXMLNode(self.XML_Rootitem, "relative_files")
            rel_files = getXMLNodes(rel_node, "file")
            for f in rel_files:
                self.relative_files.append(fiFile(f, self.config))
            
            abs_node = getXMLNode(self.XML_Rootitem, "absolute_files")
            abs_files = getXMLNodes(abs_node, "file")
            for f in abs_files:
                self.absolute_files.append(fiFile(f, self.config))
            
            rem_node = getXMLNode(self.XML_Rootitem, "remote_files")
            rem_files = getXMLNodes(rem_node, "file")
            for f in rem_files:
                self.remote_files.append(fiFile(f, self.config))
            
            log_node = getXMLNode(self.XML_Rootitem, "log_files")
            log_files = getXMLNodes(log_node, "file")
            for f in log_files:
                self.log_files.append(fiFile(f, self.config))
            
            
            methods_node = getXMLNode(self.XML_Rootitem, "methods")
            quiz_node = getXMLNode(methods_node, "shellquiz")
            self.shellquiz_code = base64.b64decode(quiz_node.getAttribute("source"))
            
            self.__loadLanguageSets()
        else:
            print "generic.xml file not found! This file is very important!"
            sys.exit(1)
        
    def __loadLanguageSets(self):
        langnodes = getXMLNode(self.XML_Rootitem, "languagesets")
        for c in langnodes.childNodes:
            if (c.nodeName == "language"):
                langname = c.getAttribute("name")
                langfile = c.getAttribute("langfile")
                self.langsets[langname] = baseLanguage(langname, langfile, self.config)
    
    def generateShellQuiz(self):
        ret = None
        exec(self.shellquiz_code)
        return(ret)
    
    def getAllLangSets(self):
        return(self.langsets)
    
    def getAllReadfileRegex(self):
        ret = []
        langs = self.getAllLangSets()
        for k,v in langs.items():
            readfile_regex = v.getReadfileDetectors()
            for reg in readfile_regex:
                ret.append((k, reg))
        return(ret)
    
    def getAllSniperRegex(self):
        ret = []
        langs = self.getAllLangSets()
        for k,v in langs.items():
            readfile_regex = v.getSniper()
            ret.append((k, readfile_regex))
        return(ret)
    
    def getRelativeFiles(self, lang=None):
        ret = []
        for f in self.relative_files:
            ret.append(f)
            
        if (lang != None):
            for f in self.langsets[lang].getRelativeFiles():
                ret.append(f)
        return(ret)
    
        
    def getAbsoluteFiles(self, lang=None):
        ret = []
        for f in self.absolute_files:
            ret.append(f)
            
        if (lang != None):
            for f in self.langsets[lang].getAbsoluteFiles():
                ret.append(f)
        return(ret)
    
        
    def getLogFiles(self, lang=None):
        ret = []
        for f in self.log_files:
            ret.append(f)
            
        if (lang != None):
            for f in self.langsets[lang].getLogFiles():
                ret.append(f)
        return(ret)
    
        
    def getRemoteFiles(self, lang=None):
        ret = []
        for f in self.remote_files:
            ret.append(f)
            
        if (lang != None):
            for f in self.langsets[lang].getRemoteFiles():
                ret.append(f)
        return(ret)
    
class baseLanguage(baseTools):
    
    def __init__(self, langname, langfile, config):
        baseTools.config = config
        langfile = os.path.join(sys.path[0], "config", langfile)
        self.XML_Langfile = None
        self.XML_Rootitem = None
        
        if (os.path.exists(langfile)):
            self.XML_Langfile = xml.dom.minidom.parse(langfile)
            self.XML_Rootitem = self.XML_Langfile.firstChild
        else:
            print "%s file not found!" %(langfile)
            sys.exit(1)
        
        self.LanguageName = langname
        
        self.relative_files = []
        self.absolute_files = []
        self.remote_files   = []
        self.log_files      = []
        
        self.exec_methods   = []
        self.payloads       = []
        
        self.sniper_regex   = None
        
        self.quiz_function  = None
        
        self.detector_include  = []
        self.detector_readfile = [] 
    
        self.__populate()
    
    def getName(self):
        return(self.LanguageName)
    
    def getSniper(self):
        return(self.sniper_regex)
    
    def getExecMethods(self):
        return(self.exec_methods)
    
    def getPayloads(self):
        return(self.payloads)
    
    def getRelativeFiles(self):
        return(self.relative_files)
    
    def getAbsoluteFiles(self):
        return(self.absolute_files)
    
    def getRemoteFiles(self):
        return(self.remote_files)
    
    def getLogFiles(self):
        return(self.log_files)
    
    def getIncludeDetectors(self):
        return(self.detector_include)
    
    def getReadfileDetectors(self):
        return(self.detector_readfile)
    
    def getQuizSource(self):
        return(self.quiz_function)
    
    def generateQuiz(self):
        ret = None
        exec(self.quiz_function)
        return(ret)
    
    def __populate(self):
        rel_node = getXMLNode(self.XML_Rootitem, "relative_files")
        rel_files = getXMLNodes(rel_node, "file")
        for f in rel_files:
            self.relative_files.append(fiFile(f, self.config))
        
        abs_node = getXMLNode(self.XML_Rootitem, "absolute_files")
        abs_files = getXMLNodes(abs_node, "file")
        for f in abs_files:
            self.absolute_files.append(fiFile(f, self.config))
        
        rem_node = getXMLNode(self.XML_Rootitem, "remote_files")
        rem_files = getXMLNodes(rem_node, "file")
        for f in rem_files:
            self.remote_files.append(fiFile(f, self.config))
        
        log_node = getXMLNode(self.XML_Rootitem, "log_files")
        log_files = getXMLNodes(log_node, "file")
        for f in log_files:
            self.log_files.append(fiFile(f, self.config))
        
        exec_methods = getXMLNode(self.XML_Rootitem, "exec_methods")
        exec_nodes = getXMLNodes(exec_methods, "exec")
        for f in exec_nodes:
            self.exec_methods.append(fiExecMethod(f, self.config))
            
        payloads = getXMLNode(self.XML_Rootitem, "payloads")
        payload_nodes = getXMLNodes(payloads, "payload")
        for f in payload_nodes:
            self.payloads.append(fiPayload(f, self.config))
        
        
        self.sniper_regex = getXMLNode(self.XML_Rootitem, "snipe").getAttribute("regex")
        
        methods_node = getXMLNode(self.XML_Rootitem, "methods")
        quiz_node = getXMLNode(methods_node, "quiz")
        quiz_code = base64.b64decode(quiz_node.getAttribute("source"))
        
        self.quiz_function = quiz_code
        
        detectors_node = getXMLNode(self.XML_Rootitem, "detectors")
        include_patterns = getXMLNode(detectors_node, "include_patterns")
        pattern_nodes =  getXMLNodes(include_patterns, "pattern")
        for f in pattern_nodes:
            self.detector_include.append(f.getAttribute("regex"))
            
        
        readfile_patterns = getXMLNode(detectors_node, "readfile_patterns")
        pattern_nodes =  getXMLNodes(readfile_patterns, "pattern")
        for f in pattern_nodes:
            self.detector_readfile.append(str(f.getAttribute("regex")))
        
class fiPayload(baseTools):
    def __init__(self, xmlPayload, config):
        self.initLog(config)
        self.name = xmlPayload.getAttribute("name")
        self.doBase64 = (xmlPayload.getAttribute("dobase64") == "1")
        self.inputlist = getXMLNodes(xmlPayload, "input")
        self.source = getXMLNode(xmlPayload, "code").getAttribute("source")
        self._log("fimap PayloadObject loaded: %s" %(self.name), self.LOG_DEVEL)
        
    def getName(self):
        return(self.name)
    
    def getSource(self):
        return(self.source)
    
    def generatePayload(self):
        ret = self.source
        for q in self.inputlist:
            type_ = q.getAttribute("type")
            if (type_ == "question"):
                question = q.getAttribute("text")
                placeholder = q.getAttribute("placeholder")
                inp = raw_input(question)
                if (self.doBase64):
                    inp = base64.b64encode(inp)
                ret = self.source.replace(placeholder, inp)
            elif (type_ == "info"):
                info = q.getAttribute("text")
                print info
            elif (type_ == "wait"):
                info = q.getAttribute("text")
                raw_input(info)
        return(ret)
                    

class fiExecMethod(baseTools):
    def __init__(self, xmlExecMethod, config):
        self.initLog(config)
        self.execname   = xmlExecMethod.getAttribute("name")
        self.execsource = xmlExecMethod.getAttribute("source")
        self._log("fimap ExecObject loaded: %s" %(self.execname), self.LOG_DEVEL)
        
    def getSource(self):
        return(self.execsource)
    
    def getName(self):
        return(self.execname)
    
    def generatePayload(self, command, doBase64):
        if (doBase64):
            command = base64.b64encode(command)
        payload = self.getSource().replace("__PAYLOAD__", command)
        return(payload)
        
class fiFile(baseTools):
    def __init__(self, xmlFile, config):
        self.initLog(config)
        self.filepath = xmlFile.getAttribute("path")
        self.postdata = xmlFile.getAttribute("post")
        self.findstr  = xmlFile.getAttribute("find")
        self.flags    = xmlFile.getAttribute("flags")
        self._log("fimap FileObject loaded: %s" %(self.filepath), self.LOG_DEVEL)
        
    def getFilepath(self):
        return(self.filepath)
    
    def getPostData(self):
        return(self.postdata)
    
    def getFindStr(self):
        return(self.findstr)
    
    def getFlags(self):
        return(self.flags)
    
    def containsFlag(self, flag):
        return (flag in self.flags)
    
    def isInjected(self, content):
        return (content.find(self.findstr) != -1)