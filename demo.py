import os
os.environ["FORGE_DB_PATH"] = "sample_digital_twin.db"

import database
from models import load_tolerance_stack, load_all_current_part_requirements, load_vehicle_requirement
from build_sample_db import build_sample_db

def get_current_stack_ids() -> list[str]:
    current_stack_ids = []
    for row in database.get_all_current_stacks():
        current_stack_ids.append(row["id"])
    return current_stack_ids

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
            requested_stack_id = input("\nWhich tolerance stack would you like to load? Please enter the corresponding tolerance stack id or enter 'q' to stop the selection.\n").strip()
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

def user_sample_reset_check():
    user_reset_request = input("Would you like to rebuild the initial sample database?\nWARNING:A reset will DELETE all the current database content and create a set of NEW sample data.\nIf you want to reset the database to its initial sample state enter 'y'. ").strip().lower()

    if user_reset_request == "y":
        build_sample_db()

if __name__ == "__main__":
    database.create_tables()
    user_sample_reset_check()
    stop_program = False
    while not stop_program:
        print("MENU")
        print("-"*40)
        print("1 - Display current Tolerance Stacks")
        print("q - Quit program")
        user_menu_input = input("What would you like to do?").strip().lower()
        if user_menu_input == "1":
            display_all_current_stacks()
            load_current_revision_of_selected_stack()
        elif user_menu_input == "q":
            stop_program = True
            input("Good Bye!")
        else:
            print("You did not enter a valid option. Please try again.")
    database.connection.close()