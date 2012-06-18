'''
Created on Mar 24, 2012

@author: mshulman
'''
import os
import urllib
import urllib2
import cgi
from cgi import escape
import xml.sax
import random
# ######################################################################################
#  Class        : VendorRequest
#  Version      : 1.0 Release 1
#  Title        : Request BU UIS Service.
#  Description  : Generates and sends XML request to BU UIS for service (Python version)
#  Written      : 04/13/2012 by Michael sHulman
# ######################################################################################

class VendorRequest:
    __VERSION                       = '1.0'
    __REQUEST_TEMPLATE_NAME         = r'request.xmt';
    __DEFAULT_SYNC_METHOD           = 'GET';
    __DEFAULT_XML_REQUEST_SCHEMA    = 'http://www.bu.edu/uis/XmlGateway';
    __DEFAULT_XML_REQUEST_SCHEMA_LOC= 'http://www.bu.edu/link/system/schemas/XmlGateway/Request.xsd';

#
# Constructor
#
    def __init__(self):
        self.params = {}
        self.syncParams = {}
        self.errorMsg =""
        self.errorInd = 0
        self.customData = ""
        self.session = ""
        self.syncMethod = ""
        self.syncUrl = ""
        self.url = ""
        self.xml = ""
        self.xmlRequestSchema = ""
        self.xmlRequestSchemaLoc = ""
    #
    # Add one parameter to send to BU Computing Services
    #
    def addParameter(self, param , value):
        if self.params.has_key(param):
            self.params[param].append(value)
        else:
            self.params[param] = [value]
    #
    # Add one synchronization parameter to send to BU Computing Services to regain
    # the control back after asynchronous process (LOGIN) will be completed
    #
    def addSyncParameter(self, param , value):
        if self.syncParams.has_key(param):
            self.syncParams[param].append(value)
        else:
            self.syncParams[param] = [value]
    #
    # Retrieves error message
    #
    def getErrorMsg(self):
        return self.errorMsg
    #
    # Sends request XML document to BU Computing Services and returns the response as
    # a BuResponse object.
    #
    def getResponse(self):
        if self.xml =="" :
            self.__createXml()            # if inputXml is not set we create it
        if self.errorInd == 1:
            return
        requestContent = self.url + '/' + str(random.randint(0,10000000)) + '?' + self.__encodeUrl(self.xml)
        request = urllib2.Request(requestContent)
        response = urllib2.urlopen(request)
        return BuResponse(response.read())
    #
    # Checks for errors
    #
    def isError(self):
        return self.errorInd
    #
    # Sets Custom Data to send to BU Computing Services.
    #
    def setCustomData (self, customData):
        self.customData = "<![CDATA[%s]]>" % customData
    #
    # Sets one single value parameter to send to BU Computing Services.
    #
    def setParameter(self, param, value):
        self.params [param] = [value]
    #
    # Sets all parameters to send to BU Computing Services.
    #
    def setParameters(self, params):
        self.params = params
    #
    # Sets one single or multi value parameter to send to BU Computing Services.
    #
    def setParameterValues(self, param , values):
        self.params[param] = values
    #
    # Sets Session for current Vendor's session with BU Computing Services
    #
    def setSession(self, session):
        self.session = session
    #
    # Sets method to be used to send HTTP(s) message to Vendor application
    # to regain the control back after asynchronous process (LOGIN) will be completed.
    #
    def setSyncMethod(self, method):
        self.syncMethod = method
    #
    # Sets one single value synchronization parameter to send to BU Computing Services
    # to regain the control back after asynchronous process (LOGIN) will be completed.
    #
    def setSyncParameter(self, param , value):
        self.syncParams[param] = [value]
    #
    # Sets one single or multi value synchronization parameter to send to BU Computing
    # Services to regain the control back after asynchronous process (LOGIN) will be
    # completed.
    #
    def setSyncParameterValues(self, param , values):
        self.syncParams[param] = values
    #
    # Sets all synchronization parameters to send to BU Computing Services to regain
    # the control back after asynchronous process (LOGIN) will be completed.
    #
    def setSyncParameters(self, params):
        self.syncParams = params
    #
    # Sets URL to Vendor application to regain the control back after asynchronous
    # process (LOGIN) will be completed.
    #
    def setSyncUrl(self, url):
        tempUrl = url
        if (tempUrl == ''):                            # vendor wants default syncUrl
            self.syncMethod = escape(os.environ['REQUEST_METHOD'])
            if self.syncMethod == "POST":
# do samething with post
                postParams = cgi.FieldStorage()
                keys = postParams.keys()
                keys.sort()
                for k in keys:
                    self.SyncParameter(k , postParams[k])
            if os.environ['HTTPS'] != 'off':
                tempUrl = 'https://'
            else:
                tempUrl = 'http://'
            tempUrl += os.environ['SERVER_NAME'] + ':' + os.environ['SERVER_PORT'] + os.environ['SCRIPT_NAME'];
            if os.environ['QUERY_STRING'] != '':
                tempUrl += '?' + os.environ['QUERY_STRING']

        self.syncUrl = self.__encodeXml(tempUrl)
    #
    # Sets URL to BU Computing Services
    #
    def setUrl(self, url):
        self.url = url
    #
    # Sets the request XML document to be send within the body of HTTP(s) request to
    # BU Computing Services.
    #
    def setXml(self, xml):
        self.xml = xml
    #
    # Sets the request XML schema
    #
    def setXmlRequestSchema(self, xmlRequestSchema):
        self.xmlRequestSchema = xmlRequestSchema
    #.
    # Sets the request XML schema location
    #
    def setXmlRequestSchemaLoc(self,xmlRequestSchemaLoc):
        self.xmlRequestSchemaLoc = xmlRequestSchemaLoc
    #
    # Create Input Xml
    #
    def __createXml(self):
        if self.syncMethod == "":
            self.syncMethod = VendorRequest.__DEFAULT_SYNC_METHOD;
        if self.xmlRequestSchema == "":
            self.xmlRequestSchema= VendorRequest.__DEFAULT_XML_REQUEST_SCHEMA;
        if self.xmlRequestSchemaLoc == "":
            self.xmlRequestSchemaLoc = VendorRequest.__DEFAULT_XML_REQUEST_SCHEMA_LOC;
        parameters = self.__createParamString(self.params)
        syncParameters = self.__createParamString(self.syncParams)
        template_loc =  os.path.dirname(__file__) + "/" + VendorRequest.__REQUEST_TEMPLATE_NAME
        try:
            template = open(template_loc, "r")
        except IOError:
            self.errorInd = 1
            self.errorMsg = "Could not open file: %s" % VendorRequest.__REQUEST_TEMPLATE_NAME
            return
        while 1:
            line = template.readline()
            if not line:
                break
            self.xml += line

        self.xml = self.xml.replace('!SESSION_KEY!',self.session)
        self.xml = self.xml.replace('!VERSION!',VendorRequest.__VERSION)
        self.xml = self.xml.replace('!XML_REQUEST_SCHEMA!',self.xmlRequestSchema)
        self.xml = self.xml.replace('!XML_REQUEST_SCHEMA_LOC!',self.xmlRequestSchemaLoc)
        self.xml = self.xml.replace('!SYNC_URL!',self.syncUrl)
        self.xml = self.xml.replace('!SYNC_METHOD!',self.syncMethod)
        self.xml = self.xml.replace('!PARAMETERS!',parameters)
        self.xml = self.xml.replace('!SYNC_PARAMETERS!',syncParameters)
        self.xml = self.xml.replace('!CUSTOM_DATA!',self.customData)

    #
    # Create Param String
    #
    def __createParamString(self,params):
        paramString = ""
        names = params.keys()
        names.sort()
        for name in names:
            for value in params[name]:
                encodeName = self.__encodeXml(name)
                encodeValue = self.__encodeXml(value)
                paramString += "\n\t\t<param name='%s' value='%s'/>" % (encodeName, encodeValue)
        return paramString;

    #
    # Return the passed string after replacing all special and non-printable characters
    # with their %XX hex values (URL-encoded)
    #
    def __encodeUrl(self, content):
        return urllib.quote(content)

    #
    # Encode XML
    #
    def __encodeXml(self,text):
        text = text.replace('&', '&amp;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        text = text.replace(">", '&gt;')
        text = text.replace("<", '&lt;')
        return text

# ######################################################################################
#  Class        : BuResponse
#  Version      : 1.0 Release 1
#  Title        : Response from BU UIS Service.
#  Description  : This interface provides methods to parse a response XML document
#                 from BU Computing Services
#  Written      : 04/13/2012 by Michael sHulman
# ######################################################################################
class BuResponse():
    __VERSION = '1.0'
#
# Constructor
#
    def __init__(self,xmlContent):
        self.xmlContent = xmlContent
        self.parsed = 0
        self.mapping = {}

    def getAlias(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['alias']

    #
    # Retrieves custom data from BU Computing services response
    #
    def getCustomData(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['custom_data']

    #
    # Retrieves client's email address if available
    #
    def getEmail(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['email']

    #
    # Retrieves the response HTML page from BU Computing Services.
    #
    def getHtml(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['html']

    #
    # Retrieves client's BU unique ID (UID).
    #
    def getId(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['id']

    #
    # Retrieves the response message from BU Computing Services.
    #
    def getMessage(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['message']

    #
    #  Retrieves client's Full Name
    #
    def getName(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['name']

    #
    # Retrieves value for one particaular parameter from BU Computing Services response
    #
    def getParameter(self,name) :
        if not self.parsed: self.__parseContent()
        # simplify when single array member
        return self.mapping['params'][name][0]
    #
    # Retrieves list of names for all params from BU Computing Services response.
    #
    def getParameterNames(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['params'].keys()

    #
    # Retrieves list of all values for one particaular parameter from BU Computing
    # Services response.
    #
    def getParameterValues(self,name) :
        if not self.parsed: self.__parseContent()
        return self.mapping['params'][name]
    #
    # Retrieves the value of BU WebLink session key for the current request.
    #
    def getSession(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['session']
    #
    # Retrieves the sub_type of BU response.
    #
    def getSubType(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['subtype']
    #
    # Retrieves the transaction of BU response.
    #
    def getTransaction(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['transaction']
    #
    # Retrieves the type of BU response.
    #
    def getType(self) :
        if not self.parsed: self.__parseContent()
        if self.mapping['xsi_type'] != "" :
            return self.mapping['xsi_type']
        else :
            return self.mapping['type']

    # Retrieves the url to BU "PreLogin" Service.
    #
    def getUrl(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['url']

    #
    # Retrieves the version of BU Response XML document
    #
    def getVersion(self) :
        if not self.parsed: self.__parseContent()
        return self.mapping['version']
    #
    # Retrieves the response XML document for future 'manual' processing without
    # using most of current interface methods.
    #
    def getXml(self) :
        return self.xmlContent
    #
    # Parse Content
    #
    def __parseContent(self) :
        self.parsed = 1
        handler = BuResponseHandler()
        xml.sax.parseString(self.xmlContent, handler)
        self.mapping = handler.mapping

class BuResponseHandler( xml.sax.ContentHandler):
    __VERSION = '1.0'

    def __init__(self):
        self.mapping = {}
        self.currenttag = ''
        self.paramsElementInd = 0

    def startElement(self, tag, attributes) :
        self.currenttag = tag
        if self.currenttag == 'bu_uis_output':
            try:
                self.mapping['version']    = attributes['version']
            except KeyError:
                self.mapping['version']    = ''
            try:
                self.mapping['session']     = attributes['session']
            except KeyError:
                self.mapping['session']     = ''
            try:
                self.mapping['xsi_type']     = attributes['xsi:type']
            except KeyError:
                self.mapping['xsi_type']     = ''
            try:
                self.mapping['type']         = attributes['type']
            except KeyError:
                self.mapping['type']         = ''
            try:
                self.mapping['subtype']     = attributes['subtype']
            except KeyError:
                self.mapping['subtype']     = ''
            try:
                self.mapping['alias']     = attributes['alias']
            except KeyError:
                self.mapping['alias']     = ''
            try:
                self.mapping['id']         = attributes['id']
            except KeyError:
                self.mapping['id']         = ''
            try:
                self.mapping['name']         = attributes['name']
            except KeyError:
                self.mapping['name']         = ''
            try:
                self.mapping['email']     = attributes['email']
            except KeyError:
                self.mapping['email']     = ''
            try:
                self.mapping['transaction']     = attributes['transaction']
            except KeyError:
                self.mapping['transaction']     = ''
        if ( tag == 'html' ) :
            try:
                self.mapping['url']         = attributes['url']
            except KeyError:
                self.mapping['url']         = ''
        if tag == 'parameters':
                self.paramsElementInd = 1
                self.mapping['params'] = {}
        if tag == 'param' and self.paramsElementInd :
            try:
                self.mapping['params'][attributes['name']]
            except KeyError:
                self.mapping['params'][attributes['name']] = []
            self.mapping['params'][attributes['name']].append(attributes['value'])

    def characters(self, content) :
        if self.currenttag == 'message':
            try:
                self.mapping['message'] += content
            except KeyError:
                self.mapping['message'] = content

        if self.currenttag  == 'html':
            try:
                self.mapping['html'] += content
            except KeyError:
                self.mapping['html'] = content

        if self.currenttag  == 'custom_data':
            try:
                self.mapping['custom_data'] += content
            except KeyError:
                self.mapping['custom_data'] = content

    def endElement (self, tag) :
        if self.currenttag  == 'parameters':
            self.paramsElementInd = 0
