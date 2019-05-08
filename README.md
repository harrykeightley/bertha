# bertha
Harry's Clunky 2002 Marking tool.

- Installation
  - Navigate to the directory where beautiful Bertha lives.
  - ``` pip3 install -r requirements.txt ```
  - Download the latest marking ```criteria.json``` and put it in the same directory as ```bertha.py```
  - Change the contents of ```editor_commands.py``` to reflect the IDE you use (vscode by default)
- Command Line Usage
  - Basic usage is: ``` python3 bertha.py {root_student_dir} ```
  - State is saved by default in a file called state.pickle in the same directory as bertha. If you want to be explicit about where you store it, use the ```-s``` or ```--save``` followed by the location of the file you want to specify as the save.

## How does it actually work?

When you open it up for the first time the student frame should look like this:

![Student frame](https://i.imgur.com/adGJqK5.png)
- **View** : Pulls up the code for the current student.
- **Save** : Add student to the set of saved students and update the ```.style``` file to reflect your marks.
- **Next** : takes you to the next unsaved student.
- **Skip** : This is for if you've already done some marking, it adds the student to the saved set without modifying their style file.

### For marking specific criteria

![Criteria Frame](https://i.imgur.com/nw57nN9.png)
- The red ```1``` here shows that one deduction will be forgiven for this criteria.
- Deductions are made with the minus button
- You can reset marks on a specific criteria with the ```^``` button

### Good luck!
