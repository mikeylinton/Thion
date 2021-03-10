import re;from graphviz import Digraph as Dot
inputfile=open('dev.in','r')

section=None
players={}
buildings={}
PreConditions=[]
MainFlow=[]
PostConditions=[]


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
		print(f"\nUnexpected error:",line,'\n')

for building in buildings:
	print(building)

for player in players:
	print(player)

print("------------------")
for string in PreConditions:
	action=string.pop(0)
	print(action)

	if action=="locked":
		building=string.pop(0)
		if re.search("\[.*\]",building):
			building,room=building.split('[');room=room.strip(']')
			print(room,"in",building)
			print(room)
			buildings[building][2][room][1]=True
		else:
			print(building)
			buildings[building][1]=True
		print(buildings[building])
		print("------------------")
	
	if action=="unlocked":
		building=string.pop(0)
		if re.search("\[.*\]",building):
			building,room=building.split('[');room=room.strip(']')
			buildings[building][2][room][1]=False
		else:
			buildings[building][1]=False
		print(buildings[building])
		print("------------------")

print("------------------")
unit=0
for string in MainFlow:
	action=string.pop(0)
	print(action)

	if action=="enter":
		player=string.pop(0)
		print(player)
		facility=string.pop(0)
		print(facility)
		#players[player][1]=building
		print(players[player])
		if facility in buildings:
			print()
		else:
			for building in buildings:
				if facility in buildings[building][2]:
					buildings[building][2][room][2]=building+'['+facility+']'+
					break
					
		print("------------------")

	elif action=="exit":
		player=string.pop(0)
		print(player)
		building=string.pop(0)
		print(building)
		print("------------------")

	elif action=="lock":
		player=string.pop(0)
		print(player)
		building=string.pop(0)
		print(building)
		print("------------------")

	elif action=="unlock":
		player=string.pop(0)
		print(player)
		building=string.pop(0)
		print(building)
		print("------------------")

	else:
		print("Action not found")
		print("------------------")
	unit+=1
print("Total units:",unit)