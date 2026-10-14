import os
os.environ["FORGE_DB_PATH"] = "sample_digital_twin.db"

import database
from models import load_tolerance_stack, load_all_current_part_requirements, load_part_requirement, load_vehicle_requirement
from build_sample_db import build_sample_db

def get_current_stack_ids() -> list[str]:
    current_stack_ids = []
    for row in database.get_all_current_stacks():
        current_stack_ids.append(row["id"])
    return current_stack_ids

def get_current_part_requirement_ids() -> list[str]:
    current_part_requirement_ids = []
    for row in database.get_latest_part_requirements():
        current_part_requirement_ids.append(row["id"])
    return current_part_requirement_ids

def get_current_vehicle_requirement_ids() -> list[str]:
    current_vehicle_requirement_ids = []
    for row in database.get_latest_vehicle_requirements():
        current_vehicle_requirement_ids.append(row["id"])
    return current_vehicle_requirement_ids

def display_all_current_stacks():
    print("These are the current tolerance stack in the system:")
    for row in database.get_all_current_stacks():
        print(f"{row["id"]} Rev {row["revision"]} - {row["description"]} - {row["target_requirement_id"]}")

def load_current_revision_of_selected_stack():
    current_stack_ids = get_current_stack_ids()
    if not current_stack_ids:
        print("There are no current tolerance stacks in the system")
    else:
        valid_stack_id = False

        while not valid_stack_id:
            requested_stack_id = input("\nWhich tolerance stack would you like to load?\nPlease enter the corresponding tolerance stack ID or enter 'q' to stop the selection.\n").strip()
            if requested_stack_id in current_stack_ids:
                valid_stack_id = True
            elif requested_stack_id == "q":
                print("Selection stopped.")
                return
            else:
                print("This was not a valid tolerance stack ID. Please enter a valid ID.")

        active_stack = load_tolerance_stack(stack_id= requested_stack_id, status= "current")

        print(f"\nSelected Stack: {active_stack.id} Rev {active_stack.revision} - status: {active_stack.life_cycle_status}")
        print(f"Result: ±{active_stack.stack_result():.2f}")
        print(f"Target: {active_stack.target.id} Rev {active_stack.target.revision}")
        if active_stack.target_validation():
            print(f"Target met - Target usage: {active_stack.target_usage():.2f}%")
        else:
            print(f"Target exceeded - Target usage: {active_stack.target_usage():.2f}%")
        for contributor in active_stack.contributors:
            print(f"{contributor.id} Rev {contributor.revision} - {contributor.description} - ±{contributor.half_range:.2f}")
        print(f"Are these contributors up to date: {active_stack.inputs_are_current(load_all_current_part_requirements())}")
        print(f"Target is up to date: {active_stack.target_is_current()}")

def display_all_current_part_requirements() -> None:
    for row in database.get_latest_part_requirements():
        print(f"{row["id"]} Rev {row["revision"]} - {row["part"]} - {row["description"]}")

def load_selected_part_requirement():
    current_part_requirement_ids = get_current_part_requirement_ids()
    if not current_part_requirement_ids:
        print("There are no part requirements in the system.")
    else:
        valid_requirement_id = False

        while not valid_requirement_id:
            requested_requirement_id = input("\nWhich part requirement would you like to load?\nPlease enter the corresponding part requirement ID or enter 'q' to stop the selection.\n").strip()
            if requested_requirement_id in current_part_requirement_ids:
                valid_requirement_id = True
            elif requested_requirement_id == "q":
                print("Selection stopped.")
                return
            else:
                print("This was not a valid part requirement ID. Please enter a valid ID.")

        active_requirement = load_part_requirement(requested_requirement_id)

        print(f"\nSelected: {active_requirement.id} Rev {active_requirement.revision} - {active_requirement.description}")
        print(f"Part: {active_requirement.part}")
        print(f"Tolerance Type: {active_requirement.category} | Upper Limit: {active_requirement.upper_limit} | Lower Limit: {active_requirement.lower_limit}")

def display_all_current_vehicle_requirements() -> None:
    for row in database.get_latest_vehicle_requirements():
        print(f"{row["id"]} Rev {row["revision"]} - {row["program"]} - {row["description"]}")

def load_selected_vehicle_requirement():
    current_vehicle_requirement_ids = get_current_vehicle_requirement_ids()
    if not current_vehicle_requirement_ids:
        print("There are no part requirements in the system.")
    else:
        valid_requirement_id = False

        while not valid_requirement_id:
            requested_requirement_id = input("\nWhich vehicle requirement would you like to load?\nPlease enter the corresponding vehicle requirement ID or enter 'q' to stop the selection.\n").strip()
            if requested_requirement_id in current_vehicle_requirement_ids:
                valid_requirement_id = True
            elif requested_requirement_id == "q":
                print("Selection stopped.")
                return
            else:
                print("This was not a valid vehicle requirement ID. Please enter a valid ID.")

        active_requirement = load_vehicle_requirement(requested_requirement_id)

        print(f"\nSelected: {active_requirement.id} Rev {active_requirement.revision} - {active_requirement.description}")
        print(f"Program: {active_requirement.program} | System: {active_requirement.system}")
        print(f"Nominal: {active_requirement.nominal} | Upper Limit: {active_requirement.upper_tol_limit} | Lower Limit: {active_requirement.lower_tol_limit}")

def user_sample_reset_check():
    user_reset_request = input("Would you like to rebuild the initial sample database?\nWARNING:A reset will DELETE all the current database content and create a set of NEW sample data.\nIf you want to reset the database to its initial sample state enter 'y'. ").strip().lower()

    if user_reset_request == "y":
        build_sample_db()

if __name__ == "__main__":
    database.create_tables()
    user_sample_reset_check()
    stop_program = False
    while not stop_program:
        print("\nMENU")
        print("-"*40)
        print("1 - Display current Tolerance Stacks")
        print("2 - Display Part Requirements")
        print("3 - Display Vehicle Requirements")
        print("q - Quit program")
        user_menu_input = input("What would you like to do? ").strip().lower()
        if user_menu_input == "1":
            display_all_current_stacks()
            load_current_revision_of_selected_stack()
        elif user_menu_input == "2":
            display_all_current_part_requirements()
            load_selected_part_requirement()
        elif user_menu_input =="3":
            display_all_current_vehicle_requirements()
            load_selected_vehicle_requirement()
        elif user_menu_input == "q":
            stop_program = True
            input("Good Bye!")
        else:
            print("You did not enter a valid option. Please try again.")
    database.connection.close()