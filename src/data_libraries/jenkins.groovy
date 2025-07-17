current_stack ="data_libraries"

sonarProjectName = "myapp_${current_stack}"
sonarProjectKey = "myapp_${current_stack}"
sonarProjectBaseDir = "src/${current_stack}"
sonarSource = "data_logging/data_logging"
sonarTestSource = "data_logging/test"
sonarTestCoverage = "data_logging/reports/coverage.xml"
sonarTestReport = "data_logging/reports/test.xml"

def checkUnitTests(Map stack) {
    echo "stack name : ${stack.envName}"
    stage("Check UnitTests-Linter ${current_stack}") {
        dir("src/${current_stack}") {
            sh """
                python3 -m venv venv
                . venv/bin/activate
                make check
            """
        }
        echo "end : ${current_stack}"
    }
}


return this
