from pathlib import Path
import database

from models import RequirementCategory, PartRequirement, VehicleRequirement, ToleranceStack, load_vehicle_requirement, load_part_requirement, load_tolerance_stack, load_all_current_part_requirements

def reset_sample_db():
    with database.connection:
        cursor = database.connection.cursor()
        cursor.execute("""
            SELECT file
            FROM pragma_database_list
            WHERE name = "main"
        """)
        main_row = cursor.fetchone()
        expected_path = Path(__file__).parent / "sample_digital_twin.db"
        if Path(main_row["file"]).resolve() != expected_path.resolve():
            raise ValueError (
                "Reset was stopped because the connection points to the wrong database."
            )
        cursor.execute("""
            DELETE FROM contributors
        """)
        cursor.execute("""
            DELETE FROM tolerance_stacks
        """)
        cursor.execute("""
            DELETE FROM part_requirements
        """)
        cursor.execute("""
            DELETE FROM vehicle_requirements
        """)

def build_sample_db():
    reset_sample_db()

    PartRequirement(
        id= "SAMPLE_PR_001",
        revision= 1,
        part = "SAMPLE_PART_001",
        description= "Front bumper lateral position",
        category= RequirementCategory.POSITION,
        nominal= 0.0,
        upper_limit= 0.5,
        lower_limit= -0.5,
        datums= ["A", "B", "C"],
        log_comment= "Sample requirement"
    ).save_part_requirement()

    PartRequirement(
        id= "SAMPLE_PR_002",
        revision= 1,
        part = "SAMPLE_PART_002",
        description= "Headlamp lateral position",
        category= RequirementCategory.POSITION,
        nominal= 0.0,
        upper_limit= 0.35,
        lower_limit= -0.35,
        datums= ["A", "B", "C"],
        log_comment= "Sample requirement"
    ).save_part_requirement()

    PartRequirement(
        id= "SAMPLE_PR_003",
        revision= 1,
        part = "SAMPLE_PART_003",
        description= "Headlamp mounting position",
        category= RequirementCategory.POSITION,
        nominal= 0.0,
        upper_limit= 0.2,
        lower_limit= -0.2,
        datums= ["A", "B", "C"],
        log_comment= "Sample requirement"
    ).save_part_requirement()

    VehicleRequirement(
        id= "SAMPLE_VR_001",
        revision= 1,
        program= "SAMPLE_PROGRAM_001",
        system= "Front",
        description= "Front bumper-to-headlamp gap",
        nominal= 3.0,
        upper_tol_limit= 0.8,
        lower_tol_limit= -0.8,
        log_comment= "1st sample vehicle requirement"
    ).save_vehicle_requirement()

    ToleranceStack(
        id= "SAMPLE_TS_001",
        revision= 1,
        description= "Front bumper-to-headlamp gap",
        vehicle_requirement= load_vehicle_requirement("SAMPLE_VR_001")
    ).save_stack()

    active_stack = load_tolerance_stack(stack_id= "SAMPLE_TS_001", status= "latest")
    active_stack.add_contributor(load_part_requirement("SAMPLE_PR_001"))
    active_stack.add_contributor(load_part_requirement("SAMPLE_PR_002"))
    active_stack.add_contributor(load_part_requirement("SAMPLE_PR_003"))
    active_stack.wip_to_current()

    VehicleRequirement(
        id= "SAMPLE_VR_002",
        revision= 1,
        program= "SAMPLE_PROGRAM_001",
        system= "Front",
        description= "Front bumper-to-headlamp tighter gap demonstration",
        nominal= 3.0,
        upper_tol_limit= 0.5,
        lower_tol_limit= -0.5,
        log_comment= "tighter sample vehicle requirement"
    ).save_vehicle_requirement()

    ToleranceStack(
        id= "SAMPLE_TS_002",
        revision= 1,
        description= "Tighter gap target demonstration",
        vehicle_requirement= load_vehicle_requirement("SAMPLE_VR_002")
    ).save_stack()

    active_stack = load_tolerance_stack(stack_id= "SAMPLE_TS_002", status= "latest")
    active_stack.add_contributor(load_part_requirement("SAMPLE_PR_001"))
    active_stack.add_contributor(load_part_requirement("SAMPLE_PR_002"))
    active_stack.add_contributor(load_part_requirement("SAMPLE_PR_003"))
    active_stack.wip_to_current()

    load_part_requirement("SAMPLE_PR_003").update(upper_limit= 0.4, lower_limit= -0.4, log_comment= "Revised sample mounting capability")

    active_stack = load_tolerance_stack(stack_id= "SAMPLE_TS_001", status= "latest")
    active_stack.check_for_updates(load_all_current_part_requirements())
    
    active_stack = load_tolerance_stack(stack_id= "SAMPLE_TS_001", status= "latest")
    active_stack.accept("contributor update confirmed")

