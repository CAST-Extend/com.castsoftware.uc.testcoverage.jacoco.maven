import cast_upgrade_1_6_13  # @UnusedImport
from cast.application import ApplicationLevelExtension, create_link
import logging 
import os
import traceback
from csv import reader
import configparser

"""
class TestCoverageApplication
"""
    
class TestCoverageApplication(ApplicationLevelExtension):

    ###################################################################################################        
    # metric id used for background fact code coverage metric to feed the custom tile in Standalone Health Dashboard 
    code_coverage_metric = 66004
    threshold_coverage_class = 0.5
    
    def __init__(self):
        # setting the value for unit testing, will be overwitten by standard analysis
        self.default_deploy_folder = 'C:/Users/MMR/Documents/ws_eclipse/ws_misc/com.castsoftware.uc.testcoverage.jacoco.maven/tests/com.vogella.junit.first'
        self.dict_classes = {}
        self.dict_methods = {}
        self.dict_packages = {}
        # overall coverage
        self.overall_class_test_coverage = 0.0
        # coverage per java class
        self.class_coverage = {}
        
    ###################################################################################################        
    def get_deploy_folder(self, application):
        deploy_folder = self.default_deploy_folder 
        if application.get_application_configuration() != None:
            # for local debug
            deploy_folder = application.get_application_configuration().deploy_path
            #application_name = application.get_managment_base().get_applications()[0].name
            if not (deploy_folder.endswith("/") or deploy_folder.endswith("\\")):
                deploy_folder += "/"
            #deploy_folder += application_name + "/" 
            
        logging.debug ('Found  deploy_folder as ---> ' + str(deploy_folder))
        return deploy_folder
    ###################################################################################################        

    def find_jacoco_files(self, application, file_end_pattern):
        deploy_folder = self.get_deploy_folder(application) 
        
        filepathset = []
        
        #stop = False
        for root, subdirs, files in os.walk(deploy_folder):
            #if stop: break
            #logging.debug('root %s ' + root)
            # List subdirectories
            #for subdir in subdirs:
            #    logging.debug('\t- subdirectory ' + subdir)
            # List of files located recursively in the root folder
            for filename in files:
                #if stop: break
                file_path = os.path.join(root, filename)
                if "site\\jacoco\\" in file_path and filename.endswith('jacoco.csv'): 
                    #or filename.endswith('jacoco.xml') or filename.endswith('.html') ):
                    logging.debug('\t- file ' + file_path)
                    filepathset.append(file_path)
                """
                if filename.endswith(file_end_pattern):
                    # accept multiple .csv files, as Prolint likes to process chunks...
                    _filename = deploy_folder + filename
                    logging.info ('Found file_path as ---> ' + str(file_path))
                    filepathset.append(file_path)
                    # keep only 1 file
                    stop = True
                """
        return filepathset
    ###################################################################################################
    def compute_code_coverage(self, branch_missed, branch_covered, line_missed, line_covered):
        '''
        https://docs.sonarqube.org/latest/user-guide/metric-definitions/
        Coverage (coverage): A mix of Line coverage and Condition coverage. It's goal is to provide an even more accurate answer the question  'How much of the source code has been covered by the unit tests?'.
        Coverage = (CT + CF + LC)/(2*B + EL)
        where:
        CT = conditions that have been evaluated to 'true' at least once
        CF = conditions that have been evaluated to 'false' at least once
        LC = covered lines = linestocover - uncovered_lines
        B = total number of conditions
        EL = total number of executable lines (lines_to_cover)
        
        https://community.sonarsource.com/t/sonarqube-calculation-coverage/21804/2
        Here's an easier way to think about it (PR to the docs coming eventually)
        Coverage (coverage)
        It is a mix of Line coverage and Condition coverage. Its goal is to provide an even more accurate answer to the following question: How much of the source code has been covered by the unit tests?
    
        Coverage = (Covered Conditions + Covered Lines)/(Conditions to Cover + Lines to Cover)
        where
            Covered Conditions = conditions_to_cover - uncovered conditions
            Covered Lines = lines_to_cover - uncovered_lines
            Conditions to Cover = total number of conditions ( conditions_to_cover )
            Lines to Cover = total number of executable lines ( lines_to_cover )
    
        Alternatively:
        Coverage = ( conditions_to_cover - uncovered conditions + lines_to_cover - uncovered_lines ) / ( conditions_to_cover + lines_to_cover )

        '''
    
        denum = (int(branch_covered) + int(branch_missed) + int(line_missed) + int(line_covered))
        class_test_coverage = 100
        #if no instruction, % is 100%
        if denum != 0: 
            class_test_coverage = ((int (branch_covered) + int(line_covered)) / denum) *  100 
        return round(class_test_coverage,1)

    ###################################################################################################
    
    
    def end_application(self, application):
        logging.info("*********************************************************************************") 
        logging.info("TestCoverageApplication : running code at the end of an application")
        config = configparser.ConfigParser()
        config['DEFAULT']['coverageTool'] = 'Jacoco'
        ini_file_path = self.get_deploy_folder(application) + 'coverageResults.ini'
        application_name = application.get_managment_base().get_applications()[0].name
        #schema_mngt = application.get_managment_base().name
        #schema_central = application.get_dashboard_services().name
        schema_central = application.get_application_configuration().get_dashboard_services()[0].name
        logging.info("Will write to output file %s" % ini_file_path)
        logging.info("application_name %s" % application_name)
        logging.info("schema_central %s" % schema_central)
    
        
        application.declare_property_ownership('Coverage_Cat.coverageTool',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.coverageRatio',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.isjacococovered',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.branchToCover',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.branchMissed',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.branchCovered',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.lineToCover',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.lineMissed',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])
        application.declare_property_ownership('Coverage_Cat.lineCovered',['JV_CLASS','JV_GENERIC_CLASS','JV_INST_CLASS'])        
        
        # Java classes 
        for obj in application.objects().has_type(['JV_CLASS','JV_GENERIC_CLASS', 'JV_INST_CLASS']).load_positions():
            #logging.debug('class %s' % obj.get_fullname())
            self.dict_classes[obj.get_fullname()]= obj   
        """
        # Java methods 
        for obj in application.objects().has_type(['JV_METHOD','JV_GENERIC_METHOD', 'JV_INST_METHOD'].load_positions()):
            #logging.debug('method %s' % obj.get_fullname())
            obj.load_positions()
            self.dict_methods[obj.get_fullname()]= obj   
            
        # Java packages
        for obj in application.objects().has_type(['JV_PACKAGE'].load_positions()):
            #logging.debug('package %s' % obj.get_fullname())
            obj.load_positions()
            self.dict_packages[obj.get_fullname()]= obj               
        """   
        
        #jacoco_csv_filepath = self.find_jacoco_files(application, 'jacoco.csv|jacoco.xml|site\\jacoco\\index.html')[0]
        jacoco_csv_files = self.find_jacoco_files(application, 'jacoco.csv')
        
        overall_branch_to_cover = 0
        overall_branch_missed = 0
        overall_branch_covered = 0
        overall_line_to_cover = 0
        overall_line_missed = 0
        overall_line_covered = 0
        
        for jacoco_csv_filepath in jacoco_csv_files:
            jacoco_csv_filepath = jacoco_csv_filepath.replace('\\\\','\\')
            logging.info('Parsing jacoco CSV results file %s' % str(jacoco_csv_filepath))
            current_project_branch_to_cover = 0
            current_project_branch_missed = 0
            current_project_branch_covered = 0
            current_project_line_to_cover = 0
            current_project_line_missed = 0
            current_project_line_covered = 0
            
            with open(jacoco_csv_filepath, 'r') as csvfile:
                # pass the file object to reader() to get the reader object
                csv_reader = reader(csvfile, delimiter =",")
                # Iterate over each row in the csv using reader object
                nbRecord = 0
                nbRecordSkipped = 0
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    try:
                        nbRecord +=1
                        # skip the header line
                        if nbRecord > 1: 
                            classtolookfor = row[1] + '.' + row[2]
                            if self.class_coverage.get(classtolookfor) != None:
                                # we don't process 2 times the same java class
                                logging.warning('### Found several times class %s. Skipping this new result for the class' % str(classtolookfor))
                                continue
                            
                            logging.info('Processing results for class %s' % str(classtolookfor))
                            branch_missed       = int(row[5])
                            branch_covered      = int(row[6])
                            branch_to_cover     = branch_missed + branch_covered
                            
                            line_missed         = int(row[7])
                            line_covered        = int(row[8])
                            line_to_cover       = line_missed + line_covered
                                                        
                            logging.debug('    branch_to_cover = %s ' % str(branch_to_cover))
                            logging.debug('    branch_missed = %s ' % str(branch_missed))                            
                            logging.debug('    branch_covered = %s ' % str(branch_covered))
                            logging.debug('    line_to_cover = %s ' % str(line_to_cover))
                            logging.debug('    line_missed = %s ' % str(line_missed))
                            logging.debug('    line_covered = %s ' % str(line_covered))
                            overall_branch_to_cover += branch_to_cover
                            current_project_branch_to_cover += branch_to_cover
                            overall_branch_missed += branch_missed
                            current_project_branch_missed += branch_missed
                            overall_branch_covered += branch_covered
                            current_project_branch_covered += branch_covered
                            
                            overall_line_to_cover += line_to_cover
                            current_project_line_to_cover += line_to_cover                            
                            overall_line_missed += line_missed
                            current_project_line_missed += line_missed
                            overall_line_covered += line_covered
                            current_project_line_covered += line_covered                            
                            class_test_coverage = self.compute_code_coverage(branch_missed, branch_covered, line_missed, line_covered)
                            logging.info('    Class test coverage = %s%%' % str(class_test_coverage))
                            self.class_coverage[classtolookfor] =  class_test_coverage
                            #config['Class ' + classtolookfor]['test_coverage'] = str(class_test_coverage)
    
                            instruction_missed      = int(row[3])
                            instruction_covered     = int(row[4])
                            instruction_to_cover    = instruction_missed + instruction_covered
                            complexity_missed       = int(row[9])
                            complexity_covered      = int(row[10])
                            complexity_to_cover     = complexity_missed + complexity_covered
                            method_missed           = int(row[11])
                            method_covered          = int(row[12])
                            method_to_cover         = method_missed + method_covered
                            
                            logging.info('looking in Imaging results for class %s' % str(classtolookfor))
                            o_class = self.dict_classes.get(classtolookfor)
                            if o_class is not None:
                                logging.info('found class %s : updating coverage properties' % str(o_class.get_name()))
                                o_class.save_property('Coverage_Cat.coverageTool', "Jacoco")            
                                o_class.save_property('Coverage_Cat.coverageRatio', str(class_test_coverage))
                                if float(class_test_coverage) < TestCoverageApplication.threshold_coverage_class:
                                    o_class.save_violation('Coverage_Cat.isjacococovered', o_class.get_positions()[0])
                                #################################################################################
                                o_class.save_property('Coverage_Cat.branchToCover', int(branch_to_cover))
                                o_class.save_property('Coverage_Cat.branchMissed', int(branch_missed))
                                o_class.save_property('Coverage_Cat.branchCovered', int(branch_covered))
                                o_class.save_property('Coverage_Cat.lineToCover', int(branch_to_cover))
                                o_class.save_property('Coverage_Cat.lineMissed', int(branch_missed))
                                o_class.save_property('Coverage_Cat.lineCovered', int(branch_covered))                                
                                #################################################################################

                                
                            else:
                                logging.warning ("Oops!  Class %s was not found in Imaging results !" % classtolookfor)
                                
                    except UnicodeEncodeError:
                        logging.warning ("Oops!  That was an UnicodeEncodeError, due to invalid character in .csv file. Skipping "+ str(row))
                        nbRecordSkipped += 1
                        continue
                    except UnicodeDecodeError:
                        logging.warning ("Oops!  That was an UnicodeDecodeError, due to invalid encoding used for file open. Skipping "+ str(row))
                        nbRecordSkipped += 1
                    except IndexError:
                        logging.info ("Oops!  index of out of range. Skipping "+ str(row))
                        nbRecordSkipped += 1
                    # all other errors
                    except:
                        tb = traceback.format_exc()
                        logging.info ("Oops!  Error. Skipping row "+ str(row) + " :" + tb)
                        nbRecordSkipped += 1
                    continue        
                
                current_project_class_test_coverage = self.compute_code_coverage(current_project_branch_missed, current_project_branch_covered, current_project_line_missed, current_project_line_covered)
                logging.info('Current project class coverage %s%%' % str(current_project_class_test_coverage))
                config['DEFAULT']['project_class_test_coverage_for_' + jacoco_csv_filepath] = str(current_project_class_test_coverage)                
                
            self.overall_class_test_coverage = self.compute_code_coverage(overall_branch_missed, overall_branch_covered, overall_line_missed, overall_line_covered)
            logging.info('Overall class coverage %s%%' % str(self.overall_class_test_coverage))
            logging.info('Overall branch to cover %s' % str(overall_branch_to_cover))
            logging.info('Overall line to cover %s' % str(overall_line_to_cover))
            
            config['DEFAULT']['overall_class_test_coverage'] = str(self.overall_class_test_coverage)
            config['DEFAULT']['application_name'] = str(application_name)
            config['DEFAULT']['schema_central'] = str(schema_central)
            
            # write to csv file
            with open(ini_file_path, 'w') as configfile:
                config.write(configfile)    
            
    #########################################################################################################################  
        
    def end_app_log(self):
        # Final reporting
        logging.info("###################################################################################")
        
        
    #########################################################################################################################  
    '''
    def after_snapshot(self, application):
        #code_coverage_metric = 66004
        
        ApplicationLevelExtension.after_snapshot(self, application)
        central = application.get_central()
        
        logging.info("Retrieve snapshots")
        last_snapshot_id = None
        sql = "select snapshot_id, snapshot_name from dss_snapshots where snapshot_id in (select max(snapshot_id) from dss_snapshots);"
        for line in central.execute_query(sql): 
            if line[0] is not None and line[0]: 
                last_snapshot_id = line[0]        
        logging.info("Last snapshot id is %s" % str(last_snapshot_id))
        
        
        # update the code coverage metric for the last snapshot
        try:
            if last_snapshot_id != None:
                value = self.overall_class_test_coverage
                sql = """UPDATE dss_metric_results SET metric_num_value = """ + str(value)  +""" where metric_id = """ + str(code_coverage_metric) + """ and snapshot_id = """ + str(last_snapshot_id) + """;"""
                logging.info("Update metric code coverage in snapshot - UPDATE %s" % str(sql))
                ret = central.execute_query(sql)
                logging.info("UPDATE ret %s" % str(ret))

                sql = """DELETE dss_metric_results where metric_id = """ + str(code_coverage_metric) + """ and snapshot_id = """ + str(last_snapshot_id) + """;"""
                logging.info("Update metric code coverage in snapshot - DELETE : %s" % str(sql))
                ret = central.execute_query(sql)
                logging.info("DELETE ret %s" % str(ret))
                
                sql = """INSERT into dss_metric_results(metric_id,object_id,metric_value_index,metric_num_value, metric_char_value, metric_object_id, snapshot_id, position_id) """ \
                                 """ VALUES(""" + str(code_coverage_metric) + """,3,1,""" + value + """,NULL,0,"""+ str(last_snapshot_id) +""",0);"""
                logging.info("Update metric code coverage in snapshot - INSERT %s" % str(sql))
                ret = central.execute_query(sql)
                logging.info("INSERT ret %s" % str(ret))
                 
        except:
            tb = traceback.format_exc()
            logging.warning("Error Last snapshot Update metric code coverage in snapshot : %s" % tb)
        '''
        
    #########################################################################################################################
    
    