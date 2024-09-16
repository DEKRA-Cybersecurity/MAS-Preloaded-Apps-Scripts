# Scripts MASA

## Getting started

This Python project is designed to perform static analysis of Android Apps to cover 10 MASA test cases (CODE-1, CODE-2, CRYPTO-1, CRYPTO-3, NETWORK-1, NETWORK-2, NETWORK-3, PLATFORM-2, PLATFORM-3 and STORAGE-2). The main script extracts details such as the APK name, version, urls and permissions requested by the application, based on these parameters and the execution of the test cases, it provides a value that indicates the risk score of a set of applications.

The results of the analysis are stored both in a MySQL database distributed in different tables and in an Excel file or CSV file, which allows easy access and visualization of the data collected. In this excel you can see four tabs which are:

- Report: It stores the hash and app name of each application as well as the result (PASS, FAIL, Needs Review, NA) for each test case.
- Findings: In this sheet it is possible to see for each test case on which file it has matched (some test cases indicate the match line, in other cases it is not possible).
- Total_Fail_Counts: Indicates for each test case how many matches have been found, it is necessary for the calculation of the formula.
- Formula: Indicates the value obtained when calculating the risk score.
- Logging: In case of obtaining failures during the analysis, these will be registered in this table.
- Device_Metadata: In this sheet will be stored the metadata of the device from which the applications have been scanned.

## Installation

The first step is to install the necessary packages using the requirements.txt file by executing the following command:

```
pip install -r requirements.txt
```

In order to register the data in the database, it will be necessary to set up a mysql database following these steps:

- Download and install MySQL database server

```
sudo apt install mysql-server
```

- MySQL should start automatically after installation. However, if it's not started, you can
  start it manually using:

```
sudo systemctl start mysql
```

- Connect as root to create a new user:

```
mysql -u root -p
```

- Create a user named `masa_script`, as in settings.py , and grant it privileges. You could
  also choose other credentials and update the file settings.py

```
mysql> CREATE USER masa_script@localhost IDENTIFIED BY 'MASA123';
mysql> GRANT ALL PRIVILEGES ON *.* TO masa_script@localhost;
mysql> FLUSH PRIVILEGES;
mysql> exit;
```

## Documentation

Once the necessary packages have been installed, it will be necessary to execute the following command to create all the tables and structure of the database:

```
python3 -c "from db.database_utils import first_execution; first_execution()"
```

To complete the configuration of the repository, it will be necessary to clone the [following repository](https://github.com/CookieCrumbs19212/AndScanner) inside the path `/tools`

Inside the project, exists a configuration variables file (`/config/methods_config.yml`) that can be modified to set your preferences. These variables include the export format (xlxs or csv), the use of semgrep during test case execution and the database name. It is important to specify the Android version of the device you are going to analyze (you must choose between 13 or 14 in the `androidVersion` parameter), depending on the version you choose, the script will consider a different set of permissions. Before executing the analysis, it is essential to adjust these variables to your desired values.

If the applications to be scanned belong to a mobile device, it is necessary to fill in the information from the configuration file (`/config/methods_config.yml`). Within this file, there is an object called "metadata" where you must specify the brand, device, name, version_release, ID, version_incremental, type, and tags. If the analysis is performed on a device image, this data will be automatically extracted from the image.

Then, analysis can be initiated. To proceed, store the image of the application or set of applications and execute the file run.sh using the following command:

- In case a device image will be analysed, run:

```
./run.sh VENDOR_NAME
```

`VENDOR_NAME` will be the name of the folder where you have stored the image (`/data/images/<VENDOR_NAME>`)

- In case a set of apps will be analysed, run:

```
./run.sh
```

As a result of the analysis the data obtained will be exported, there are two options CSV or XLXS, to choose the format you must access the configuration file located in the path `/config/methods_config.yml` and give value (True/False) to the variable export*csv. The exported data can be found in the folder `/results/YYYYYYYYYYMMdd_ms*<ID_EXECUTION>/`.

In case you want to delete all the data in the database, you will need to execute the following command:

```
python3 -c "from db.database_utils import clear_database; clear_database()"
```

## Types of Scans

Script can be run in two different ways: through the image of a device or through a set of applications of your choice.

### Device image

To scan the image from a device, it is necessary to store the image in the `/data/images/` folder. Within the `/data/images/` directory, create a subfolder named after the vendor for each image. For example, `/data/images/<VENDOR_NAME>/`.

When inserting the image of a device into the `/<VENDOR_NAME>` folder, it must be a compressed file, such as .zip, .rar or .tar.gz.

### Set of applications

It is also possible to scan a set of applications without the need of a device image. This can be achieved by storing all the applications (apk files) in the following path: `/data/apks/`

To store applications in the apks folder, applications will have to be separated by folders as follows:

- `/MAS-Preloaded-Apps-Scripts`: Main project directory.
  - `/data`: Directory that contains all the necessary data to execute the analysis.
    - `/apks`: Directory that will contain all apks.
      - `/folder_1`: Subdirectory containing apk_1.
        - `app_1.apk`
      - `/folder_2`: Subdirectory containing apk_2.
        - `app_2.apk`
      - `/folder_3`: Subdirectory containing apk_3.
        - `app_3.apk`
      - ...


## Database structure

- `TestSSL_URL:`
  This table stores the URLs that have already been scanned in NETWORK-2 test case and the result.
- `Findings:`
  This table stores all the matches found in the test cases. It stores the hash of the application and the app_name, as well as the category and ID of the test case and the path where the match is located, along with the line number in the file. In some test cases where multiline match is required, it is not possible to get the line number of the match.
- `Report:`
  This table stores the result of the test cases (PASS, FAIL or Need Review), information about the scan and information of the application. The application information stored is the hash, app_name and version_name to identify it. Regarding the scan information, it stores if semgrep option is enabled or not and the version of the script used in the analysis.
- `Total_Fail_Counts:`
  This table stores the hash of the application along with the number of matches found for each test case.
- `Logging:`
  This table stores information about events that occurred during the execution of the script. The hash of the application and the time of the event is also stored, as well as the error message.
- `Permissions:`
  This table stores the Android permissions required by the application.
- `Executions:` This table stores the identifier of the analysis with the timestamp.
- `Device_Metadata:` This table stores the metadata of the device from which the applications have been scanned. 

## Risk Score

To understand the result of the Risk Score, how its value is obtained, what parameters are taken into account and what formula is used, [read this paper](https://docs.google.com/document/d/1dnjXoHpVL5YmZTqVEC9b9JOfu6EzQiizZAHVAeDoIlo/edit).

If you need to recalculate the risk score of an execution, you can do so using the recalculate_risk_score.py script (located in /utils folder). This script allows you to send the ID_EXECUTION of the execution you want to recalculate or the path to the results folder where the CSV files containing the execution's data are located.

```
python3 utils/recalculate_risk_score.py "ID_EXECUTION"
```

or

```
python3 utils/recalculate_risk_score.py "~/MAS-Preloaded-Apps-Scripts/results/YYYYMMdd_HHmmss_ms_ID_EXECUTION"
```

**What is the Shared User Id (SUID)?**
The Shared User Id is a tag found in the AndroidManifest.xml and influences the formula value.

## Additional tools

In order to run the script and get the results, you will need to use additional tools found in the `/tools` directory, which are:

- APKTOOL: A tool that allows you to decompile and recompile APK files. One of APKTool's capabilities is the ability to extract additional APK files and resources that may be present within a main APK.
- JADX: Open source decompiling tool used to convert APK (Android Package) files into Java source code.
- APKSIGNER: Used to confirm that the APK signature will be verified correctly on all versions of the Android platform supported by that APK.
- TESTSSL: Identify and report known vulnerabilities in the SSL/TLS configuration. This may include detection of weak configurations, support for outdated protocol versions, and other security issues.
- SEMGREP: Open-source static analysis tool designed to identify and locate code patterns in source code. Developed to enhance and streamline the process of code review and security analysis, Semgrep employs a pattern-based approach to scan codebases for potential issues, bugs, or security vulnerabilities.
  Test cases CODE-2, CRYPTO-1, NETWORK-2, PLATFORM-3 and STORAGE-2 can be executed using semgrep and the rules developed by OWASP. To do so, access the configuration file located at config/methods_config.yaml and set the value of semgrep tag to True.
- ANDSCANNER: This tool is used to extract the firmware image.

## Adding new test cases

In case you want to add new test cases, you have to follow the next steps:

1. Access the `/config/methods_config.yml` file and add the name of the new test case to the corresponding category (CODE, CRYPTO, NETWORK...) or create a new one if it does not exist.
2. Access the directory `/tests/section/test_name.py` where section will be the name of the category and test_name the name of the test case to be added and copy the new test case.
3. Inside the file `/tests/section/test_name.py` implement the test case code in a method called check(), the parameters that the check() method of all the test cases will receive will always be the same for all of them, which are defined in the file `/utils/auxiliary_functions.py` in the check_app method in the variable all_params. So if you need to add any additional variable you would have to add it in all_params and modify the headers of all the check() methods of each test case adding this/these new variable(s).

If you want the risk score to take into account the newly developed test case, you would have to add to the database tables (Report and Total_Fail_Counts) a new column with the name of the test case in capital letters (in case of adding new test cases to the database, the unit test that checks the formula would become FAIL).

### Unit testing

Once these steps have been followed, the execution of the script will also analyse the newly added test case. To check that no modifications have been made to the results of the rest of the test cases and that they are kept originally, we will check the results of the unit tests.

To perform the execution of the unit tests it is necessary to follow several steps to have the environment correctly set up, since we need to specify the name of the database by means of a config variable (database) and the creation of a database for testing (automated_MASA_TESTING).

1. Execute the database creation command.

```
python3 -c "from db.database_utils import first_execution; first_execution('automated_MASA_TESTING')"
```

2. Access the configuration file and change the value of the `database` variable to `automated_MASA_TESTING`
3. Run an analysis prior to launching the unit tests, our input variables are the apks found in the /unit_tests/reference_apk/\* directory. To run the analysis we have to launch the command:

```
./run.sh True
```

With this command we will run an analysis of the applications but we will use the variables, directories and databases destined for unit tests.

4. Once the database has been created and the testing analysis has been executed, we can launch the unit tests with the command:

```
pytest
```

5. In case you want to launch the unit tests again, it will be necessary to clean the database, to do this we will launch the command:

```
python3 -c "from db.database_utils import clear_database; clear_database('automated_MASA_TESTING')"
```

If you want to re-launch the script with the normal behaviour it will be necessary to revert the changes, to do this we will have to change the value of the variable of the configuration file `database` to `automated_MASA` and launch the script with the command

```
./run.sh
```

## Logging information

### Log: Application was decompiled and no sources folder was found.

If the application does not contain source code directly in the package you are decompiling, jadx will not be able to create a /sources folder because there is simply no source code to extract.

# Branching Strategy and Contributions

This project currently uses a two-branch strategy to manage development and releases. Below is an explanation of the purpose of each branch and guidelines for contributing to the project.

`Main Branch (main)`

- Purpose: The main branch contains the primary, stable codebase of the project. This is the branch that end users should use to run the project.
- Use: If you are using the project for its intended purpose and do not plan to develop new features, clone or download the main branch.

`Development Branch (dev)`

- Purpose: The dev branch is used for ongoing development and testing of new features. It serves as the integration branch where feature branches are merged after development.
- Use: If you plan to contribute to the project by developing new features or making improvements, you should work with the dev branch.

## Contribution Workflow

1. Create a feature branch:

   - When you start working on a new feature or fix, create a new branch from dev with a descriptive name (e.g., feature/login-improvement or bugfix/header-alignment).

   ```
   git checkout dev
   git checkout -b feature/your-feature-name
   ```

2. Develop your feature:

   - Implement your changes and commit them to your feature branch. Make sure your commits are atomic and have meaningful messages.

3. Push your feature branch:

   - Push your feature branch to the remote repository.

   ```
   git push origin feature/your-feature-name
   ```

4. Create a pull request:

   - Once your feature is complete and tested, create a pull request (PR) to merge your feature branch into dev. Describe the changes you have made and any relevant details.
   - Make sure your PR conforms to the project's contribution guidelines and passes all automated tests.

5. Review and merge:
   - Your PR will be reviewed by the maintainers. After approval and successful testing, it will be merged into the dev branch.
   - Periodically, stable changes from dev will be merged into main.
