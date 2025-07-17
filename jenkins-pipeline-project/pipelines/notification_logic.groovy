def color_status(String status) {
    status = status ?: 'SUCCESS'
    switch (status) {
        case 'SUCCESS':
            return 'green'
        case 'FAILURE':
            return 'red'
        case 'UNSTABLE':
            return 'yellow'
        case 'ABORTED':
            return 'grey'
        default:
            return 'blue'
    }
}

def notify(String color, String subject, String status, Map facts) {
    echo "notification_logic.groovy notify()"
    echo "Notification: ${subject}"
    echo "Status: ${status}"    
    echo "Color: ${color}"
    echo "Facts: ${facts}"

    try {
        // Email notification
        emailext (
            subject: subject,
            body: """
                <p>Build Status: ${status}</p>
                <p>Build Details:</p>
                <ul>
                ${facts.collect { k, v -> "<li>${k}: ${v}</li>" }.join('\n')}
                </ul>
                <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>
            """,
            recipientProviders: [[$class: 'DevelopersRecipientProvider']],
            to: env.EMAIL_RECIPIENTS ?: '',
            mimeType: 'text/html'
        )
    } catch (e) {
        echo "Failed to send notification: ${e.message}"
    }
}

def build_facts() {
    def facts = [:]
    facts['build_number'] = env.BUILD_NUMBER ?: 'unknown'
    facts['build_url'] = env.BUILD_URL ?: 'unknown'
    facts['job_name'] = env.JOB_NAME ?: 'unknown'
    facts['parameters'] = get_parameter_str()
    return facts
}

def notifyBuild(String status) {
    echo "notification_logic.groovy started"
    def subject = "Build ${status}: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
    def facts = build_facts()
    def color = color_status(status)
    notify(color, subject, status, facts)
}

def get_parameter_str(){
    return """BRANCH: ${env.BRANCH},
AWS_ACCOUNT: ${env.AWS_ACCOUNT},
STACK: ${env.STACK},
ENVIRONMENT: ${env.ENVIRONMENT},
AWS_REGION: ${env.AWS_REGION},
AWS_PROFILE: ${env.AWS_PROFILE},
GIT_COMMIT: ${env.GIT_COMMIT},
GIT_BRANCH: ${env.GIT_BRANCH},
GIT_URL: ${env.GIT_URL}"""
}

return this