getCurrent(){
    return [
        'envName': "${AWS_ACCOUNT}",
        'envAwsCredentials': "${AWS_CREDENTIALS_IN_JENKINS}"
    ]
}

def execute_deploy(List ordered_stacks) {
    stage("Execution Action"){
        script {
            sh "echo \"STACK: ${STACK}, INCLUDE_PREVIOUS_STACK: ${INCLUDE_PREVIOUS_STACK}, ENVIRONMENT: ${ENVIRONMENT}, AWS_REGION: ${AWS_REGION}, AWS_PROFILE: ${AWS_PROFILE}, AWS_ACCOUNT: ${AWS_ACCOUNT}, GIT_COMMIT: ${GIT_COMMIT}, GIT_BRANCH: ${GIT_BRANCH}, GIT_URL: ${GIT_URL}\""
            sh "echo \"Ordered Status: ${ordered_stacks}\""
            stack = ordered_stacks
        }

        if(ACTION == "DEPLOY") {
            stacks.each { stack -> 
                if(fileExists("src/{stack}/jenkins.groovy")) {
                    def jenkinsScript = load "src/${stack}/jenkins.groovy"
                    jenkinsScript.checkUnitTests(getCurrent())
                }

                // terraform
                if(fileExists("src/${stack}/terraform/jenkins.groovy")) {
                    def jenkinsScript = load "src/${stack}/terraform/jenkins.groovy"
                    jenkinsScript.checkAndDeploy(getCurrent())
                } else {
                    echo "No terraform script found for stack: ${stack}"
                }

                // resources initialization
                if(fileExists("src/{stack}/jenkins.groovy")) {
                    def jenkinsScript = load "src/${stack}/jenkins.groovy"
                    jenkinsScript.initResources(getCurrent())
                } else {
                    echo "No resources initialization script found for stack: ${stack}"
                }
            }
        } else {
            stage("Execution Action - No Deploy") {
                script {
                    sh "echo \"No deploy action taken for stack: ${stack}\""
                }
            }
        }
    }
}

