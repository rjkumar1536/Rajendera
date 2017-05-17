node {
   // properties([disableConcurrentBuilds()])
      //echo 'st1 started'
                   //echo "date:" $(date +'%Y-%m-%d_%H-%M-%S')
    properties properties: [disableConcurrentBuilds()]           // bat 'echo %time%'
   timestamps{
    lock(resource: "res", inversePrecedence: true,quantity:1) {
                                         milestone 1
                                         echo 'locked'
                                
   
   timestamps{
    stage 'CHECKOUT'
    echo 'ht started'
  checkout([$class: 'GitSCM', branches: [[name: '**']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'a2fa13d7-ddda-47a1-9828-f6abf2b80d2a', url: 'git@github.com:carwale/CIDemoRepository.git']]])
   }
   timestamps{
    stage 'BUILD'
    echo 'Hello from build'
     echo 'ht ended'
                   //echo "date:" $(date +'%Y-%m-%d_%H-%M-%S')
              bat 'echo %time%'
   }
}
   }
}
