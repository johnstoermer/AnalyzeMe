# AnalyzeMe
AnalyzeMe is a data analysis tool for GroupMe group messages. Currently, it allows you to get user messages as a DataFrame from pandas or export them to CSV files.

## Usage:
Import AnalyzeMe with:
```python
from AnalyzeMe import AnalyzeMe as am
```
To start, give AnalyzeMe your GroupMe API token:
```python
my_group = am('YOUR_TOKEN')
```
Next, find the group message id you intend to look at with printGroupIDs():
```python
my_group.printGroupIDs()
```
Output (group name: group id):
```
Madden 2007: 12345678
Pokemon Go: 12345678
Survived The First Semester: 12345678
Top Secret: 12345678
```
To start looking at a specific group use the function getGroup():
```python
my_group.loadGroup('GROUP_ID')
```
Once you have loaded a group, you can check the user ids of members in the group with printUserIDs():
```python
my_group.printUserIDs()
```
Output (user name: user id):
```
Clay Jensen: 12345678
Upgraded Mac: 12345678
Coffee: 12345678
Sam: 12345678
Kyle From Tenacious D: 12345678
```
With a user id, you can get a DataFrame of the user by calling getDF():
```python
user_df = my_group.getDF('USER_ID')
```
Alternatively, you can export all users and their messages to files using toCSV():
```python
my_group.toCSV()
```
