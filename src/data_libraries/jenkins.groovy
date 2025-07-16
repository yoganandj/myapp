current_stack ="data_libraries"

sonarProjectName = "myapp_${current_stack}"
sonarProjectKey = "myapp_${current_stack}"
sonarProjectBaseDir = "src/${current_stack}"
sonarSource = "data_logging/data_logging"
sonarTestSource = "data_logging/test"
sonarTestCoverage = "data_logging/reports/coverage.xml"
sonarTestReport = "data_logging/reports/test.xml"

def checkUnitTests(String stack) {
    stage("Check UnitTests-Linter ${stack}") {
        dir("src/${stack}") {
            sh "make check"
        }
    }
}


return this
