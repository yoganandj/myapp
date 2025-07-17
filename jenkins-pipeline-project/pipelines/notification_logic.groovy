

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
def notify_build(String status, String message) {
    def subject = "Latest status of ${env.JOB_NAME} build #${env.BUILD_NUMBER}"
    def facts = build_facts()
    color = color_status(status)
    notify(color, subject, status, facts)
}

get get_parameter_str(){
    return "BRANCH:" ${BRANCH},\nAWS_ACCOUNT: ${nAWS_ACCOUNT}, \nSTACK: ${STACK}, \nENVIRONMENT: ${ENVIRONMENT}, \nAWS_REGION: ${AWS_REGION}, \nAWS_PROFILE: ${AWS_PROFILE}, \nGIT_COMMIT: ${GIT_COMMIT}, \nGIT_BRANCH: ${GIT_BRANCH}, \nGIT_URL: ${GIT_URL}"
}
