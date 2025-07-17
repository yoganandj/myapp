def ordered_stacks = [
    'data_libraries',
    'data_delivery'
]

pipeline {
    agent any

    parameters {
        choice(
            name: 'ACTION',
            choices: ['DEPLOY', 'NO_DEPLOY'],
            description: 'Select the action to perform'
        )
        string(
            name: 'BRANCH', 
            defaultValue: 'main', 
            description: 'Branch to deploy from'
        )
        choice(
            name: 'STACK',
            choices: ['ALL', 'data_libraries', 'data_delivery'],
            description: 'myapp stack to deploy'
        )
        booleanParam(
            name: 'INCLUDE_PREVIOUS_STACK',
            defaultValue: false,
            description: 'Include previous stack in deployment'
        )
        string(
            name: 'GIT_COMMIT_HASH',
            defaultValue: 'DO NOT SET',
            description: 'Git commit hash to deploy'
        )
    }

    environment {
        AWS_ACCOUNT = 'dev01'
        AWS_CREDENTIALS_IN_JENKINS = "${AWS_ACCOUNT}-myapp-aws"
        GITHUB_URL = "https://github.com/yoganandj/myapp.git"
        GIT_CREDENTIALS_IN_JENKINS = 'gith-jenkins-credentials'
    }

    stages {
        stage('Setup GitHub Credentials') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: "${GIT_CREDENTIALS_IN_JENKINS}",
                        usernameVariable: 'USERNAME',
                        passwordVariable: 'TOKEN'
                    )]) {
                        bat """
                            echo https://%USERNAME%:%TOKEN%@github.com > %USERPROFILE%\\.git-credentials
                            git config --global credential.helper store
                        """
                    }
                }
            }
        }

        stage('Git Checkout') {
            steps {
                script {
                    def scmVars = checkout([
                        $class: 'GitSCM',
                        branches: [[name: "*/${params.BRANCH}"]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        submoduleCfg: [],
                        userRemoteConfigs: [[
                            url: "${GITHUB_URL}",
                            credentialsId: "${GIT_CREDENTIALS_IN_JENKINS}"
                        ]]
                    ])

                    env.GIT_COMMIT = scmVars.GIT_COMMIT
                    env.GIT_BRANCH = scmVars.GIT_BRANCH
                    env.GIT_AUTHOR_NAME = bat(
                        script: 'git log -1 --pretty=format:"%an"',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage("Process Stacks") {
            steps {
                script {
                    def jenkinsNotify = load 'pipelines/notification_logic.groovy'
                    jenkinsNotify.notifyBuild('STARTED')

                    def jenkinsDeploy = load 'pipelines/deployment_logic.groovy'
                    jenkinsDeploy.execute_deploy(ordered_stacks)
                }
            }
        }
    }

    post {
        always {
            script {
                def jenkinsNotify = load 'pipelines/notification_logic.groovy'
                jenkinsNotify.notifyBuild(currentBuild.result)
                cleanWs()
            }
        }
    }
}