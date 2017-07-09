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
    // slackSend (color: colorCode, message: summary)
    slackSend (color: colorCode, message: customMessage)
    
}

def update_database(String status)
{
     env.Database_Query="update"
     env.Database_status=status
     bat returnStdout: true,script: 'python %ScriptLocation%Entry_into_database.py  %CommitHash% %AuthorName% %Commit_Message% %Deploy_History_Table% %Database_Query% %Database_status%'

}



def Testing(){
    lock('Testing-pipeline'){
        properties([pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '1m']])])
        properties([parameters([string(defaultValue: 'D:\\ci\\CarwaleFeatureTestingPipeline\\CIDemoRepository', description: '', name: 'WorkSpace')])])
        properties([parameters([string(defaultValue: 'D:\\JenkinsUtilities\\Feature_Testing\\', description: '', name: 'ScriptLocation')])])
        properties([parameters([string(defaultValue: 'D:\\JenkinsUtilities\\Feature_Testing\\Package\\', description: '', name: 'DEPLOY_FOLDER_LOCATION')])])    
        properties([parameters([string(defaultValue: 'D\\ci\\CarwaleFeatureTestingPipeline\\CIDemoRepository', description: '', name: 'WorkSpaceLinuxStyle')])])
        
        env.WorkSpaceLinuxStyle = 'D:/ci/CarwaleFeatureTestingPipeline/carwaleweb'
        env.WorkSpace = 'D:\\ci\\CarwaleFeatureTestingPipeline\\carwaleweb'
        env.ScriptLocation = 'D:\\JenkinsUtilities\\Feature_Testing\\'
        env.DEPLOY_FOLDER_LOCATION = 'D:\\JenkinsUtilities\\Feature_Testing\\Package\\'
        env.Current_Environment="FeatureTesting"
        env.Configuration="Debug"
        env.CommitHash="CommitHash"
        env.AuthorName="AuthorName"
        env.Commit_Message="Commit_Message"
        env.Deploy_History_Table="Feature_Testing_Deploy_History"
        env.Site_Pool_Table="FeatureTestingWebsitePool"
        env.Database_Query="insert"
        env.Database_status="STARTED"
        node {
            dir("${env.WorkSpace}") {
                stage 'CHECKOUT'
                try{           
                    def prdetails = "${env.BRANCH_NAME}".split("-")
                    echo "In stage checkout"
                  checkout([$class: 'GitSCM', branches: [[name: 'origin/' + "${env.BRANCH_NAME}"]], doGenerateSubmoduleConfigurations: false,  extensions: [[$class: 'PruneStaleBranch']], submoduleCfg: [], userRemoteConfigs: [[url: 'git@github.com:carwale/carwaleweb.git']]])
                }
                catch(Exception ex){
                    throw ex
                } 
                try{
                        res=bat returnStdout: true, script: "python %ScriptLocation%git_authors.py %WorkSpace%"
                        echo res
                        def commit_details = res.split("Commit_Details:")[1].split(",")
                        env.CommitHash=commit_details[0].replaceAll("\\s","")
                        env.AuthorName=commit_details[1].replaceAll("\\s","")
                        env.Commit_Message=commit_details[2].replaceAll("\\s","")
                        // echo "${env.CommitHash}"
                            
                }
                catch(Exception ex){
                        echo ex
                }    
                res=bat returnStdout: true,script: 'python %ScriptLocation%Entry_into_database.py  %CommitHash% %AuthorName% %Commit_Message% %Deploy_History_Table% %Database_Query% %Database_status%'
                echo res

                stage 'BUILD'
                try {
                    bat "%ScriptLocation%Build\\build.bat %WorkSpace% %Configuration% %DEPLOY_FOLDER_LOCATION%"
                    echo "done wd build"
                } 
                catch (Exception ex){
                    currentBuild.result = "FAILED"
                    update_database("ABORTED")
                    throw ex
                }

                stage 'Check Database Changes'
                try{
                    res=""
                    res = bat returnStdout: true, script: "python %ScriptLocation%Database_differences.py %WorkSpace%" 
                    echo res
                    
                    
                    if(res.contains("Database_Scripts_changed"))
                        bat returnStdout: true, script: "python %ScriptLocation%send_mail.py %ScriptLocation% " 
                    

                }
                catch(Exception ex){
                    update_database("ABORTED")
                    throw ex
                } 



                stage 'GetServer' 
                try{
                    res = bat returnStdout: true, script: "python %ScriptLocation%GetNode.py %Current_Environment% %Site_Pool_Table%" 
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
                  
                }
                catch (Exception ex){
                    echo res
                    update_database("ABORTED")
                    throw ex
                }   
                
            }
        }     
       






            try{
                stage("DeployCode " )
                timeout(time: 12000, unit: 'SECONDS'){
                    input message: 'Click Proceed to DeployCode', submitter: ''
                }
                node{
                        bat "%ScriptLocation%Deploy\\deploy_Feature_Testing.bat %DEPLOY_FOLDER_LOCATION%  %APPLICATION_NAME%" 
                        echo "deployed"
                }
            }
            catch(FlowInterruptedException ex){
                echo "Aborted by user or time out"
                node{
                    update_database("ABORTED")
                }
                throw ex
            }
            catch (Exception ex){
                echo "exception occured"
                node{
                    update_database("ABORTED")
                }
                throw ex
            }
            
    
            node{        
                    update_database("COMPLETED")
            }
            echo "Site Deployed at ${PORT}"  
            notifySlack("Completed","Site Deployed at ${PORT}")
            
                
                                  
        
      
    }
}
return this
