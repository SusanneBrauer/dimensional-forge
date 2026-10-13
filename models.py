from database import connection, get_latest_part_requirement, get_latest_part_requirements, get_latest_vehicle_requirement, get_latest_vehicle_requirements, get_current_tolerance_stack, get_latest_tolerance_stack_revision, get_rev_of_part_requirement, get_rev_of_vehicle_requirement, get_revision_of_stack, get_contributors_for_tolerance_stack

from typing import Literal
from enum import Enum
import math
import copy
import sqlite3

class RequirementCategory(Enum):
    POSITION = "Position"
    PROFILE = "Profile"
    SIZE ="Size"

class PartRequirement:
    def __init__(
        self,
        id: str,
        revision: int,
        part: str,
        description: str,
        category: RequirementCategory,
        nominal: float,
        upper_limit: float,
        lower_limit: float,
        datums: list[str],
        log_comment: str
    ):
        self.id = id
        self.revision = revision
        self.part = part
        self.description = description
        self.category = category.value
        self.nominal = nominal
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.datums = datums
        self.log = log_comment
    def tolerance_range(self) -> float:
        return self.upper_limit - self.lower_limit
    def upper_boundary(self) -> float:
        return self.nominal + self.upper_limit
    def lower_boundary(self) -> float:
        return self.nominal + self.lower_limit
    def save_part_requirement(self) -> None:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO part_requirements (
                id,
                revision,
                part,
                description,
                category,
                nominal,
                upper_limit,
                lower_limit,
                primary_datum,
                secondary_datum,
                tertiary_datum,
                log_comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.id,
                self.revision,
                self.part,
                self.description,
                self.category,
                self.nominal,
                self.upper_limit,
                self.lower_limit,
                self.datums[0],
                self.datums[1],
                self.datums[2],
                self.log
            )
        )
        connection.commit()
    def update(
            self,
            description: str | None = None,
            nominal: float | None = None,
            upper_limit: float | None = None,
            lower_limit: float | None = None,
            datums: list[str] | None =  None,
            log_comment: str | None = None
    ) -> None:
        new_revision = copy.deepcopy(self)
        new_revision.revision += 1
        new_revision.log = ""
        if description is not None:
            new_revision.description = description
            new_revision.log += f"Rev {self.revision} description: {self.description} to Rev {new_revision.revision} description: {new_revision.description}\n"
        if nominal is not None:
            new_revision.nominal = nominal
            new_revision.log += f"Rev {self.revision} nominal: {self.nominal} to Rev {new_revision.revision} nominal: {new_revision.nominal}\n"
        if upper_limit is not None:
            new_revision.upper_limit = upper_limit
            new_revision.log += f"Rev {self.revision} upper_limit: {self.upper_limit} to Rev {new_revision.revision} upper_limit: {new_revision.upper_limit}\n"
        if lower_limit is not None:
            new_revision.lower_limit = lower_limit
            new_revision.log += f"Rev {self.revision} lower_limit: {self.lower_limit} to Rev {new_revision.revision} lower_limit: {new_revision.lower_limit}\n"
        if datums is not None:
            new_revision.datums = datums
            new_revision.log += f"Rev {self.revision} datums: {self.datums} to Rev {new_revision.revision} datums: {new_revision.datums}\n"
        if log_comment is not None:
            new_revision.log += log_comment
        new_revision.save_part_requirement()
        return new_revision

class VehicleRequirement:
    def __init__(
        self,
        id: str,
        revision: int,
        program: str,
        system: str,
        description: str,
        nominal: float,
        upper_tol_limit: float,
        lower_tol_limit: float,
        log_comment: str,
    ):
        self.id = id
        self.revision = revision
        self.program = program
        self.system = system
        self.description = description
        self.nominal = nominal
        self.upper_tol_limit = upper_tol_limit
        self.lower_tol_limit = lower_tol_limit
        self.log = log_comment
    def tolerance_range(self) -> float:
        return self.upper_tol_limit - self.lower_tol_limit
    def upper_boundary(self) -> float:
        return self.nominal + self.upper_tol_limit
    def lower_boundary(self) -> float:
        return self.nominal + self.lower_tol_limit
    def save_vehicle_requirement(self) -> None:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO vehicle_requirements (
                id,
                revision,
                program,
                system,
                description,
                nominal,
                upper_limit,
                lower_limit,
                log_comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.id,
                self.revision,
                self.program,
                self.system,
                self.description,
                self.nominal,
                self.upper_tol_limit,
                self.lower_tol_limit,
                self.log
            )
        )
        connection.commit()
    def update(
            self,
            description: str | None = None,
            nominal: float | None = None,
            upper_limit: float | None = None,
            lower_limit: float | None = None,
            log_comment: str | None = None
    ) -> None:
        new_revision = copy.deepcopy(self)
        new_revision.revision += 1
        new_revision.log = ""
        if description is not None:
            new_revision.description = description
            new_revision.log += f"Rev {self.revision} description: {self.description} to Rev {new_revision.revision} description: {new_revision.description}\n"
        if nominal is not None:
            new_revision.nominal = nominal
            new_revision.log += f"Rev {self.revision} nominal: {self.nominal} to Rev {new_revision.revision} nominal: {new_revision.nominal}\n"
        if upper_limit is not None:
            new_revision.upper_tol_limit = upper_limit
            new_revision.log += f"Rev {self.revision} upper_limit: {self.upper_tol_limit} to Rev {new_revision.revision} upper_limit: {new_revision.upper_tol_limit}\n"
        if lower_limit is not None:
            new_revision.lower_tol_limit = lower_limit
            new_revision.log += f"Rev {self.revision} lower_limit: {self.lower_tol_limit} to Rev {new_revision.revision} lower_limit: {new_revision.lower_tol_limit}\n"
        if log_comment is not None:
            new_revision.log += log_comment
        new_revision.save_vehicle_requirement()
        return new_revision

class StackContributor:
    def __init__(
        self,
        requirement_id: str,
        requirement_revision: int,
        requirement_description: str,
        requirement_half_range: float
    ):
        self.id = requirement_id
        self.revision = requirement_revision
        self.description = requirement_description
        self.half_range = requirement_half_range

class StackTarget:
    def __init__(
        self,
        requirement_id: str,
        requirement_revision: int,
        requirement_description: str,
        requirement_half_range: float,
    ):
        self.id = requirement_id
        self.revision = requirement_revision
        self.description = requirement_description
        self.half_range = requirement_half_range

class ToleranceStack:
    def __init__(
        self,
        id: str,
        revision: int,
        description: str,
        vehicle_requirement: VehicleRequirement
    ):
        self.id = id
        self.revision = revision
        self.description = description
        self.target = StackTarget(
            vehicle_requirement.id,
            vehicle_requirement.revision,
            vehicle_requirement.description,
            vehicle_requirement.tolerance_range()/2
        )
        self.life_cycle_status = "wip"
        self.contributors: list[StackContributor] = []
        self.target_changed = False
        self.validation_changed = False
        self.review_required = False
        self.review_remark = None
    def add_contributor(self, part_requirement: PartRequirement) -> None:
        contributor = StackContributor(
            part_requirement.id,
            part_requirement.revision,
            part_requirement.description,
            part_requirement.tolerance_range()/2
        )
        self.contributors.append(contributor)
    def confirm_object_stored_and_at_wip(self) -> None:
        record = get_revision_of_stack(self.id, self.revision)
        if record is None:
            raise LookupError(
                f"Record for stack {self.id} - rev {self.revision} was not found"
            )
        if record["life_cycle_status"] != "wip":
            raise ValueError(
                f"The record for {self.id} - rev {self.revision} is not stored as WIP"
            )
    def save_wip_changes(self):
        if self.life_cycle_status != "wip":
            raise ValueError(
                f"Stack {self.id} - rev {self.revision} is not WIP and cannot be changed."
            )
        self.confirm_object_stored_and_at_wip()
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE tolerance_stacks
                SET description = ?
                WHERE id = ? AND revision = ?
            """, (self.description, self.id, self.revision))
            cursor.execute("""
                DELETE FROM contributors
                WHERE stack_id = ? AND stack_revision = ?
            """, (self.id, self.revision))
            for contributor in self.contributors:
                cursor.execute("""
                    INSERT INTO contributors(
                        stack_id,
                        stack_revision,
                        requirement_id,
                        requirement_revision,
                        instance_label
                    ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        self.id,
                        self.revision,
                        contributor.id,
                        contributor.revision,
                        None
                    )
                )
    def wip_to_current(self) -> None:
        self.confirm_object_stored_and_at_wip()
        if not self.contributors:
            raise ValueError(
                f"Stack {self.id} - rev {self.revision} has no contributors so it can not be promoted to current."
            )
        self.save_wip_changes()
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE tolerance_stacks
                SET life_cycle_status = "current"
                WHERE id = ? AND revision = ?
            """, (self.id, self.revision))
        self.life_cycle_status = "current"
    def stack_result(self) -> float | str:
        if not self.contributors:
            return "Not calculated—no contributors"
        square_sum = 0
        for contributor in self.contributors:
            square_sum += contributor.half_range * contributor.half_range
        return math.sqrt(square_sum)
    def contributors_by_range(self) -> list[StackContributor]:
        return sorted(
            self.contributors,
            key=lambda contributor: contributor.half_range,
            reverse=True
        )
    def target_validation(self) -> bool:
        if not self.contributors:
                    return "Not calculated—no contributors"
        return self.stack_result() <= self.target.half_range
    def validation_status(self) -> str:
        if not self.contributors:
            return "Not calculated—no contributors"
        if self.target_validation():
            return "Target Met"
        return "Target exceeded"
    def target_usage(self) -> float | str:
        if not self.contributors:
            return "Not calculated—no contributors"
        return (self.stack_result() / self.target.half_range) * 100
    def find_current_requirement(
        self,
        contributor: StackContributor,
        current_requirements: list[PartRequirement]
    ):
        for requirement in current_requirements:
            if requirement.id == contributor.id:
                return requirement
        raise LookupError(
            f"Part requirement {contributor.id} was not found "
            f"in the supplied current requirements for stack {self.id}."
        )
    def inputs_are_current(
            self,
            current_requirements: list
        ) -> bool:
        inputs_current = True
        for contributor in self.contributors:
            current_requirement = self.find_current_requirement(contributor, current_requirements)
            if not contributor.revision == current_requirement.revision:
                inputs_current = False
        return inputs_current
    def update_status(
            self,
            current_requirements: list
        ) -> str:
        if self.inputs_are_current(current_requirements):
            return "this is still the current official stack"
        return "one or more inputs have changed, so an updated calculation is pending"
    def changed_requirements(
        self,
        current_requirements: list
    ) -> list:
        updated_requirements = []
        for contributor in self.contributors:
            current_requirement = self.find_current_requirement(contributor, current_requirements)
            if contributor.revision != current_requirement.revision:
                updated_requirements.append(current_requirement)
        return updated_requirements
    def update_contributors(
        self,
        requirement: PartRequirement,
    ) -> None:
        for contributor in self.contributors:
            if requirement.id == contributor.id:
                contributor.description = requirement.description
                contributor.revision = requirement.revision
                contributor.half_range = requirement.tolerance_range()/2
    def save_stack(self) -> None:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO tolerance_stacks(
                id,
                revision,
                description,
                target_requirement_id,
                target_requirement_revision,
                life_cycle_status,
                target_changed,
                validation_changed,
                review_required,
                review_remark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
                self.id,
                self.revision,
                self.description,
                self.target.id,
                self.target.revision,
                self.life_cycle_status,
                self.target_changed,
                self.validation_changed,
                self.review_required,
                self.review_remark
            )
        )
        for contributor in self.contributors:
            cursor.execute("""
                INSERT INTO contributors(
                    stack_id,
                    stack_revision,
                    requirement_id,
                    requirement_revision,
                    instance_label
                ) VALUES (?, ?, ?, ?, ?)
                """, (
                    self.id,
                    self.revision,
                    contributor.id,
                    contributor.revision,
                    None
                )
            )
        connection.commit()
    def recalculate(
        self,
        current_requirements: list
    ) -> "ToleranceStack":
        recalculated_stack = copy.deepcopy(self)
        latest_record = get_latest_tolerance_stack_revision(self.id)
        if latest_record is None:
            raise LookupError(
                f"No stored revisions found for tolerance stack {self.id}."
            )
        recalculated_stack.revision = latest_record["revision"] + 1
        recalculated_stack.life_cycle_status = "pending review"
        recalculated_stack.review_required = True
        for requirement in recalculated_stack.changed_requirements(current_requirements):
            requirement_data = load_part_requirement(requirement.id)
            recalculated_stack.update_contributors(requirement_data)
        return recalculated_stack
    def check_inputs(
        self,
        current_requirements: list
    ) -> "ToleranceStack | None":
        if self.inputs_are_current(current_requirements):
            return None
        return self.recalculate(current_requirements)
    def find_current_vehicle_requirement(self) -> sqlite3.Row:
        requirement = get_latest_vehicle_requirement(self.target.id)
        if requirement is None:
            raise LookupError(
                f"Vehicle requirement {self.target.id} was not found "
                f"in the database for stack {self.id}."
            )
        return requirement
    def target_is_current(
        self,
    ) -> bool:
        target_requirement = self.find_current_vehicle_requirement()["revision"]
        return target_requirement == self.target.revision
    def update_target(self) -> None:
        target_requirement_row = self.find_current_vehicle_requirement()
        self.target.description = target_requirement_row["description"]
        self.target.revision = target_requirement_row["revision"]
        self.target.half_range = (target_requirement_row["upper_limit"]-target_requirement_row["lower_limit"])/2
    def revalidate_target(self):
        old_validation_status = self.validation_status()
        self.update_target()
        self.target_changed = True
        new_validation_status = self.validation_status()
        if old_validation_status != new_validation_status:
            self.validation_changed = True
        else:
            self.validation_changed = False
    def update_stack(self) -> None:
        cursor = connection.cursor()
        cursor.execute(
            """
                UPDATE tolerance_stacks
                SET
                    target_requirement_revision = ?,
                    life_cycle_status = ?,
                    target_changed = ?,
                    review_required = ?,
                    review_remark = ?,
                    validation_changed = ?
                WHERE
                    id = ? AND revision = ?
            """, (
                self.target.revision,
                self.life_cycle_status,
                self.target_changed,
                self.review_required,
                self.review_remark,
                self.validation_changed,
                self.id,
                self.revision
            )
        )
        connection.commit()
    def check_target(self) -> str:
        if self.target_is_current():
            return "Target is current."
        return self.revalidate_target()
    def check_for_updates(
        self,
        current_requirements: list
    ) -> "ToleranceStack | None":
        updated_stack = self.check_inputs(current_requirements)
        if updated_stack is not None:
            updated_stack.check_target()
            updated_stack.save_stack()
            return updated_stack
        self.check_target()
        self.update_stack()
        return None
    def disregard(
        self,
        remark: str
    ) -> None:
        self.confirm_object_stored_and_pending_review()
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE tolerance_stacks
                SET
                    life_cycle_status = "disregarded",
                    review_remark = ?,
                    review_required = 0
                WHERE id = ? AND revision = ?
            """, (remark, self.id, self.revision))
        self.life_cycle_status = "disregarded"
        self.review_remark = remark
        self.review_required = False
    def supersede_current_stack(self) -> None:
        cursor = connection.cursor()
        cursor.execute(
            """
                UPDATE tolerance_stacks
                SET
                    life_cycle_status = "superseded"
                WHERE
                    id = ? AND life_cycle_status = "current"
            """, (self.id,)
        )
    def confirm_object_stored_and_pending_review(self) -> None:
        record = get_revision_of_stack(self.id, self.revision)
        if record is None:
            raise LookupError(
                f"Record for stack {self.id} - rev {self.revision} was not found"
            )
        if record["life_cycle_status"] != "pending review":
            raise ValueError(
                f"The record for {self.id} - rev {self.revision} is not stored as 'pending review'"
            )
    def accept(
        self,
        remark: str
    ) -> None:
        self.confirm_object_stored_and_pending_review()
        with connection:
            self.supersede_current_stack()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE tolerance_stacks
                SET
                    life_cycle_status = "current",
                    review_remark = ?,
                    review_required = 0
                WHERE id = ? AND revision = ?
            """, (remark, self.id, self.revision))
        self.life_cycle_status = "current"
        self.review_remark = remark
        self.review_required = False
    def acknowledge_target_change(self) -> None:
        self.target_changed = False
        self.validation_changed = False
        self.review_required = False
        self.update_stack()
    def needs_review(self) -> bool:
        return self.review_required

def load_part_requirement(requirement_id: str) -> PartRequirement:
    row = get_latest_part_requirement(requirement_id)
    if row is None:
        raise LookupError(
            f"Part requirement {requirement_id} was not found."
        )
    loaded_requirement = PartRequirement(
        id= row["id"],
        revision= row["revision"],
        part= row["part"],
        description= row["description"],
        category= RequirementCategory(row["category"]),
        nominal= row["nominal"],
        upper_limit= row["upper_limit"],
        lower_limit= row["lower_limit"],
        datums= [
            row["primary_datum"],
            row["secondary_datum"],
            row["tertiary_datum"],
        ],
        log_comment= row["log_comment"]
    )
    return loaded_requirement

def load_rev_of_part_requirement(requirement_id: str, revision: int) -> PartRequirement:
    row = get_rev_of_part_requirement(requirement_id, revision)
    if row is None:
        raise LookupError(
            f"Part requirement {requirement_id} rev {revision} was not found."
        )
    loaded_requirement = PartRequirement(
        id= row["id"],
        revision= row["revision"],
        part= row["part"],
        description= row["description"],
        category= RequirementCategory(row["category"]),
        nominal= row["nominal"],
        upper_limit= row["upper_limit"],
        lower_limit= row["lower_limit"],
        datums= [
            row["primary_datum"],
            row["secondary_datum"],
            row["tertiary_datum"]
        ],
        log_comment= row["log_comment"]
    )
    return loaded_requirement

def load_vehicle_requirement(requirement_id: str) -> VehicleRequirement:
    row = get_latest_vehicle_requirement(requirement_id)
    if row is None:
        raise LookupError(
            f"Vehicle requirement {requirement_id} was not found."
        )
    loaded_requirement = VehicleRequirement(
        id= row["id"],
        revision= row["revision"],
        program= row["program"],
        system= row["system"],
        description= row["description"],
        nominal= row["nominal"],
        upper_tol_limit= row["upper_limit"],
        lower_tol_limit= row["lower_limit"],
        log_comment= row["log_comment"]
    )
    return loaded_requirement

def load_rev_of_vehicle_requirement(requirement_id:str, revision: int):
    row = get_rev_of_vehicle_requirement(requirement_id, revision)
    if row is None:
        raise LookupError(
            f"Vehicle requirement {requirement_id} rev {revision} was not found."
        )
    loaded_requirement = VehicleRequirement(
        id= row["id"],
        revision= row["revision"],
        program= row["program"],
        system= row["system"],
        description= row["description"],
        nominal= row["nominal"],
        upper_tol_limit= row["upper_limit"],
        lower_tol_limit= row["lower_limit"],
        log_comment= row["log_comment"]
    )
    return loaded_requirement

def load_tolerance_stack(stack_id: str, status: Literal["current", "latest"] = "latest") -> ToleranceStack:
    if status == "current":
        row = get_current_tolerance_stack(stack_id)
    elif status == "latest":
        row = get_latest_tolerance_stack_revision(stack_id)
    else:
        raise ValueError(
            f"Unsupported stack status {status!r}. Use 'current' or 'latest'."
        )
    if row is None:
        raise LookupError(
            f"No {status} revision found for tolerance stack {stack_id}."
        )
    loaded_stack = ToleranceStack(
        id = row["id"],
        revision = row["revision"],
        description= row["description"],
        vehicle_requirement= load_rev_of_vehicle_requirement(row["target_requirement_id"], row["target_requirement_revision"])
    )
    contributor_rows = get_contributors_for_tolerance_stack(loaded_stack.id, loaded_stack.revision)
    if contributor_rows:
        for contributor in contributor_rows:
            requirement = load_rev_of_part_requirement(contributor["requirement_id"], contributor["requirement_revision"])
            loaded_stack.add_contributor(requirement)
    loaded_stack.target_changed = bool(row["target_changed"])
    loaded_stack.life_cycle_status = row["life_cycle_status"]
    loaded_stack.validation_changed = bool(row["validation_changed"])
    loaded_stack.review_required = bool(row["review_required"])
    loaded_stack.review_remark = row["review_remark"]
    return loaded_stack

def load_all_current_part_requirements() -> list[PartRequirement]:
    current_part_requirements = []
    part_requirement_rows = get_latest_part_requirements()

    for row in part_requirement_rows:
        requirement = PartRequirement(
            id= row["id"],
            revision= row["revision"],
            part= row["part"],
            description= row["description"],
            category= RequirementCategory(row["category"]),
            nominal= row["nominal"],
            upper_limit= row["upper_limit"],
            lower_limit= row["lower_limit"],
            datums= [
                row["primary_datum"],
                row["secondary_datum"],
                row["tertiary_datum"],
            ],
            log_comment= row["log_comment"],
        )
        current_part_requirements.append(requirement)

    return current_part_requirements

def load_all_current_vehicle_requirements() -> list[VehicleRequirement]:
    current_vehicle_requirements = []
    vehicle_requirement_rows = get_latest_vehicle_requirements()

    for row in vehicle_requirement_rows:
        requirement = VehicleRequirement(
            id= row["id"],
            revision= row["revision"],
            program= row["program"],
            system= row["system"],
            description= row["description"],
            nominal= row["nominal"],
            upper_tol_limit= row["upper_limit"],
            lower_tol_limit= row["lower_limit"],
            log_comment= row["log_comment"],
        )
        current_vehicle_requirements.append(requirement)

    return current_vehicle_requirements

if __name__ == "__main__":
    connection.close()