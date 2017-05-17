node {
    lock(resource: "res", inversePrecedence: true,quantity:1) {
            bat 'echo %time%'
            echo 'locked'
            stage 'CHECKOUT'
            echo ' started st'
            stage 'BUILD'
            echo 'Hello from build'
            echo 'st1 ended'
            bat 'echo %time%'
   }
}
