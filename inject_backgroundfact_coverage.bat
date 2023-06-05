@echo off

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
REM configure python path, not required if python is on the path
SET PYTHONPATH=
REM SET PYTHONPATH=C:\Python\Python310\
SET PYTHONCMD=python
IF NOT "%PYTHONPATH%" == "" SET PYTHONCMD=%PYTHONPATH%\python

ECHO =================================
"%PYTHONCMD%" -V
ECHO =================================

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
REM install the additional python lib required
REM IF NOT "%PYTHONPATH%" == "" "%PYTHONPATH%\Scripts\pip" install requests 

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: REST API URL : http|https://host(:port)(/WarName)/rest
SET RESTAPIURL=http://localhost:8080/rest

REM SET APIKEY=N/A
SET USER=admin
SET PASSWORD=admin

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
SET APPNAME=MyApp

:: Application name regexp filter, if not defined all application will be exported
::SET APPFILTER=Webgoat^|eComm.*
SET APPFILTER=%APPNAME%

:: Deploy folder
SET DEPLOYFOLDER=C:/ProgramData/CAST/AIP-Console-Standalone/deploy/%APPNAME%

:: Background fact metric id for Coverage  
SET METRICID=66004

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
REM Build the command line
SET CMD="%PYTHONCMD%" "%~dp0inject_backgroundfact_coverage.py" 

IF DEFINED RESTAPIURL 				SET CMD=%CMD% -restapiurl "%RESTAPIURL%"

IF NOT DEFINED USER 				SET USER=N/A
IF NOT DEFINED PASSWORD 			SET PASSWORD=N/A
IF NOT DEFINED APIKEY 				SET APIKEY=N/A
SET CMD=%CMD% -user "%USER%" -password "%PASSWORD%" -apikey "%APIKEY%"

SET CURRENTFOLDER=%~dp0
:: remove trailing \
SET CURRENTFOLDER=%CURRENTFOLDER:~0,-1%

SET OUTPUTFOLDER=%CURRENTFOLDER%

SET LOGFILE=%CURRENTFOLDER%\inject_backgroundfact_coverage_bat.log
IF DEFINED LOGFILE					SET CMD=%CMD% -log "%LOGFILE%"
IF DEFINED OUTPUTFOLDER 			SET CMD=%CMD% -of "%OUTPUTFOLDER%"

SET EXTENSIONINSTALLATIONFOLDER=%CURRENTFOLDER%
SET CMD=%CMD% -extensioninstallationfolder "%EXTENSIONINSTALLATIONFOLDER%"

IF DEFINED APPFILTER 				SET CMD=%CMD% -applicationfilter "%APPFILTER%"
IF DEFINED DEPLOYFOLDER				SET CMD=%CMD% -deployfolder "%DEPLOYFOLDER%"
IF DEFINED METRICID					SET CMD=%CMD% -metricid "%METRICID%"

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

ECHO Running the command line 
ECHO %CMD%
%CMD%
SET RETURNCODE=%ERRORLEVEL%
ECHO RETURNCODE %RETURNCODE% 

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


PAUSE