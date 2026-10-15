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

def update_selected_part_requirement(active_requirement) -> None:
    update_details = {
        "description": None,
        "nominal": None,
        "upper_limit": None,
        "lower_limit": None,
        "datums": None,
        "log_comment": None
    }
    user_update_request = input("If you want to update this requirement enter 'y'. ").strip().lower()
    if user_update_request == "y":
        update_finished = False
        while not update_finished:
            print("\nUpdate Options:")
            print(f"1 - description -> {active_requirement.description} (current update input: {update_details['description']})")
            print(f"2 - nominal -> {active_requirement.nominal} (current update input: {update_details['nominal']})")
            print(f"3 - upper tolerance limit -> {active_requirement.upper_limit} (current update input: {update_details['upper_limit']})")
            print(f"4 - lower tolerance limit -> {active_requirement.lower_limit} (current update input: {update_details['lower_limit']})")
            print(f"5 - datums -> {active_requirement.datums} (current update input: {update_details['datums']})")
            print(f"6 - add comment (current update input: {update_details['log_comment']})")
            print("f - to confirm the update and safe a new revision with the updated details")
            print("q - cancel update")
            user_choice = input("What would you like to update?\n")
            match user_choice:
                case "1":
                    if update_details["description"] is None:
                        user_input = input(f"Current DESCRIPTION: {active_requirement.description}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current DESCRIPTION: {active_requirement.description}\nCurrently to be updated to: {update_details["description"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["description"] = update_details["description"]
                    elif user_input == "":
                        update_details["description"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        update_details["description"] = user_input

                case "2":
                    if update_details["nominal"] is None:
                        user_input = input(f"Current NOMINAL: {active_requirement.nominal}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current NOMINAL: {active_requirement.nominal}\nCurrently to be updated to: {update_details["nominal"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["nominal"] = update_details["nominal"]
                    elif user_input == "":
                        update_details["nominal"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        try:
                            update_details["nominal"] = float(user_input)
                        except ValueError:
                            print("Please enter a numerical value to change the nominal.")

                case "3":
                    if update_details["upper_limit"] is None:
                        user_input = input(f"Current UPPER TOLERANCE LIMIT: {active_requirement.upper_limit}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current UPPER TOLERANCE LIMIT: {active_requirement.upper_limit}\nCurrently to be updated to: {update_details["upper_limit"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["upper_limit"] = update_details["upper_limit"]
                    elif user_input == "":
                        update_details["upper_limit"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        try:
                            update_details["upper_limit"] = float(user_input)
                        except ValueError:
                            print("Please enter a numerical value to change the upper tolerance limit.")

                case "4":
                    if update_details["lower_limit"] is None:
                        user_input = input(f"Current LOWER TOLERANCE LIMIT: {active_requirement.lower_limit}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current LOWER TOLERANCE LIMIT: {active_requirement.lower_limit}\nCurrently to be updated to: {update_details["lower_limit"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["lower_limit"] = update_details["lower_limit"]
                    elif user_input == "":
                        update_details["lower_limit"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        try:
                            update_details["lower_limit"] = float(user_input)
                        except ValueError:
                            print("Please enter a numerical value to change the lower tolerance limit.")

                case "5":
                    if update_details["datums"] is None:
                        print(f"Current DATUMS: {active_requirement.datums}")
                    else:
                        print(f"Current DATUMS: {active_requirement.datums}\nCurrently to be updated to: {update_details["datums"]}")
                    user_input_primary = input("Enter the updated primary datum, hit enter if there should be no primary datum or enter 'q' to cancel and not make any changes: ").strip()
                    if user_input_primary.lower() == "q":
                        update_details["datums"] = update_details["datums"]
                    elif user_input_primary == "":
                        update_details["datums"] = []
                    else:
                        update_details["datums"] = [user_input_primary.upper()]
                        user_input_secondary = input("Enter the updated secondary datum or enter 'q' to cancel and update to only a primary datum: ").strip()
                        if user_input_secondary.lower() == "q" or user_input_secondary == "":
                            update_details ["datums"] = update_details["datums"]
                        else:
                            update_details["datums"].append(user_input_secondary.upper())
                            user_input_tertiary = input("Enter the updated tertiary datum, hit enter if there should be no tertiary datum or enter 'q' to cancel and update to only a primary datum and secondary datum: ").strip()
                            if user_input_tertiary.lower() == "q" or user_input_tertiary == "":
                                update_details["datums"] = update_details["datums"]
                            else:
                                update_details["datums"].append(user_input_tertiary.upper())

                case "6":
                    if update_details["log_comment"] is None:
                        user_input = input("What comment do you want to add? If you don't want to comment enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Currently the added comment will be: {update_details["log_comment"]}\nWhat do you want to change it to? If you don't want to make any changes 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["log_comment"] = update_details["log_comment"]
                    elif user_input == "":
                        update_details["log_comment"] = None
                        print("you made no entry no comment will be added to the update")
                    else:
                        update_details["log_comment"] = user_input

                case "f":
                    if all(entry is None for entry in update_details.values()):
                        print("You staged no changes to update. Please enter the values you want to update or enter 'q' to cancel the update.")
                    else:
                        active_requirement.update(
                            update_details["description"],
                            update_details["nominal"],
                            update_details["upper_limit"],
                            update_details["lower_limit"],
                            update_details["datums"],
                            update_details["log_comment"]
                        )
                        update_finished = True

                case "q":
                    print("update cancelled")
                    update_finished = True

                case _:
                    print("This was not a valid selection. Please try again.")

def update_selected_vehicle_requirement(active_requirement) -> None:
    update_details = {
        "description": None,
        "nominal": None,
        "upper_limit": None,
        "lower_limit": None,
        "log_comment": None
    }
    user_update_request = input("If you want to update this requirement enter 'y'. ").strip().lower()
    if user_update_request == "y":
        update_finished = False
        while not update_finished:
            print("\nUpdate Options:")
            print(f"1 - description -> {active_requirement.description} (current update input: {update_details['description']})")
            print(f"2 - nominal -> {active_requirement.nominal} (current update input: {update_details['nominal']})")
            print(f"3 - upper tolerance limit -> {active_requirement.upper_limit} (current update input: {update_details['upper_limit']})")
            print(f"4 - lower tolerance limit -> {active_requirement.lower_limit} (current update input: {update_details['lower_limit']})")
            print(f"5 - add comment (current update input: {update_details['log_comment']})")
            print("f - to confirm the update and safe a new revision with the updated details")
            print("q - cancel update")
            user_choice = input("What would you like to update?\n")
            match user_choice:
                case "1":
                    if update_details["description"] is None:
                        user_input = input(f"Current DESCRIPTION: {active_requirement.description}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current DESCRIPTION: {active_requirement.description}\nCurrently to be updated to: {update_details["description"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["description"] = update_details["description"]
                    elif user_input == "":
                        update_details["description"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        update_details["description"] = user_input

                case "2":
                    if update_details["nominal"] is None:
                        user_input = input(f"Current NOMINAL: {active_requirement.nominal}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current NOMINAL: {active_requirement.nominal}\nCurrently to be updated to: {update_details["nominal"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["nominal"] = update_details["nominal"]
                    elif user_input == "":
                        update_details["nominal"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        try:
                            update_details["nominal"] = float(user_input)
                        except ValueError:
                            print("Please enter a numerical value to change the nominal.")

                case "3":
                    if update_details["upper_limit"] is None:
                        user_input = input(f"Current UPPER TOLERANCE LIMIT: {active_requirement.upper_limit}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current UPPER TOLERANCE LIMIT: {active_requirement.upper_limit}\nCurrently to be updated to: {update_details["upper_limit"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["upper_limit"] = update_details["upper_limit"]
                    elif user_input == "":
                        update_details["upper_limit"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        try:
                            update_details["upper_limit"] = float(user_input)
                        except ValueError:
                            print("Please enter a numerical value to change the upper tolerance limit.")

                case "4":
                    if update_details["lower_limit"] is None:
                        user_input = input(f"Current LOWER TOLERANCE LIMIT: {active_requirement.lower_limit}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Current LOWER TOLERANCE LIMIT: {active_requirement.lower_limit}\nCurrently to be updated to: {update_details["lower_limit"]}\nWhat do you want to change it to? If you don't want to make any changes to this detail enter 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["lower_limit"] = update_details["lower_limit"]
                    elif user_input == "":
                        update_details["lower_limit"] = None
                        print("you made no entry and the field can not be empty. No update value stored.")
                    else:
                        try:
                            update_details["lower_limit"] = float(user_input)
                        except ValueError:
                            print("Please enter a numerical value to change the lower tolerance limit.")

                case "5":
                    if update_details["log_comment"] is None:
                        user_input = input("What comment do you want to add? If you don't want to comment enter 'q'.\n").strip()
                    else:
                        user_input = input(f"Currently the added comment will be: {update_details["log_comment"]}\nWhat do you want to change it to? If you don't want to make any changes 'q'.\n").strip()
                    if user_input.lower() == "q":
                        update_details["log_comment"] = update_details["log_comment"]
                    elif user_input == "":
                        update_details["log_comment"] = None
                        print("you made no entry no comment will be added to the update")
                    else:
                        update_details["log_comment"] = user_input

                case "f":
                    if all(entry is None for entry in update_details.values()):
                        print("You staged no changes to update. Please enter the values you want to update or enter 'q' to cancel the update.")
                    else:
                        active_requirement.update(
                            update_details["description"],
                            update_details["nominal"],
                            update_details["upper_limit"],
                            update_details["lower_limit"],
                            update_details["log_comment"]
                        )
                        update_finished = True

                case "q":
                    print("update cancelled")
                    update_finished = True

                case _:
                    print("This was not a valid selection. Please try again.")

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

        return active_requirement

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
        print(f"Nominal: {active_requirement.nominal} | Upper Limit: {active_requirement.upper_limit} | Lower Limit: {active_requirement.lower_limit}")

        return active_requirement

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
            active_requirement = load_selected_part_requirement()
            if active_requirement:
                update_selected_part_requirement(active_requirement)
        elif user_menu_input =="3":
            display_all_current_vehicle_requirements()
            active_requirement = load_selected_vehicle_requirement()
            if active_requirement:
                update_selected_vehicle_requirement(active_requirement)
        elif user_menu_input == "q":
            stop_program = True
            input("Good Bye!")
        else:
            print("You did not enter a valid option. Please try again.")
    database.connection.close()