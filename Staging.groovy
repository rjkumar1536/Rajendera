def Staging(){
    lock('Staging-Pipeline'){
        node {
            properties([parameters([string(defaultValue: 'D:\\ci\\pipelineTestingStaging\\CarwaleStagingPipeline\\releaseTesting1\\releaseTesting1', description: '', name: 'WorkSpace'), string(defaultValue: 'D:\\JenkinsUtilities\\Staging\\', description: '', name: 'ScriptLocation')]), pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '1m']])])
            properties([parameters([string(defaultValue: '', description: '', name: 'REMOTE_SCRIPT_LOCATION')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'MON_FOLDER_LOCATION')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'WEBSITE_FOLDER_LOCATION')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'WEBSITE_FOLDER_NAME')])])      
            properties([parameters([string(defaultValue: '', description: '', name: 'MON_BACKUP_LOCATION')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'WEBSITE_BACKUP_LOCATION')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'APPLICATION_NAME')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'NODE_NAME')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'PORT')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'COMPUTER_NAME')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'SSH_SCRIPTS_LOCATION')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'AUTOMATED_CHECK_RUNNER_PATH')])])
            properties([parameters([string(defaultValue: '', description: '', name: 'ROBOT_BACKUP_PATH')])])  
            properties([parameters([string(defaultValue: '', description: '', name: 'SERVER_IP')])])                  
            properties([parameters([string(defaultValue: 'D:\\JenkinsUtilities\\Package\\', description: '', name: 'DEPLOY_FOLDER_LOCATION')])])    
            env.AUTOMATED_CHECK_RUNNER_PATH = 'D:\\JenkinsUtilities\\Staging\\automatedChecks\\'
            env.WorkSpace = 'D:\\ci\\pipelineTestingStaging\\CarwaleStagingPipeline\\carwaleTesting1'
            env.ScriptLocation = 'D:\\JenkinsUtilities\\Staging\\'
            env.REMOTE_SCRIPT_LOCATION = ''
            env.MON_FOLDER_LOCATION = ''
            env.WEBSITE_FOLDER_LOCATION = ''
            env.WEBSITE_FOLDER_NAME = ''
            env.MON_BACKUP_LOCATION = ''
            env.WEBSITE_BACKUP_LOCATION = ''
            env.APPLICATION_NAME = ''
            env.NODE_NAME = ''
            env.COMPUTER_NAME = ''
            env.ROBOT_BACKUP_PATH = ''
            env.SERVER_IP = '10.10.3.110'
            env.SSH_SCRIPTS_LOCATION = 'D:\\JenkinsUtilities\\Staging\\RemoteScripts\\' 
            env.DEPLOY_FOLDER_LOCATION = 'D:\\JenkinsUtilities\\Package\\'
            def res = ""
            dir("${env.WorkSpace}") {
                stage 'CHECKOUT'
                    try{                    
                        checkout([$class: 'GitSCM', branches: [[name: 'origin/' + "${env.BRANCH_NAME}"]], doGenerateSubmoduleConfigurations: false,  extensions: [[$class: 'PruneStaleBranch']], submoduleCfg: [], userRemoteConfigs: [[url: 'git@github.com:carwale/carwaleweb.git']]])
                        
                    }
                    catch(Exception ex){
                        throw ex
                    }     
                stage 'BUILD'
                    try{
                        res = bat returnStdout: true, script: "%ScriptLocation%Build\\TransformConfig.bat" 
                        bat "%ScriptLocation%Build\\build.bat %WorkSpace% %DEPLOY_FOLDER_LOCATION%"
                        // bat "%ScriptLocation%Build\\build.bat"
                    }
                    catch (Exception ex){
                        echo res
                        throw ex
                    }    
                stage 'GetServer' 
                    try{
                        res = bat returnStdout: true, script: "python %ScriptLocation%GetNode.py" 
                        def serverdetails = res.split("\n")[2].split(";")
                        env.NODE_NAME = serverdetails[0]
                        env.MON_FOLDER_LOCATION = serverdetails[1]
                        env.WEBSITE_FOLDER_LOCATION = serverdetails[2]
                        env.MON_BACKUP_LOCATION = serverdetails[3]
                        env.REMOTE_SCRIPT_LOCATION = serverdetails[4]
                        env.WEBSITE_BACKUP_LOCATION = serverdetails[5]    
                        env.COMPUTER_NAME =serverdetails[6]            
                        env.APPLICATION_NAME = serverdetails[7]
                        env.WEBSITE_FOLDER_NAME = serverdetails[8]
                        env.PORT = serverdetails[9]
                        env.ROBOT_BACKUP_PATH = serverdetails[10]
                        echo "https://staging.carwale.com:${PORT}"
                    }
                    catch (Exception ex){
                        echo res
                        throw ex
                    }    
                stage 'RemoveNode'
                    try{
                        res = bat returnStdout: true, script: 'python  %SSH_SCRIPTS_LOCATION%RemoteExecutionRemodeNode.py %REMOTE_SCRIPT_LOCATION% %MON_FOLDER_LOCATION% %WEBSITE_FOLDER_LOCATION% %WEBSITE_FOLDER_NAME% %MON_BACKUP_LOCATION% %WEBSITE_BACKUP_LOCATION% %SERVER_IP%'        
                    }
                    catch (Exception ex){
                        echo res
                        throw ex
                    }       

                try{            
                    stage 'DeployCode'
                        res = bat returnStdout: true, script: '%ScriptLocation%Deploy\\deploy-stg1.bat'
                        echo res
                        
                    stage 'API Testing'
                       try{
                        res = bat returnStdout: true, script: "python %AUTOMATED_CHECK_RUNNER_PATH%cwChecksRunner.py https://staging.carwale.com:%PORT% ci_staging"                     
                        echo res
                       }
                       catch(Exception ex){
                            echo "api test failed"
                            //throw ex
                       }
                

                }
                catch (Exception ex){
                    currentBuild.result = "FAILURE"         
                    try{
                        res = bat returnStdout: true, script: 'python  %SSH_SCRIPTS_LOCATION%RemoteExecutionRollOver.py %REMOTE_SCRIPT_LOCATION% %MON_FOLDER_LOCATION% %WEBSITE_FOLDER_LOCATION% %WEBSITE_FOLDER_NAME% %MON_BACKUP_LOCATION% %WEBSITE_BACKUP_LOCATION% %SERVER_IP% staging'
                        echo res
                        res = bat returnStdout: true, script: 'python  %SSH_SCRIPTS_LOCATION%RemoteExecutionAddNode.py %REMOTE_SCRIPT_LOCATION% %MON_FOLDER_LOCATION% %WEBSITE_FOLDER_LOCATION% %WEBSITE_FOLDER_NAME% %MON_BACKUP_LOCATION% %WEBSITE_BACKUP_LOCATION% %SERVER_IP% staging %ROBOT_BACKUP_PATH%'                    
                        echo res
                    }
                    catch(Exception ex2){
                        echo res
                        throw ex2
                    }

                    throw ex    
                }           
            }
        }

        stage 'Addnode'
        node {
            dir("${env.WorkSpace}"){

                def res = ""
                try{
                    res = bat returnStdout: true, script: 'python  %SSH_SCRIPTS_LOCATION%RemoteExecutionAddNode.py %REMOTE_SCRIPT_LOCATION% %MON_FOLDER_LOCATION% %WEBSITE_FOLDER_LOCATION% %WEBSITE_FOLDER_NAME% %MON_BACKUP_LOCATION% %WEBSITE_BACKUP_LOCATION% %SERVER_IP% staging %ROBOT_BACKUP_PATH%'
                    echo res
                    //step([$class: 'GitHubCommitStatusSetter', contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: 'Deployment'],reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/carwale/carwaleweb'], statusBackrefSource: [$class: 'ManuallyEnteredBackrefSource', backref: 'http://Staging.carwale.com:' + env.PORT], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'Successfully hosted', state: 'SUCCESS']]]])
                
                }
                catch (Exception ex){
                    currentBuild.result = "FAILURE"         
                    try{
                        res = bat returnStdout: true, script: 'python  %SSH_SCRIPTS_LOCATION%RemoteExecutionRollOver.py %REMOTE_SCRIPT_LOCATION% %MON_FOLDER_LOCATION% %WEBSITE_FOLDER_LOCATION% %WEBSITE_FOLDER_NAME% %MON_BACKUP_LOCATION% %WEBSITE_BACKUP_LOCATION% %SERVER_IP% staging'
                        echo res
                        res = bat returnStdout: true, script: 'python  %SSH_SCRIPTS_LOCATION%RemoteExecutionAddNode.py %REMOTE_SCRIPT_LOCATION% %MON_FOLDER_LOCATION% %WEBSITE_FOLDER_LOCATION% %WEBSITE_FOLDER_NAME% %MON_BACKUP_LOCATION% %WEBSITE_BACKUP_LOCATION% %SERVER_IP% staging %ROBOT_BACKUP_PATH%'                    
                        echo res
                    }
                    catch(Exception ex2){
                        echo res
                        throw ex2
                    }

                    throw ex    
                }
            }
        }
    }
}
return this