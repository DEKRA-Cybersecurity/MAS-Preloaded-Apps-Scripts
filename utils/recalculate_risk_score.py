import formula
import os
import yaml
import sys
import auxiliar_functions
import pandas as pd
import uuid
sys.path.append('./')

main_path = os.getcwd()


def calculate_risk_score(id_execution):
    if id_execution == "":
        print("Specify an execution ID to recalculate the risk score.")
    else:
        with open('config/methods_config.yml') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        tests_list = [value.upper() for values in config['tests'].values()
                      for value in values]

        risk_score = formula.calculate_formula(
            0.01, 0.01, tests_list, str(id_execution))
        print("The risk score have been recalculated. The new value is " +
              str(risk_score) + '.')
        return risk_score


def update_formula_CSV(execution_folder, risk_score):

    formula_csv_path = auxiliar_functions.get_formula_csv_path(execution_folder)

    try:
        df = pd.read_csv(formula_csv_path, header=None)
        df.at[1, 0] = str(risk_score)
        df.to_csv(formula_csv_path, index=False, header=False)
    except FileNotFoundError:
        df = pd.DataFrame()


def main():

    id_execution = ''
    execution_folder = ''

    if not is_uuid:
        execution_folder = param
        id_execution = uuid.uuid4()
        print(id_execution)
        auxiliar_functions.insert_values(id_execution, param)
    else: 
        id_execution = param
        folder = auxiliar_functions.get_full_folder_path(results_path, id_execution)
        execution_folder = os.path.join(results_path, folder)

    risk_score = calculate_risk_score(id_execution)
    update_formula_CSV(execution_folder, risk_score)


def check_uuid(param):
    try:
        uuid_obj = uuid.UUID(param, version=4)
        return str(uuid_obj) == param
    except ValueError:
        return False


if __name__ == "__main__":

    try:
        param = sys.argv[1]
        is_uuid = check_uuid(param)
        results_path = os.path.join(main_path, 'results')
        sys.exit(main())
    except IndexError as e:
        print("Specify an execution ID to recalculate the risk score.")
    except Exception as e:
        print(e)
