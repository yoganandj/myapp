
def ordered_stacks = [
    'data_libraries',
    'data_delivery'
]


pipeline {
    agent any

    parameters {
        choice(name: 'ACTION', choices: ['DEPLOY', 'NO_DEPLOY'], description: 'Select the action to perform')

        get_parameter_str(
            name: 'BRANCH', 
            defaultValue: 'main', 
            description: 'Branch to deploy from'
        )
        choice(
            name: 'STACK',
            choices: ordered_stacks.join('ALL'),
            description: 'myapp stack to deploy'
        )
        booleanParam(
            name: 'INCLUDE_PREVIOUS_STACK',
            defaultValue: false,
            description: 'Include previous stack in deployment'
        )
        string(
            name: 'GIT_COMMIT_HASH',
            defaultValue: 'DO NOT SET'
        )
    }

    environment {
        AWS_ACCOUNT = 'dev01'
        AWS_CREDENTIALS_IN_JENKINS = "${AWS_ACCOUNT}-myapp-aws"
        GITHUB_URL = "https://github.com/yoganandj/myapp.git"
        GIT_CREDENTIALS_IN_JENKINS = 'GithubTokenForJenkinsMyApp'
    }

    stages {
        stage('github Credentials') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_IN_JENKINS}", usernameVariable: 'USERNAME', passwordVariable: 'TOKEN')]) {
                    sh "echo \"https://${USERNAME}:${TOKEN}@github.com\" > ~/.git-credentials"
                    sh "git config --global credential.helper store --file ~/.git-credentials" 
                }
                // Add your build steps for data libraries here
            }
        }
        stage('Git Checkout') {
            steps {
                script {
                    def scmVars = checkout([$class: 'GitSCM', 
                        branches: [[name: "${params.BRANCH}"]],
                        doGenerateSubmoduleConfigurations: false,
                        extension: [],
                        submoduleCfg: [],
                        url: "${GITHUB_URL}",
                        userRemoteConfigs: [[url: "${GITHUB_URL}", credentialsId: "${GIT_CREDENTIALS_IN_JENKINS}"]]
                    ]
                    )
                }

                env.GIT_COMMIT = scmVars.GIT_COMMIT
                env.GIT_BRANCH = scmVars.GIT_BRANCH
                env.GIT_AUTHOR_NAME = sh(returnStdout: true, script: "git log -1 --pretty=format:'%an").trim()
                echo 'Delivering Data...'
                // Add your build steps for data delivery here
            }
        }
        // Add additional stages as necessary
    }
    stage("Load Logic Files") {
        steps {
            script {
                def jenkinsNotify = load 'pipelines/notification_logic.groovy'
                jenkinsNotify.notifyBuild("Starting")

                def jenkinsDeploy = load 'pipelines/deployment_logic.groovy'
                jenkinsDeploy.execute_deploy(ordered_stacks)
            }
        }
    }

    post {
        always {
            script {
                def jenkinsNotify = load 'pipelines/notification_logic.groovy'
                jenkinsNotify.notifyBuild(currentBuild.results)
            }
        }
    }
}