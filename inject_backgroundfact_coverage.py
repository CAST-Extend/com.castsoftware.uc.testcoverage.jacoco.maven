import argparse
import logging
import logging.handlers
import re
import sys
import traceback
import os
import configparser

import xml.etree.ElementTree as ET
from utils.utils import RestUtils, AIPRestAPI, LogUtils

'''
 Author : MMR
 May 2023
'''

broundgrades = False
########################################################################


########################################################################
def init_parse_argument():
    # get arguments
    parser = argparse.ArgumentParser(add_help=False)
    requiredNamed = parser.add_argument_group('Required named arguments')
    requiredNamed.add_argument('-restapiurl', required=True, dest='restapiurl', help='Rest API URL using format https://demo-eu.castsoftware.com/CAST-RESTAPI or http://demo-eu.castsoftware.com/Engineering')
    requiredNamed.add_argument('-user', required=False, dest='user', help='Username')    
    requiredNamed.add_argument('-password', required=False, dest='password', help='Password')
    requiredNamed.add_argument('-apikey', required=False, dest='apikey', help='Api key')
    requiredNamed.add_argument('-applicationfilter', required=True, dest='applicationfilter', help='Application name regexp filter')
    requiredNamed.add_argument('-deployfolder', required=True, dest='deployfolder', help='Deploy folder')
    requiredNamed.add_argument('-metricid', required=True, dest='metricid', help='Background fact metric id for coverage')
    requiredNamed.add_argument('-log', required=True, dest='log', help='log file')
    requiredNamed.add_argument('-of', required=True, dest='outputfolder', help='output folder')    
    requiredNamed.add_argument('-loglevel', required=False, dest='loglevel', help='Log level (INFO|DEBUG) default = INFO')
    requiredNamed.add_argument('-extensioninstallationfolder', required=False, dest='extensioninstallationfolder', help='extension installation folder')

    return parser
########################################################################


if __name__ == '__main__':

    global logger
    # load the data or just generate an empty excel file
    loaddata = True
    # load only 10 metrics
    loadonlyXmetrics = True    
    # round the grades or not


    parser = init_parse_argument()
    args = parser.parse_args()
    restapiurl = args.restapiurl
    if restapiurl != None and restapiurl[-1:] == '/':
        # remove the trailing / 
        restapiurl = restapiurl[:-1] 
    user = 'N/A'
    if args.user != None: 
        user = args.user 
    password = 'N/A'
    if args.password != None: 
        password = args.password    
    apikey = 'N/A'
    if args.apikey != None: 
        apikey = args.apikey    
    log = args.log
    extensioninstallationfolder = "."
    if args.extensioninstallationfolder != None:
        extensioninstallationfolder = args.extensioninstallationfolder
    # add trailing / if not exist 
    if extensioninstallationfolder[-1:] != '/' and extensioninstallationfolder[-1:] != '\\' :
        extensioninstallationfolder += '/'
    
    outputfolder = args.outputfolder
    if not outputfolder.endswith('/') and not outputfolder.endswith('\\'):
        outputfolder += '/'
    
    applicationfilter = args.applicationfilter
    deployfolder = args.deployfolder
    metricid = args.metricid
    
    loglevel = "INFO"
    if args.loglevel != None and (args.loglevel == 'INFO' or args.loglevel == 'DEBUG'):
        loglevel = args.loglevel

    ###########################################################################

    # setup logging
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(log, mode="w")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if loglevel == 'INFO':
        logger.setLevel(logging.INFO)
    elif loglevel == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    try:
        # Version
        script_version = 'Unknown'
        try:
            pluginfile = extensioninstallationfolder + 'plugin.nuspec'
            LogUtils.logdebug(logger,pluginfile,True)
            tree = ET.parse(pluginfile)
            root = tree.getroot()
            namespace = "{http://schemas.microsoft.com/packaging/2011/08/nuspec.xsd}"
            for versiontag in root.findall('{0}metadata/{0}version'.format(namespace)):
                script_version = versiontag.text
        except:
            None 
        
        # log params
        logger.info('********************************************')
        LogUtils.loginfo(logger,'version='+script_version,True)
        logger.info('python version='+sys.version)
        logger.info('****************** params ******************')
        LogUtils.loginfo(logger, 'restapiurl='+restapiurl, True)
        LogUtils.loginfo(logger,'user='+str(user),True)
        if password == None or password == "N/A":
            logger.info('password=' + password)
        else: 
            logger.info('password=*******')
        if apikey == None or apikey== "N/A":
            logger.info('apikey=N/A')
        else:
            logger.info('apikey=*******') 
        LogUtils.loginfo(logger,'log file='+log,True)
        LogUtils.loginfo(logger, 'output folder='+str(outputfolder), True)
        logger.info('****************** params ******************')
        logger.info('metricid='+metricid)
        logger.info('deployfolder='+deployfolder)
        logger.info('extensioninstallationfolder='+extensioninstallationfolder)
        logger.info('log level='+loglevel)
        logger.info('********************************************')
        
        ini_coveragefile = deployfolder + '/coverageResults.ini'
        
        LogUtils.loginfo(logger, 'Initialization', True) 
        rest_utils = RestUtils(logger, restapiurl, RestUtils.CLIENT_REQUESTS, user, password, apikey, uselocalcache=None, cachefolder=None, extensionid='com.castsoftware.uc.testcoverage')
        rest_utils.open_session()
        rest_service_aip = AIPRestAPI(rest_utils) 
        
        # Few checks on the server 
        server = rest_service_aip.get_server()
        if server != None: logger.info('server version=%s, memory (free)=%s' % (str(server.version), str(server.freememory)))
        
        # retrieve the domains & the applications in those domains 
        listdomains = rest_service_aip.get_domains()
        
        bAEDdomainFound = False
        for it_domain in listdomains:
            if not it_domain.isAAD():
                bAEDdomainFound = True
                
        idomain = 0            
        for domain in listdomains:
            idomain += 1
            LogUtils.loginfo(logger, "Domain " + domain.name + " | progress:" + str(idomain) + "/" + str(len(listdomains)), True)
 
            # all domains
            listapplications = rest_service_aip.get_applications(domain)
            for objapp in listapplications:
                if applicationfilter != None and not re.match(applicationfilter, objapp.name):
                    logger.info('Skipping application : ' + objapp.name)
                    continue                
                elif applicationfilter == None or applicationfilter == '' or re.match(applicationfilter, objapp.name):
                    LogUtils.loginfo(logger, "Processing application " + objapp.name, True)
                    # snapshot list
                    logger.info('Loading the application snapshot')
                    listsnapshots = rest_service_aip.get_application_snapshots(domain.name, objapp.id)
                    
                    for objsnapshot in listsnapshots:
                        logger.info("    Snapshot " + objsnapshot.href + '#' + objsnapshot.snapshotid)
                        if os.path.isfile(ini_coveragefile):
                            config = configparser.ConfigParser()
                            config.read(ini_coveragefile)
                            overall_class_test_coverage = config['DEFAULT']['overall_class_test_coverage']
                            application_name = config['DEFAULT']['application_name']
                            schema_central = config['DEFAULT']['schema_central']                                
                            logger.info("    overall_class_test_coverage to be loaded in the background fact metric=%s for application %s | schema %s" % (str(overall_class_test_coverage), application_name, schema_central) )
                            
                            #modulelist = rest_service_aip.get_application_modules(domain.name, objapp.id, objsnapshot.snapshotid)
                            # modulelist for all snapshot
                            modulelist = rest_service_aip.get_application_modules(domain.name, objapp.id)
                            rest_service_aip.update_backgroundfactmetric(domain.name, objapp.id, objsnapshot.snapshotid, metricid, overall_class_test_coverage, modulelist, schema_central, application_name)
                            LogUtils.loginfo(logger, "  Background facts loaded", True)

                        # process only last snapshot
                        break
                                        
    except: # catch *all* exceptions
        tb = traceback.format_exc()
        #e = sys.exc_info()[0]
        LogUtils.logerror(logger, '  Error during the processing %s' % tb,True)

    LogUtils.loginfo(logger,'Done !',True)