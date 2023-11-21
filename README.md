# Scripts MASA

## Getting started

This Python project is designed to perform static analysis of Android Apps to cover 10 MASA test cases (CODE-1, CODE-2, CRYPTO-1, CRYPTO-3, NETWORK-1, NETWORK-2, NETWORK-3, PLATFORM-2, PLATFORM-3 and STORAGE-2). The main script extracts details such as the APK name, version, urls and permissions requested by the application, based on these parameters and the execution of the test cases, it provides a value that indicates the risk score of a set of applications.

The results of the analysis are stored both in a MySQL database distributed in different tables and in an Excel file, which allows easy access and visualization of the data collected. In this excel you can see four tabs which are:
- Report: It stores the hash and app name of each application as well as the result (PASS, FAIL, INCONCLUSIVE, NA) for each test case.
- Total_Fail_Counts: Indicates for each test case how many matches have been found, it is necessary for the calculation of the formula.
- Formula: Indicates the value obtained when calculating the risk score.
- Logging: In case of obtaining failures during the analysis, these will be registered in this table.

## Installation
The first step is to install the necessary packages using the requirements.txt file by executing the following command:
```
pip install -r requirements.txt
```

In order to register the data in the database, it will be necessary to set up a mysql database and modify the variables **DB_USER_MASA** and **DB_PASSWORD_MASA** in the settings.py file.

## Documentation

Once the necessary packages have been installed, a folder called apks has to be created, where the apks to be analysed will be stored.
To store applications in the apks folder, applications will have to be separated by folders as follows:

- `/scripts-masa`: Main project directory.
    - `/apks`: Directory that will contain all apks.
        - `/folder_1`: Subdirectory containing apk_1.
            - `app_1.apk`
        - `/folder_2`: Subdirectory containing apk_2.
            - `app_2.apk`
        - `/folder_3`: Subdirectory containing apk_3.
            - `app_3.apk`
        - ...

Once the database has been created, it will be necessary to execute the following command to create all the tables and structure of the database:
```
python3 -c "from db.database_utils import first_execution; first_execution()"
```

With the applications already stored in `/apks` and the database tables created, it is now possible to run the script using the following command:
```
./automate_apps_updated
```
As a result of the analysis, an excel file called **Preload_Analysis.xlsx**  will be provided, which will be located inside the `/apks` folder.
In case you want to delete all the data in the database, you will need to execute the following command:
```
python3 -c "from db.database_utils import clear_database; clear_database()"
```

## Additional tools
In order to run the script and get the results, you will need to use additional tools found in the `/tools` directory, which are:
 - APKTOOL: A tool that allows you to decompile and recompile APK files. One of APKTool's capabilities is the ability to extract additional APK files and resources that may be present within a main APK.
 - JADX: Open source decompiling tool used to convert APK (Android Package) files into Java source code.
 - APKSIGNER: Used to confirm that the APK signature will be verified correctly on all versions of the Android platform supported by that APK.
 - TESTSSL: Identify and report known vulnerabilities in the SSL/TLS configuration. This may include detection of weak configurations, support for outdated protocol versions, and other security issues.

## Adding new test cases
In case you want to add new test cases, you have to follow the next steps:
1. Access the `/config/methods_config.yml` file and add the name of the new test case to the corresponding category (CODE, CRYPTO, NETWORK...) or create a new one if it does not exist.
2. Access the directory `/tests/section/test_name.py` where section will be the name of the category and test_name the name of the test case to be added and copy the new test case.
3. Inside the file `/tests/section/test_name.py` implement the test case code in a method called check(), the parameters that the check() method of all the test cases will receive will always be the same for all of them, which are defined in the file `/utils/auxiliary_functions.py` in the check_app method in the variable all_params. So if you need to add any additional variable you would have to add it in all_params and modify the headers of all the check() methods of each test case adding this/these new variable(s). 

Once these steps have been followed, the execution of the script will also analyse the newly added test case. To check that no modifications have been made to the results of the rest of the test cases and that they are kept originally, we will check the results of the unit tests by executing the command:
```
pytest
```

If you want the risk score to take into account the newly developed test case, you would have to add to the database tables (Report and Total_Fail_Counts) a new column with the name of the test case in capital letters (in case of adding new test cases to the database, the unit test that checks the formula would become FAIL).