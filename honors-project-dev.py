import re;from graphviz import Digraph as Dot
inputfile=open('dev.in','r')

section=None
players={}
buildings={}
PreConditions=[]
MainFlow=[]
PostConditions=[]
PLACEHOLDER=None

while True:
	line=inputfile.readline().strip()
	if not line:
		break

	if re.search("^\[.*\]$",line):
		item=line.strip('[').strip(']')
		sections=(
		"Environment",
		"Players",
		"PreConditions",
		"MainFlow",
		"PostConditions")
		if item in sections:
			section=item
		else:
			print("\nUnknown section type:",line,'\n',"Section types: [Environment] , [Players] , [Pre-conditions] , [Main-flow] , [Post-conditions]",'\n')
		line=inputfile.readline().strip()


	if re.search("^.*;$",line) and not re.search("^#",line):
		items=re.split(';+',line)
		items.remove('')
		for item in items:
			if section=="Environment":
				building,rooms=item.split('[')
				rooms=rooms.strip(']')
				rooms=re.split(',',rooms)
#				building=building.replace(' ', '_')
				buildings[building]=[0,False,{}]
				for room in rooms:
#					room=room.replace(' ', '_')
					buildings[building][2][room]=[0,False]

			elif section=="PreConditions" or section=="MainFlow" or section=="PostConditions":
				i=len(vars()[section])
				vars()[section].append([])
				action,elements=item.split('(')
				elements=elements.strip(')')
				elements=re.split(',',elements)
				vars()[section][i].append(action)
				for element in elements:
					vars()[section][i].append(element)

			elif section=="Players":
				if re.search('^.*\[.*\]$',item):
					head,tail=item.split('[')
					messages=tail.strip(']')
					player,authority=head.split('(')
					authority=authority.strip(')')
					messages=re.split(',',messages)
				else:
					player,authority=item.split('(')
					authority=authority.strip(')')
					messages=None
				players[player]=[authority,None,messages]

	elif not re.search("^#",line):
		print("\nUnexpected error:",line,'\n')

#for building in buildings:
#	print(building)

#for player in players:
#	print(player)

print("------------------")
for string in PreConditions:
	action=string.pop(0)

	if action=="locked":
		building=string.pop(0)
		if re.search("\[.*\]",building):
			building,room=building.split('[');room=room.strip(']')
			buildings[building][2][room][1]=True
		else:
			buildings[building][1]=True
		print(buildings[building]);print("------------------")
	
	if action=="unlocked":
		building=string.pop(0)
		if re.search("\[.*\]",building):
			building,room=building.split('[');room=room.strip(']')
			buildings[building][2][room][1]=False
		else:
			buildings[building][1]=False
		print(buildings[building]);print("------------------")

print("MainFlow");print("------------------")
unit=0
for string in MainFlow:
	print(string)
	action=string.pop(0)

	if action=="enter" or action=="exit" or action=="lock" or action=="unlock":
		#[player,facility]
		player=string.pop(0)
		facility=string.pop(0)
		empty=False
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			
			if action=="enter" and int(buildings[building][2][room][0])<1:
				buildings[building][2][room][0]=players[player][0]	#Set Authority of room
			
			elif action=="exit":
				players[player][1]=building	
				for p in players:
					if players[p][1]==facility:
						empty=False;break
				if empty:
					buildings[building][2][room][0]=0
			
			elif action=="lock":
				PLACEHOLDER
				if 
			
			elif action=="unlock":
				PLACEHOLDER
		else:
			
			if action=="enter" and int(buildings[facility][0])<1:
				buildings[facility][0]=players[player][0]
			
			elif action=="exit":
				players[player][1]=None
				for p in players:
					if players[p][1]==facility:
						empty=False;break
				if empty:
					buildings[facility][0]=0
			
			elif action=="lock":
				PLACEHOLDER
			
			elif action=="unlock":
				PLACEHOLDER

		if action=="enter":
			players[player][1]=facility
		print(building,':',buildings[building]);print(player,':',players[player]);print("------------------")
	
	else:
		print("Action not found");print("------------------")
	unit+=1
print("Total units:",unit)
'''		
	elif action=="enter":
		player=string.pop(0)
		facility=string.pop(0)
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			if int(buildings[building][2][room][0])<1:
				buildings[building][2][room][0]=players[player][0]
		else:
			if int(buildings[facility][0])<1:
				buildings[facility][0]=players[player][0]
		players[player][1]=facility
		print(buildings[building]);print(players[player]);print("------------------")

	elif action=="exit":
		player=string.pop(0)
		facility=string.pop(0)
		empty=True
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			players[player][1]=building	
			for p in players:
				if players[p][1]==facility:
					empty=False;break
			if empty:
				buildings[building][2][room][0]=0
		else:
			players[player][1]=None
			for p in players:
				if players[p][1]==facility:
					empty=False;break
			if empty:
				buildings[facility][0]=0
		print(buildings[building]);print(players[player]);print("------------------")
'''
#		if facility in buildings:
#			if int(buildings[facility][0])<1:
#				buildings[facility][0]=players[player][0]
#				print(buildings[facility])
#		else:
#			for building in buildings:
#				if facility in buildings[building][2]:
#					if int(buildings[building][2][facility][0])<1:
#						buildings[building][2][facility][0]=players[player][0]
#						print(buildings[building])
#					break