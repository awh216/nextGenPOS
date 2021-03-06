import uuid
import sqlite3 as sql
import sys
import getpass

import Employee
import Transaction
import Store
import Item
import Payment
import RentalTransaction

# Class POS serves as a public singleton accessor for __POS which is private
class POS:
	instance = None

	def __init__(self):
		if not POS.instance:
			POS.instance = POS.__POS()            
		
	class __POS:
		
		# Constructor
		def __init__(self):
			self.__PID = str(uuid.uuid4().int)[:16]
			self.__currEmployee = None
			self.__store = self.loadStoreInfo()
			#print self.__store.getName()
			self.__num = 1 #need for the receipt, I guess it can incrememnt or something
			self.currentTransaction = None
			
		def getId(self):
			return self.__PID
			
		def getCurrEmployee(self):
			return self.__currEmployee
		
		def getNum(self):
			return self.__num
			
		def getStore(self):
			return self.__store

		def login(self,u,p):
			if u != "":
				print "Dev. Login: ID:  0032, Password: Muffins"
				print "          : ID: 94210, Password: Cupcake"
				
				if (self.__currEmployee):
					print "Cannot login with a user already logged in"
					wasLoggedOut = self.logOut()
					if (wasLoggedOut == False):
						return False
				
				couldLogin = False
				
				while (not couldLogin):
					
					employee = self.__queryDBForLogin (u, p)
					
					if (employee):
						print "\n Login successful"
						self.__currEmployee = employee
						if self.currentTransaction != None:
							self.currentTransaction.setCashier(self.__currEmployee)
						return True
						
					else:
						print "\nCould not find employee with that information"
						return False
			else:
				return None
		
		def main(self):
			while (True):
				if (self.getCurrEmployee()):
					
					cmd = raw_input("\n> ").lower()
					
					permissions = self.getCurrEmployee().getEmpType()
					
					commands =  {"log out":            [self.login,             [], ["Cashier", "Manager", "Admin"]],
								 "store info":         [self.storeInfo,         [], ["Manager", "Admin"]],
								 "transaction log":    [self.viewTransLog,      [], ["Manager", "Admin"]],
								 "create transaction": [self.createTransaction, [], ["Cashier", "Manager", "Admin"]],
								 "help":               [self.viewValidCommands, [], ["Cashier", "Manager", "Admin"]]
								}
					
					if (not cmd or cmd.isspace()):
						pass
					
					elif (cmd in commands):
						if (permissions in commands[cmd][2]):
							commands[cmd][0](*commands[cmd][1])
							
						else:
							permissionStr = ""
							for pS in commands[cmd][2]:
								if permissionStr == "":
									permissionStr += pS
								else:
									permissionStr += " or " + pS
							
							print ("Permission denied.  User must be a " + permissionStr)
					
				else:
					self.login()
			
			
		
							
		def __queryDBForLogin(self, inputId, inputPassword):
			
			try:
				
				connection = sql.connect('DB.db')
		
				with connection:
			
					cursor = connection.cursor()    
					
					# Todo: REMOVE
					if (inputId == ""):
						return Employee.Employee("Sarah Kerigan", 0032, "Cashier")
					
					
					cursor.execute('SELECT e_password FROM Employee WHERE e_id = ?', (inputId,))
					password = cursor.fetchone()[0]
				  
				if (password == inputPassword):
					
					cursor.execute('SELECT name FROM Employee WHERE e_id = ?', (inputId,))
					name = cursor.fetchone()[0]
					
					cursor.execute('SELECT type FROM Employee WHERE e_id = ?', (inputId,))
					empType = cursor.fetchone()[0]
					
					employee = Employee.Employee (name, inputId, empType)
					return employee
					
				else:
					return None
			except:
				return None
				
		def queryDBForItem(self, itemID):
			
			connection = sql.connect('DB.db')
	
			with connection:
		
				cursor = connection.cursor()    
				
				cursor.execute('SELECT * FROM Item WHERE I_ID = ?', (itemID,))
				item = cursor.fetchone()
				
				if item:
					return Item.Item (item[0], item[1], item[2], item[3])
				else:
					return None
				
		def loadStoreInfo(self):
			try:
				f = open("storeinfo.txt",'r').readlines()
				for i in range(len(f)):
					f[i] = f[i].rstrip('\r\n')
				tempStore = Store.Store(f[0],f[1],f[2],float(f[3])/100.00) #file is set up so the first line is name, second is location, third is phone number, fourth is tax
				return tempStore
				
			except:
				print "Error - Store info file may not exist"
				return None
			
		def logOut(self):
			
			#inp0 = self.__getInput ("Are you sure you want to log out %s ? <y or n> " % (self.__currEmployee.getName()), ["y", "n"])
				
			#if (inp0 == "y"):
			if self.currentTransaction != None:
				self.currentTransaction.setCashier(None)
			name = self.__currEmployee.getName()
			self.__currEmployee = None
			print "\nEmployee %s has been logged off." % (name)
			return True
						
			#elif (inp0 == "n"):
			#	print "\nEmployee %s will remain logged on." % (self.__currEmployee.getName())
			#	return False
			#	
			#else:
			#	print "Error: input request failed. Retry command"
			#	return False

		def createRentalTransaction(self):
			if self.__currEmployee != None:
				print self.__currEmployee.getName()
			self.currentTransaction = RentalTransaction.RentalTransaction(self.__store,self.__currEmployee)
			
		def createTransaction(self):
			if self.__currEmployee != None:
				print self.__currEmployee.getName()
			self.currentTransaction = Transaction.Transaction(self.__store,self.__currEmployee)
			
			#moreItems = True
#			running = True
#			transactionInfo = "Enter an item ID  -  Add item to transaction\ndone              -  Finish adding items\ncancel            -  cancel the current transaction\nremove            -  remove an item from the transaction\nitems             -  Show the items in the current transaction\nmanual            -  manually add an item to the transaction\nHelp              -  displays commands"
#			print transactionInfo
#			while moreItems:
#				command = raw_input(" > ")
#				if command.lower() == "done":
#					moreItems = False
#				elif command.lower() == "help":
#					print transactionInfo
#				elif command.lower() == "cancel":
#					moreItems = False
#					running = False
#				elif command.lower() == "manual":
#					incomplete = True
#					while incomplete:
#						try:
#							name = raw_input("Enter item name > ")
#							price = float(raw_input("Enter item price > $"))
#							sale = float(raw_input("Enter % sale > "))/100.00
#						except:
#							print "Error, try again"
#						print "Will add a "+name+" for "+str(price)+" with sale of "+str(sale)+"%"
#						incomplete = not (raw_input("Is this correct? > ").lower() in ['y','yes'])
#					self.addItemToTransaction(Item.Item(-1,name,price,sale))
#				
#				elif command.lower() == "remove":
#					response = None
#					ID = ""
#					while response == None and ID != "stop":
#						ID = raw_input("Enter the id of the item to remove or 'stop' to stop: ")
#						response = self.currentTransaction.getItem(ID)
#					if response != "stop":
#						print "removing item "+response.getName()
#						self.currentTransaction.removeItem(response)
#				elif command.lower() == "items":
#					# print "display items"
#					items = self.currentTransaction.getItems()
#					for item in items:
#						rentalString = " (Rental)"
#						if not item.isRental:
#							rentalString = ""
#						if item.getSaleValue() == 0:
#							#print(item.getName()+" $"+str(item.getPrice())+"  ID: "+item.getID()+rentalString)
#							print(item.getName()+" $"+str("{0:.2f}".format(item.getSalePrice()))+" ("+str(item.getSaleValue())+"% sale)"+"  ID: "+str(item.getID())+rentalString)#

#						else:
#							print(item.getName()+" $"+str("{0:.2f}".format(item.getSalePrice()))+" ("+str(item.getSaleValue())+"% sale)"+"  ID: "+str(item.getID())+rentalString)
#				else:
#					isRental = False
#					if command.lower().endswith("r"): #If its a rental
#						isRental = True
#						command=command[:-1]
#						print command
#					item = self.__queryDBForItem(command)
#					if item:
#						if isRental: #If its a rental
#							item.makeRental()
#							self.addItemToTransaction(item) #Add rental discount
#							print "Item "+item.getName()+" added for "+str(item.getPrice())+" at a sale of "+str(item.getSaleValue())+" as a rental"
#						else: 
#							self.addItemToTransaction(item)
#							print "Item "+item.getName()+" added for "+str(item.getPrice())+" at a sale of "+str(item.getSaleValue())
#						print "Current total is $"+str("{0:.2f}".format(self.getTransactionTotal()))
#					else:
#						print "Item does not exist in the database"
#			if running:
#				print "\n\nThe total is $"+str("{0:.2f}".format((1+self.getTax())*self.getTransactionTotal()))
#				paymentMethod = "none"
#				while paymentMethod.lower() not in ["cash","credit"]:
#					paymentMethod = raw_input("Cash or credit? > ")
#				if paymentMethod == "cash":
#					self.setPayment(Payment.Payment("cash"))
#					print "exchange money\nReceipt:"
#					print self.getTransactionReceipt()
#				else:
#					#cardNum = raw_input("Enter Card Number > ")
#					self.setPayment(Payment.Payment("credit"))
#					print "exchange money\nReceipt:"
#					print self.getTransactionReceipt()
		
		def addItemToTransaction (self, item):
			self.currentTransaction.addItem(item)
		
		#def addItemToTransaction (self, id):

		#    item = self.__queryDBForItem(id)

		#    if item:
		#        self.currentTransaction.addItemToTransaction(item)
		#        return True
		#    else:
		#        return False

		#def getAllItemsInTransaction (self):
		#    return self.currentTransaction.getItems()
		
		#def removeItemFromTransaction (self, item):
		#   return self.currentTransaction.removeItem()
		
		#def login (self, inputId, inputPassword):
		#    if (self.__currEmployee):
		#        print "Cannot login with a user already logged in"
		#        wasLoggedOut = self.logOut()
		#        if (wasLoggedOut == False):
		#            return False
		#
		#   employee = self.__queryDBForLogin (inputId, inputPassword)
		#    
		#    if (employee):
		#        self.__currEmployee = employee
		#        return True
		#    else:
		#        return False
		
		
		def getTransactionTotal(self):
			return self.currentTransaction.getCurrentTotal()

		def getTransactionItems(self):
			return self.currentTransaction.getItems()
		
		def getTransactionReceipt(self):
			return self.currentTransaction.getReceipt()
		
		def setPayment(self,payment):
			self.currentTransaction.setPayment(payment)

		def getCurrentTransaction(self):
			return self.currentTransaction
		
		def getTax(self):
			return self.__store.getTax()
		
				
		def storeInfo(self):
	
			inp0 = self.__getInput("Would you like to change the store info? (y/n): ", ["y","n"]).lower()
				
			if inp0 == "y":
				self.__initStore()
				
			#Print store info
			print("\nName: " + self.getStore().getName())
			print("Location: " + self.getStore().getLocation())
			print("Phone: " + self.getStore().getPhone())
					
			
		def __initStore(self):
			
			if not self.__store:
				
				print "A store already exists in the system.  This command will overwrite this data."
				
				inp0 = self.__getInput ("Ok to overwrite? <y or n> ", ["y", "n"])
				
				if (inp0 == "y"):
					print "\nThe store will be overwritten"
				elif (inp0 == "n"):
					print "\nThe store will not be overwritten"
					return False
				else:
					print "Error: input request failed. Retry command"
					return False
				
			print "Creating new store information"
			processDone = False
			
			while (not processDone):
				
				inputName     = raw_input("\nStore Name: ")
				inputLocation = raw_input  ("  Location: ")
				inputPhoneNo  = raw_input  (" Phone No.: ")
				
				tax = 0.06 # TODO: Fetch tax from database
				
				newStore = Store.Store (inputName, inputLocation, inputPhoneNo, tax)
				  
				inp1 = self.__getInput ("Ok to initialize store with this information? <y or n> ", ["y", "n"])
				  
				if (inp1 == "y"):
					print "\nThe store has been created"
					self.__store = newStore
					processDone = True
	
				elif (inp1 == "n"):
					print "\nThe store was not created."
					inp2 = self.__getInput ("Would you like to re-enter the information? <y or n> ", ["y", "n"])
					
					if (inp2 == "y"):
						pass
					
					elif (inp2 == "n"):
						processDone = True
						
					else:
						print "Error: input request failed. Retry command"
						return False
					
				else:
					print "Error: input request failed. Retry command"
					return False
			
			return True
		   
		def viewTransLog(self):
			
			print "viewTransLog"
			
			
			return True
			
		def viewValidCommands (self):
			
			print "\nValid Commands: "
			
			currEmp = self.__currEmployee
			
			if (currEmp == None):
				return False
				
			permissions = self.__currEmployee.getEmpType()
			
			if (permissions == "Manager" or permissions == "Admin"):
				print "    Login              - Log in as a different user" 
				print "    Log Out            - Log out current user"
				print "    Store Info         - Change Store Info"
				print "    Create Transaction - Start new transaction"
				# print "    Transaction Log    - View Transaction Log"
				print "    Help               - View Valid commands"
			else:
				print "    Login              - Log in as a different user" 
				print "    Log Out            - Log out current user"
				# print "    Store Info         - Change Store Info"
				print "    Create Transaction - Start new transaction"
				# print "    Transaction Log    - View Transaction Log"
				print "    Help              - View Valid commands"
				
			return True
		
		def __getInput (self, inputRequest, validInputs):
			
			validInput = False
			while (not validInput):
		
				userInput = raw_input(inputRequest)
				if userInput in validInputs:
					return userInput
					
				else:
					print ("Command unrecognized.")
			
if __name__ == '__main__':
	System = POS().instance
	System.main()