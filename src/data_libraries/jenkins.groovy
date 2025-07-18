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

def checkUnitTestsDataLibraries(String stack) {
    echo "stack name : ${stack}"
    stage("Check UnitTests-Linter ${stack}") {
        dir("src/data_libraries/${stack}") {
            sh """
                python3 -m venv venv
                . venv/bin/activate
                make check
                python3 --version
                python3 -m pytest tests/ --cov=${stack} --cov-report=term-missing -v
                
            """
        }
        echo "end checkUnitTestsDataLibraries for : ${stack}"
    }
}




// after merge
def checkAfterMerge(def context) {
  //  check
}

return this
