# QUBerium: An Environmentally Friendly Cryptocurrency for Queen's University Belfast

## Description
QUBerium is a peer-to-peer decentralised blockchain using a proof-of-stake consensus mechanism for storing and verifying student records. This project is designed to store records securely against internal and external attacks, with each record being verifiably correct and in a distributed manner, so that the network can continue under great strain.

This project is available from this repository, requiring an access request to the author.

## Requirements
This project should run on most systems. It has been benchmarked to run well on the following specification:
HP 250 G7 Laptop
CPU: Intel Core i3-7020U @2.3GHz Dual Core
RAM: 8GB DDR3
OS: Windows 10/Linux

A python installation is required along with the following package dependencies:
json
time
threading
hashlib
boto3==1.26.92
p2pnetwork==1.2
rsa==4.9

For more information on versioning see requirements.txt

## Installation
1. Clone the repository to your local machine
2. Using your command terminal of choice navigate to the cloned directory and to the /src directory containing 'main.py'
3. Use the following command to launch the program: 'main.py <ip> <port> <permission level> <id>'
    E.g. 'main.py localhost 5001 "admin" 40233186
4. To verify the installation has been correct, you should see the following upon startup:
![image.png](./image.png)

## Usage
ADDING A NEW RECORD
Prerequisite: Must be logged in as an administrator.
1.	From the menu select the ‘Create Record’ button.
2.	Enter the student’s information in the form provided.
    a.	If extra space is needed to enter more modules and grades, press the ‘+’ button.
3.	Once all records have been entered press ‘Submit’
4.	The fields should then go blank, and the command line should print ‘New record added’.
5.	To validate success, navigate back to the menu using ‘Return to Menu’.
6.	Select ‘Blockchain’
7.	Select the newest block.
8.	Verify that details of your transaction have been added.
    a.	Note, the record will be encrypted. To confirm the data has been entered correctly, search for the student’s records.
----------------------------------------------------------------------------------------------------------------------
SEARCHING FOR A STUDENT’S RECORD
Prerequisite: Must be logged in as an administrator.

1.	Select the ‘Search’ button.
2.	Enter the student’s ID in the box presented.
3.	Select ‘Submit’ when ready.
4.	The student’s records should now be displayed if they exist. Otherwise, a popup will be displayed informing the user of an error.

----------------------------------------------------------------------------------------------------------------------
VIEWING YOUR RECORD AS A STUDENT
Prerequisite: Must be logged in as a student.

1.	Select ‘My Records’ from the main menu.
2.	The student records should now be displayed.
    a.	If not, you may see a ‘Retrieving’ label. The software is waiting for the users records to be returned and this may take a moment.
    b.	If the records cannot be found, ‘Records not found – please contact and administrator’ should be displayed and the instructions followed.

----------------------------------------------------------------------------------------------------------------------
SENDING TOKENS TO OTHER NODES
1.	From the main menu select ‘Send Tokens’
2.	Enter the amount you want to send.
3.	Enter the ID of the person you want to send the tokens to.
4.	Select ‘Submit’ when ready.
5.	Upon success a ‘Success!’ popup will be displayed, otherwise one will see an error message popup.
6.	To verify success, navigate back to the main menu using ‘Return To Menu’.
7.	Select the ‘Balances’ button.
8.	The balance of each connected node will be displayed. Verify the correct amount has been deducted from one’s balance and been added to the recipient.
    a.	NB. The balance of one of the nodes may differ slightly, as if chosen to be validator and they produce a successful block to store the transaction they will be rewarded in tokens.
9.	Navigate back to the main menu and select ‘Blockchain’
10.	Select the latest block and confirm the transaction stored inside is correct.


## Authors and acknowledgment
Author: Cameron McGreevy
Acknowledgment to Ihsen Alouani for his help in creating and designing the project.

## License
MIT License

Copyright (c) 2023 Cameron McGreevy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

