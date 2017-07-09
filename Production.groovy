import org.jenkinsci.plugins.workflow.steps.FlowInterruptedException              
def notifySlack(String Status = 'STARTED',String customMessage=" ")
{
    // build status of null means successful
    Status =  Status ?: 'SUCCESSFUL'

    // Default values
    def colorName = 'RED'
    def colorCode = '#FF0000'
    def subject = "${Status}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    def summary = "${subject} (${env.BUILD_URL})"
    def details = """<p>STARTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
    <p>Check console output at <a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>"""
     
    // Override default values based on build status
    if (Status == 'STARTED') {
        color = 'YELLOW'
        colorCode = '#FFFF00'
    }
    else if (Status == 'SUCCESSFUL'){
        color = 'GREEN'
        colorCode = '#00FF00'
    }
    else {
        color = 'RED'
        colorCode = '#FF0000'
    }
    slackSend (color: colorCode, message: summary)
    slackSend (color: colorCode, message: customMessage)
    
}
def rollback(serverDetails,int server){
    def res = ""
    try{
        timeout(time: 12000, unit: 'SECONDS') {
            input message: 'Click Proceed to Rollback Automatically', submitter: ''
        }       
        for(int RollBackFromServer=server;RollBackFromServer>=0;RollBackFromServer--){
            stage("REVERT " + "${serverDetails[RollBackFromServer]['node_name']}")
            timeout(time: 12000, unit: 'SECONDS') {
                input message: 'Click Proceed to RollOver', submitter: ''
            }
            node {

                res = bat returnStdout: true, script: "python  %SSH_SCRIPTS_LOCATION%RemoteExecutionRollOver.py ${serverDetails[RollBackFromServer]['remote_script_location']} ${serverDetails[RollBackFromServer]['mon_folder_location']} ${serverDetails[RollBackFromServer]['website_folder_location']} ${serverDetails[RollBackFromServer]['website_folder_name']} ${serverDetails[RollBackFromServer]['mon_backup_location']} ${serverDetails[RollBackFromServer]['website_backup_location']} ${serverDetails[RollBackFromServer]['server_ip']} production ${serverDetails[RollBackFromServer]['backup_lock_file']}" 
            }
            timeout(time: 12000, unit: 'SECONDS') {
                input message: 'Click Proceed to AddNode', submitter: ''
            }
            node{
                res = bat returnStdout: true, script: "python  %SSH_SCRIPTS_LOCATION%RemoteExecutionAddNode.py ${serverDetails[RollBackFromServer]['remote_script_location']} ${serverDetails[RollBackFromServer]['mon_folder_location']} ${serverDetails[RollBackFromServer]['website_folder_location']} ${serverDetails[RollBackFromServer]['website_folder_name']} ${serverDetails[RollBackFromServer]['mon_backup_location']} ${serverDetails[RollBackFromServer]['website_backup_location']} ${serverDetails[RollBackFromServer]['server_ip']} production ${serverDetails[RollBackFromServer]['robot_backup_location']}"
                res = bat returnStdout: true, script: "python  %ScriptLocation%RemoveLock.py ${serverDetails[RollBackFromServer]['server_ip']} ${serverDetails[RollBackFromServer]['backup_lock_file']}"                    
                
            }
        }
    }
    catch(Exception ex) {
        echo res
        echo 'RollBack Unsuccessful'
        throw ex
    }               

}
def Production(){
    lock('Production-pipeline'){
        properties([pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '1m']])])
        properties([parameters([string(defaultValue: 'D:\\ci\\CarwaleProductionPipeline\\CIDemoRepository_DB', description: '', name: 'WorkSpace')])])
        properties([parameters([string(defaultValue: 'D:\\JenkinsUtilities\\Production-DB\\', description: '', name: 'ScriptLocation')])])
        properties([parameters([string(defaultValue: 'C:\\JenkinsUtilities\\Production-DB\\Package\\', description: '', name: 'DEPLOY_FOLDER_LOCATION')])])    
        properties([parameters([string(defaultValue: 'D:\\ci\\CarwaleProductionPipeline\\CIDemoRepository_DB', description: '', name: 'WorkSpaceLinuxStyle')])])
        
        env.WorkSpaceLinuxStyle = 'D:/ci/CarwaleProductionPipeline/carwaleweb'
        env.WorkSpace = 'D:\\ci\\CarwaleProductionPipeline\\carwaleweb'
        env.ScriptLocation = 'D:\\JenkinsUtilities\\Production-DB\\'
        env.SSH_SCRIPTS_LOCATION = 'D:\\JenkinsUtilities\\Production-DB\\RemoteScripts\\' 
        env.DEPLOY_FOLDER_LOCATION = 'D:\\JenkinsUtilities\\Production-DB\\Package\\'

        def staticServers = [
            [   "server_IP" : "10.10.3.10",
                "Remote_Path" : "E:/sites/stc.carwale.com"
            ],
            [   "server_IP" : "10.10.4.10",
                "Remote_Path" : "E:/sites/stc.carwale.com"
            ]        
        ]
        def serverDetails = [
            [
                "remote_script_location": "E:/CDScripts/",
                "mon_folder_location": "E:/sites/carwale/mon",
                "website_folder_location": "E:/sites/",
                "mon_backup_location": "E:/CDScripts/mon",
                "website_backup_location": "E:/backup",
                "website_folder_name":"carwale",
                "application_name": "carwale",
                "node_name":"CWWEB1",
                "computer_name":"\"https://10.10.3.10:8172/msdeploy.axd?site=carwale\"",
                "server_ip": "10.10.3.10",
                "robot_backup_location" : "E:/CDScripts/robot/",
                "backup_lock_file": "E:/CDScripts/backuplock.txt"
            ],
            [
                "remote_script_location": "E:/CDScripts/",
                "mon_folder_location": "E:/sites/carwale/mon",
                "website_folder_location": "E:/sites/",
                "mon_backup_location": "E:/CDScripts/mon",
                "website_backup_location": "E:/backup",
                "website_folder_name":"carwale",
                "application_name": "carwale",
                "node_name":"CWWEB2",
                "computer_name":"\"https://10.10.4.10:8172/msdeploy.axd?site=carwale\"",
                "server_ip": "10.10.4.10",
                "robot_backup_location" : "E:/CDScripts/robot/",
                "backup_lock_file": "E:/CDScripts/backuplock.txt"
            ],
            [
                "remote_script_location": "E:/CDScripts/",
                "mon_folder_location": "E:/sites/carwale/mon",
                "website_folder_location": "E:/sites/",
                "mon_backup_location": "E:/CDScripts/mon",
                "website_backup_location": "E:/backup",
                "website_folder_name":"carwale",
                "application_name": "carwale",
                "node_name":"CWWEB3",
                "computer_name":"\"https://10.10.3.11:8172/msdeploy.axd?site=carwale\"",
                "server_ip": "10.10.3.11",
                "robot_backup_location" : "E:/CDScripts/robot/",
                "backup_lock_file": "E:/CDScripts/backuplock.txt"

            ],
            [
                "remote_script_location": "E:/CDScripts/",
                "mon_folder_location": "E:/sites/carwale/mon",
                "website_folder_location": "E:/sites/",
                "mon_backup_location": "E:/CDScripts/mon",
                "website_backup_location": "E:/backup",
                "website_folder_name":"carwale",
                "application_name": "carwale",
                "node_name":"CWWEB4",
                "computer_name":"\"https://10.10.4.11:8172/msdeploy.axd?site=carwale\"",
                "server_ip": "10.10.4.11",
                "robot_backup_location" : "E:/CDScripts/robot/",
                "backup_lock_file": "E:/CDScripts/backuplock.txt"
            ],
            [
                "remote_script_location": "E:/CDScripts/",
                "mon_folder_location": "E:/sites/carwale/mon",
                "website_folder_location": "E:/sites/",
                "mon_backup_location": "E:/CDScripts/mon",
                "website_backup_location": "E:/backup",
                "website_folder_name":"carwale",
                "application_name": "carwale",
                "node_name":"CWWEB5",
                "computer_name":"\"https://10.10.3.12:8172/msdeploy.axd?site=carwale\"",
                "server_ip": "10.10.3.12",
                "robot_backup_location" : "E:/CDScripts/robot/",
                "backup_lock_file": "E:/CDScripts/backuplock.txt"
            ],
            [
                "remote_script_location": "E:/CDScripts/",
                "mon_folder_location": "E:/sites/carwale/mon",
                "website_folder_location": "E:/sites/",
                "mon_backup_location": "E:/CDScripts/mon",
                "website_backup_location": "E:/backup",
                "website_folder_name":"carwale",
                "application_name": "carwale",
                "node_name":"CWWEB6",
                "computer_name":"\"https://10.10.4.12:8172/msdeploy.axd?site=carwale\"",
                "server_ip": "10.10.4.12",
                "robot_backup_location" : "E:/CDScripts/robot/",
                "backup_lock_file": "E:/CDScripts/backuplock.txt"
            ]
       
        ]
        int deployonserver
        node {
            dir("${env.WorkSpace}") {
                stage 'CHECKOUT'
                try{           
                    def prdetails = "${env.BRANCH_NAME}".split("-")
                    checkout([$class: 'GitSCM', branches: [[name: 'origin/' + "${env.BRANCH_NAME}"]], doGenerateSubmoduleConfigurations: false,  extensions: [[$class: 'PruneStaleBranch']], submoduleCfg: [], userRemoteConfigs: [[url: 'git@github.com:carwale/carwaleweb.git']]])
                    // checkout([$class: 'GitSCM', branches: [[name: 'origin/pull/'+prdetails[1]+'/head']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[name: 'origin', refspec: '+refs/pull/'+prdetails[1]+'/head:refs/remotes/origin/pull/'+prdetails[1]+'/head', url: 'git@github.com:carwale/CIDemoRepository.git']]])
                }
                catch(Exception ex){
                    throw ex
                }     

                stage 'BUILD'
                try {
                    //notifySlack('STARTED')
                    res = bat returnStdout: true, script: "%ScriptLocation%Build\\TransformConfig.bat" 
                    bat "%ScriptLocation%Build\\build.bat %WorkSpace% %DEPLOY_FOLDER_LOCATION%"
                    // echo "hello"
                } 
                catch (Exception ex){
                    // If there was an exception thrown, the build failed
                    // echo "There is some error in build"
                    currentBuild.result = "FAILED"
                    throw ex
                }
                for(currentStaticServer=0;currentStaticServer < staticServers.size();currentStaticServer++){
                    stage 'DeployStatic'
                    try {
                        timeout(time: 12000, unit: 'SECONDS') {
                            input message: 'Click Proceed to Deploy static content', submitter: ''                                        
                        }
                        res = bat returnStdout: true, script: "python  %ScriptLocation%DeployStatic.py ${staticServers[currentStaticServer]['server_IP']} ${staticServers[currentStaticServer]['Remote_Path']} %WorkSpace%/Carwale/Static"                    
                        echo res
                    }
                    catch(Exception ex) {
                        echo res
                        throw ex
                    }
                }
                // finally{
                //    echo "finally"
                //     Success or failure, always send notifications
                //     notifySlack(currentBuild.result)
                // }
            }
        }     
        for(currentServer=0;currentServer<serverDetails.size();currentServer++){
            try{
                stage("RemoveNode " + "${serverDetails[currentServer]['node_name']}")
                timeout(time: 12000, unit: 'SECONDS') {
                    input message: 'Click Proceed to RemoveNode', submitter: ''
                }
                node{
                    res = bat returnStdout: true, script: "python  %SSH_SCRIPTS_LOCATION%RemoteExecutionRemodeNode.py ${serverDetails[currentServer]['remote_script_location']} ${serverDetails[currentServer]['mon_folder_location']} ${serverDetails[currentServer]['website_folder_location']} ${serverDetails[currentServer]['website_folder_name']} ${serverDetails[currentServer]['mon_backup_location']} ${serverDetails[currentServer]['website_backup_location']} ${serverDetails[currentServer]['server_ip']} ${serverDetails[currentServer]['backup_lock_file']}"        
                    echo "node removed"                                    
                }
            }   
            catch(FlowInterruptedException ex){
                echo 'Its aborted..now I cant do anything.....Removing node cant be done'
                rollback(serverDetails,currentServer)
            }
            catch (Exception ex){
                echo "Some error in remove node" //need to check whether to rollback or not 
                rollback(serverDetails,currentServer)
                throw ex                    
            }        
            try{
                stage("DeployCode " + "${serverDetails[currentServer]['node_name']}")
                timeout(time: 12000, unit: 'SECONDS'){
                    input message: 'Click Proceed to DeployCode', submitter: ''
                }
                node{
                        bat "%ScriptLocation%Deploy\\deploy.bat %DEPLOY_FOLDER_LOCATION% ${serverDetails[currentServer]['computer_name']} ${serverDetails[currentServer]['application_name']}" 
                }
            }
            catch(FlowInterruptedException ex){
                echo "Aborted by user or time out"
                rollback(serverDetails,currentServer)
                throw ex
            }
            catch (Exception ex){
                echo "exception occured"
                rollback(serverDetails,currentServer)
                throw ex
            }
            // stage("API Testing " + "${serverDetails[currentServer]['node_name']}")
            // try{
            //     node{
            //         echo "Api Testing"
            //     }
            // }
            // catch (Exception ex){
            //     echo "exception occured"
            //     rollback(serverDetails,currentServer)
            //     throw ex
            // }
            try{
                stage("Warmup " + "${serverDetails[currentServer]['node_name']}")
                node{
                    res = bat returnStdout : true, script: "%ScriptLocation%warmup\\ConsoleApplication1.exe http://${serverDetails[currentServer]['server_ip']}"
                }
            }
            catch (Exception ex){
                echo "exception occured"
                rollback(serverDetails,currentServer)
                throw ex
            }    
            try{
                stage("AddNode " + "${serverDetails[currentServer]['node_name']}")
                timeout(time: 12000, unit: 'SECONDS'){
                    input message: 'Click Proceed to AddNode', submitter: ''
                }
                node{
                    res = bat returnStdout: true, script: "python  %SSH_SCRIPTS_LOCATION%RemoteExecutionAddNode.py ${serverDetails[currentServer]['remote_script_location']} ${serverDetails[currentServer]['mon_folder_location']} ${serverDetails[currentServer]['website_folder_location']} ${serverDetails[currentServer]['website_folder_name']} ${serverDetails[currentServer]['mon_backup_location']} ${serverDetails[currentServer]['website_backup_location']} ${serverDetails[currentServer]['server_ip']} production ${serverDetails[currentServer]['robot_backup_location']}"                    
                    echo "Node Added To LB"
                }
            }
            catch(FlowInterruptedException ex){
                echo "Aborted by user or time out"
                rollback(serverDetails,currentServer)
                throw ex
            }
            catch (Exception ex){
                echo "exception occured"
                rollback(serverDetails,currentServer)
                throw ex
            }                        
        }
        for(currentServer=0;currentServer<serverDetails.size();currentServer++){
            node{
                try{
                    res = bat returnStdout: true, script: "python  %ScriptLocation%RemoveLock.py ${serverDetails[currentServer]['server_ip']} ${serverDetails[currentServer]['backup_lock_file']}"                    
                }
                catch (Exception ex){
                    echo res
                }
            }
        }
    }
}
return this
