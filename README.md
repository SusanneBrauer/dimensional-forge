# Dimensional Forge - Dimensional Requirements and Tolerance Analysis
## About
The project explores how structured data storage, relationships between records, and revision tracking can improve the reliability and accessibility of engineering information.

This is a database application that connects part requirements with product requirements through tolerance stacks to provide information to all stakeholders in one solution. A tolerance stack is a calculation used to predict how variations in individual components combine and affect the final product.

Tolerance calculations(currently 1D tolerance stacks only), vehicle requirements and part requirements are often stored separately in engineering workflows. This can cause disconnects in the inputs, results and targets as well as confusion as to what is the latest calculation or assumption. With things being stored on separate documents getting hold of all details can be difficult.  
This tool ties all the information together and allows the user to identify changes in inputs and/or targets. It even recalculates and re-evaluates existing stacks based on updates. As these updates happen all revisions are preserved in the database.  
This ensures that calculations, targets and inputs can be made available for all stakeholders across the development process.  
Every stack can give information about its RSS result, contributors and how much of the tolerance the predicted range is using of the target range.  
Input tolerance ranges can be centred as well as biased. Biased Tolerance values will for calculation purposes be treated as centered tolerance through their range while disregarding the centre offset tolerance.
## Development Status
Dimensional Forge is an ongoing personal learning project. The current version focuses on storing and linking engineering requirements, calculating tolerance stacks, managing revisions, and identifying changes that require engineering review.

Future development will explore additional calculation methods, improved user interactions, and further refinement of the database structure.

## Features
- store tolerance stacks and connect it to product requirement
- add part requirements to tolerance stacks
- update and create a new revision stack when part requirements change
- tolerance stack have different life cycle states: `wip`, `current`, `pending review`, `superseded` and `disregarded`
- review workflow through menu interaction
- tolerance stack produce RSS calculation and compare the result to the target (percentage of target use provided as well)
- tolerances stacks and requirements preserve previous revisions
- the working assumption is not overwritten automatically they have to be promoted or disregarded (disregarded changes are preserved as such)
## Running
- **Python needs to be installed** *(tested in Python 3.14)*
- run `python demo.py` from the project folder (When running in Windows: If `python` isn't recognised, try `py demo.py`)
- enter `y` to rebuild the sample data or hit `Enter` to retain the existing dataset
- **on the first run:** enter `y` to create the sample data
- in the main menu select: current tolerance stacks, current review items, part requirements and vehicle requirements. Enter the number for the relevant option or `q` to exit
- select tolerance stacks, part requirements and vehicle requirements by entering the respective IDs or enter `q` to return to the main menu
- selected requirements can be updated when entering `y`
- in the update menu choose the updates you want to make by entering the respective numbers and confirm the updates by entering `f` or cancel it by entering `q`
- opening the view of current review items checks for tolerance stacks requiring review and displays all pending tolerance stacks
- when viewing review items the user can choose a pending stack by entering its ID which will load the details for the review items
- the user can then either accept or disregard an update through menu interaction

## Sample Data
The sample data set currently contains two scenarios:
- `SAMPLE_TS_001` is an updated tolerance stack that meets its target
- `SAMPLE_TS_002` is a tolerance stack with outdated contributors that exceeds its target

## Example
When a supplier or part owner update a part tolerance that was used in an existing stack the stack is able to recognise that the input tolerance has changed and creates a new revision of itself with updated contributors and checks how the new results evaluates against the target. This new revision will not overwrite the current one. An engineer needs to confirm that the change is representative of the current assumption and promoted to be the new working stack.  
The engineer loads the tolerance stack using the `load_tolerance_stack()` function and uses the `check_for_updates()` methods to check for updated inputs or targets and recalculate and/or re-evaluates the stack considering the updated requirements. And after reviewing any changes and promote or pass over the new revision with the methods `accept()` or `disregard()`.

## Known Limitations / Future Improvements
- **Disregarded updates:** When a proposed tolerance stack revision is disregarded, subsequent update checks can rediscover the same underlying requirement changes and generate another revision.
- **Planned improvement:** Refine the update detection process to recognise previously reviewed and disregarded changes, while still identifying genuinely new updates that require engineering review.

## File Map
- `demo.py` - runs the user interactions
- `build_sample_db.py` - setup of the sample data
- `models.py` - holds objects and behaviors
- `database.py` - contains database setup and queries

## Tech Stack
- Python
- SQLite