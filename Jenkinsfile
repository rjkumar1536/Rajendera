node {
   echo 'Hello World'
   stages{
       stage('BUILD'){
           setGitHubPullRequestStatus context: '', message: '"This is peding"', state: 'PENDING'
           setGitHubPullRequestStatus context: '', message: '"This is success"', state: 'SUCCESS'
       }
   }
}
