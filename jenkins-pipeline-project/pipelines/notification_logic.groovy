

def color_status(String status) {
    status = status ?: 'SUCCESS' // Default to SUCCESS if status is null or empty
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

def notify(String color, String subject, String status, List facts) {
    echo "notification_logic.groovy notify()"
    echo "Notification: ${subject}"
    echo "Status: ${status}"    
    echo "Color: ${color}"
    echo "Facts: ${facts}"

    // Here you can integrate with a notification service or system
}

def build_facts() {
    def facts = [:]
    facts['build_number'] = env.BUILD_NUMBER ?: 'unknown'
    facts['build_url'] = env.BUILD_URL ?: 'unknown'
    facts['job_name'] = env.JOB_NAME ?: 'unknown'
    return facts
}
def notifyBuild(String status) {
    echo "notification_logic.groovy started"
    def subject = "Latest status of ${env.JOB_NAME} build #${env.BUILD_NUMBER}"
    def facts = build_facts()
    def color = color_status(status)
    this.notify(color, subject, status, facts)
}

def get_parameter_str(){
    return "BRANCH: ${env.BRANCH},\nAWS_ACCOUNT: ${env.AWS_ACCOUNT}, \nSTACK: ${env.STACK}, \nENVIRONMENT: ${env.ENVIRONMENT}, \nAWS_REGION: ${env.AWS_REGION}, \nAWS_PROFILE: ${env.AWS_PROFILE}, \nGIT_COMMIT: ${env.GIT_COMMIT}, \nGIT_BRANCH: ${env.GIT_BRANCH}, \nGIT_URL: ${env.GIT_URL}"
}
return this;
