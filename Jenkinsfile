pipeline {
    agent any
    stages {
        stage('No-op') {
            steps {
                echo "stating"
                githubNotify account: 'rjkumar1536', credentialsId: '1ca353d7-2d41-4629-9ca8-7fd9daf59b9e',description: 'This is an example', repo: 'Rajendera',  status: 'SUCCESS', targetUrl: 'https://my-jenkins-instance.com'
            }
        }
    }
    post {
        always {
            echo 'One way or another, I have finished'
            deleteDir() /* clean up our workspace */
        }
        success {
            echo 'I succeeeded!'
            /*job(String name) {
                publishers {
                    gitHubIssueNotifier {
                    }
                }
            }*/
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}
