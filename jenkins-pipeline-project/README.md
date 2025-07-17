# Jenkins Pipeline Project

This project contains a Jenkins pipeline script specifically designed for the development environment `dev01`. The pipeline is structured to manage the deployment and integration of various components in a defined order.

## Project Structure

- **pipelines/jenkin_dev01.groovy**: This file contains the Jenkins pipeline script for the `dev01` environment. It defines the stack in the following order:
  - `data_libraries`
  - `data_delivery`
  - Additional components as necessary for the pipeline execution.

## Usage Instructions

1. **Setup Jenkins**: Ensure that Jenkins is installed and configured on your server.
2. **Create a New Pipeline**: In Jenkins, create a new pipeline job and point it to the `jenkin_dev01.groovy` script located in the `pipelines` directory.
3. **Run the Pipeline**: Trigger the pipeline to execute the defined stages in the specified order.

## Additional Information

For further customization or additional stages, modify the `jenkin_dev01.groovy` file as needed. Ensure that all dependencies are properly managed and that the environment is set up to support the execution of the pipeline.