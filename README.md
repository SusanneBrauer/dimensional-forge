# Dimensional Forge - Dimensional Requirements and Tolerance Analysis
## About
A database application that connects part requirements with product requirements through tolerance stacks to provide information to all stakeholders in one solution.

Tolerance calculations(currently 1D stacks only), vehicle requirements and part requirements are currently stored separately. This can cause disconnects in the inputs, results and targets as well as confusion as to what is the latest calculation or assumption. With things being stored on separate documents getting hold of all details can be difficult.  
This tool ties all the information together and allows the user to identify changes in inputs and/or targets. It even recalculates and revaluates existing stacks based on updates. As these updates happen all revisions are preserved in the database.  
This ensures that calculations, targets and inputs can be made available for all stakeholders across the development process.  
Every stack can give information about its RSS-result, contributors and how much of the tolerance the predicted range is using of the target range.  
Input tolerance ranges can be centred as well as biased. Biased Tolerance values will for calculation purposes be treated as centered tolerance through their range while disregarding the centre offset tolerance.
## Features
- store tolerance stacks and connect it to product requirement
- add part requirements to tolerance stacks
- update and create a new revision stack when part requirements change
- tolerance stack have different life cycle states: `wip`, `current`, `pending review`, `superseded` and `disregarded`
- review workflow: `accept` and `disregard` pending stacks currently running through python methods *demo menu support planned*
- tolerance stack produce RSS calculation and compare the result to the target (percentage of target use provided as well)
- tolerances stacks and requirements preserve previous revisions
- the working assumption is not overwritten automatically they have to be promoted or disregarded (disregarded changes are preserved as such)
## Running
- run `python demo.py` from the project folder
- enter `y` to rebuild the sample data or hit `Enter` to retain the existing dataset
- **on the first run:** enter `y` to create the sample data
- select a tolerance stack by entering its ID or enter `q` to quit the selection

## Sample Data
The sample data set currently contains two scenarios:
- `SAMPLE_TS_001` is an updated tolerance stack that meets its target
- `SAMPLE_TS_002` is a tolerance stack with outdated contributors that exceeds its target

## Example
When a supplier or part owner update a part tolerance that was used in an existing stack the stack is able to recognise that the input tolerance has changed an creates a new revision of itself with updated contributors and checks how the new results evaluates against the target. This new revision will not over write the current one. An engineer needs to confirm that the change is representative of the current assumption and promoted to be the new working stack.  
The engineer loads the tolerance stack using the `load_tolerance_stack()` function and uses the `check_for_updates()` methods to check for updated inputs or targets and recalculate and/or revaluate the stack considering the updated requirements. And after reviewing any changes and promote or pass over the new revision with the methods `accept()` or `disregard()`.

## File Map
- `demo.py` - runs the user interactions
- `build_sample_db.py` - setup of the sample data
- `models.py` - holds objects and behaviors
- `database.py` - contains database setup and queries

## Tech Stack
- Python
- SQLite