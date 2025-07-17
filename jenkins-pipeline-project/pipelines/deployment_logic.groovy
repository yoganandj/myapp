def getCurrent() {
    return [
        'envName': "${env.AWS_ACCOUNT}",
        'envAwsCredentials': "${env.AWS_CREDENTIALS_IN_JENKINS}"
    ]
}

def execute_deploy(List ordered_stacks) {
    stage("Execution Action") {
        script {
            echo """Stack Details:
                STACK: ${env.STACK}
                INCLUDE_PREVIOUS_STACK: ${env.INCLUDE_PREVIOUS_STACK}
                ENVIRONMENT: ${env.ENVIRONMENT}
                AWS_REGION: ${env.AWS_REGION}
                AWS_PROFILE: ${env.AWS_PROFILE}
                AWS_ACCOUNT: ${env.AWS_ACCOUNT}
                GIT_COMMIT: ${env.GIT_COMMIT}
                GIT_BRANCH: ${env.GIT_BRANCH}
                GIT_URL: ${env.GIT_URL}
            """
            echo "Ordered Stacks: ${ordered_stacks}"
        }

        if (params.ACTION == "DEPLOY") {
            ordered_stacks.each { stack -> 
                if (fileExists("src/${stack}/jenkins.groovy")) {
                    echo "deployment logic checking file exist -- jenkins.groovy"
                    def jenkinsScript = load "src/${stack}/jenkins.groovy"
                    jenkinsScript.checkUnitTests(getCurrent())
                }

                // terraform
                if (fileExists("src/${stack}/terraform/jenkins.groovy")) {
                    def jenkinsScript = load "src/${stack}/terraform/jenkins.groovy"
                    jenkinsScript.checkAndDeploy(getCurrent())
                } else {
                    echo "No terraform script found for stack: ${stack}"
                }

                // resources initialization
                if (fileExists("src/${stack}/jenkins.groovy")) {
                    def jenkinsScript = load "src/${stack}/jenkins.groovy"
                    jenkinsScript.initResources(getCurrent())
                } else {
                    echo "No resources initialization script found for stack: ${stack}"
                }
            }
        } else {
            stage("Execution Action - No Deploy") {
                echo "No deploy action taken for stack: ${ordered_stacks}"
            }
        }
    }
}

return this