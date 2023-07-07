import sys

from src.ast.assign_visitor import AssignVisitor
from src.log_modules.util import getAst
from src.stork import Stork


def retrieve_variable_from_assignment(assignment, assignment_list):
    print(f"method call, length of assignments: {len(assignment_list)}")
    data_file = has_data_file(assignment=assignment)
    try:
        if data_file:
            for item in assignment_list:
                # print(f"Item: {item}")
                if data_file[0] == item["variable"]:
                    # print(f"Assignment: {item}")
                    # print(f"Path to dataset from variable {item['variable']}: {item['data_source'][0]}")
                    last_change = find_closest_assignment(assignment=assignment, assignment_list=assignment_list)
                    print(f"Closest variable: {last_change}, to the assignment: {assignment}")
    except (NameError, AttributeError) as e:
        print(e)

def retrieve_variable_from_assignment_list(assignment_list):
    print(f"method call, length of assignments: {len(assignment_list)}")
    for assignment in assignment_list:
        data_file = has_data_file(assignment=assignment)
        try:
            if data_file:
                for item in assignment_list:
                    # print(f"Item: {item}")
                    if data_file[0] == item["variable"]:
                        # print(f"Assignment: {item}")
                        # print(f"Path to dataset from variable {item['variable']}: {item['data_source'][0]}")
                        last_change = find_closest_assignment(assignment=assignment, assignment_list=assignment_list)
                        print(f"Closest variable: {last_change}, to the assignment: {assignment}")
        except (NameError, AttributeError) as e:
            print(e)




def find_closest_assignment(assignment, assignment_list):
    diff = sys.maxsize
    closest = None
    destination_line = assignment['lineno']
    for item in assignment_list:
        if destination_line - item['lineno'] < diff:
            diff = destination_line - item['lineno']
            if diff <= 0:
                break
            closest = item
    return closest


def has_data_file(assignment):
    for source in assignment["data_source"]:
        if isinstance(source, dict):
            try:
                return source["data_file"]
            except KeyError as e:
                print(e)
                return False


def has_data_file_single_source(source):
    if isinstance(source, dict):
        try:
            return source["data_file"]
        except KeyError as e:
            print(e)
            return False

#
# # TODO Check duplicates in the variable list. When having duplicates, a full pass
# #  of the assignment list needs to be finished. REVISIT
#
# # def check_duplicates(variables):
# #     duplicate = False
# #     for variable in variables:
# #         for item in variables:
# #             if variable['variable'] == item['variable']:
# #                 duplicate = True
#

if __name__ == '__main__':
    stork = Stork(config_path=r"../db_conn/config_s3.ini")
    pipeline = "../log_modules/variable_path_reading.py"

    # pipeline = "../examples/argus_eyes.py"
    # stork.setup(pipeline=pipeline, new_pipeline="../log_modules/variable_path_reading_var_retrieval.py")

    stork.setClient(stork.access_key, stork.secret_access_key)
    stork.assignVisitor = AssignVisitor()
    tree = getAst(pipeline=pipeline)
    stork.assignVisitor.setPipeline(pipeline=pipeline)
    stork.assignVisitor.visit(tree)

    assignments = stork.assignVisitor.assignments

    print(f"Assignments: {assignments}")

    variables = [{'variable': assignment["variable"], 'lineno': assignment["lineno"]} for assignment in assignments]
    print(f"Variables: {variables}")

    retrieve_variable_from_assignment(assignment_list=assignments)
