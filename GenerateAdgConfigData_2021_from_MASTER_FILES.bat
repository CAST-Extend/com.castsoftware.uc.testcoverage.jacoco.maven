@echo off
MODE CON: COLS=132 LINES=40

::Parameters to adapt to each analysis env :
Set OutputFolder=.\					 -- not used with -plugin parameter. generated in subfolder
Set MasterFileFolder=.\MasterFiles   -- not used with -plugin parameter. looked in subfolder
Set adgMetrics=AdgConfigData.xml     -- not used with -plugin parameter. Fixed name.

::Parameters to adapt in some cases :
::Set MetricsCompiler_BAT_path=.\MasterFiles\MetricsCompilerFromFlat.bat
::Set MetricsCompiler_BAT_path=.\MAsterFiles\MetricsCompilerWithJARCLI.bat
REM Be careful this command must use Java 8, in the below case it's using java 8 from flat folder but you need to add double quotes in "%JAVA_HOME%\bin\java" 
REM in below MetricsCompiler.bat file
Set MetricsCompiler_BAT_path=C:\Program Files\CAST\8.3\tools\MetricsCompiler\MetricsCompiler.bat

Title Generating %adgMetrics% from MASTER FILES at %TargetFolder%

:: call Compiler - full syntax (with specific AdgConfigData file name)
call "%MetricsCompiler_BAT_path%" -plugin 

::TOBE : Manage ERRORLEVEL ?
pause