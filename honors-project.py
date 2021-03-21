import re;import argparse
inputfile=open('dev.in','r')

parser=argparse.ArgumentParser(description='Honors Project by Michael Linton.')
parser.add_argument('--verbose','-v',action=argparse.BooleanOptionalAction,help='Verbose')
args=parser.parse_args()

PLACEHOLDER=None;section=None
players={};buildings={}
PreConditions=[];MainFlow=[];PostConditions=[]

print("---------------")
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
				building,rooms=item.split('[');rooms=rooms.strip(']')
				rooms=re.split(',',rooms)
				buildings[building]=[0,False,{}]
				for room in rooms:
					buildings[building][2][room]=[0,False]

			elif section=="PreConditions" or section=="MainFlow" or section=="PostConditions":
				i=len(vars()[section])
				vars()[section].append([])
				action,elements=item.split('(');elements=elements.strip(')')
				elements=re.split(',',elements)
				vars()[section][i].append(action)
				for element in elements:
					vars()[section][i].append(element)

			elif section=="Players":
				if re.search('^.*\[.*\]$',item):
					head,tail=item.split('[');messages=tail.strip(']')
					player,authority=head.split('(');authority=authority.strip(')')
					messages=re.split(',',messages)
				else:
					player,authority=item.split('(');authority=authority.strip(')')
					messages=None
				players[player]=[authority,None,messages]

	elif not re.search("^#",line):
		print("\nUnexpected error:",line,'\n')
if args.verbose:
	print("buildings");print("---------------")
	for building in buildings:
		print(building,':',buildings[building])
	print("---------------")

if args.verbose:
	print("players");print("---------------")
	for player in players:
		print(player,':',players[player])
	print("---------------")

if args.verbose: print("PreConditions");print("---------------")
for string in PreConditions:
	state=string.pop(0)

	if state=="locked" or state=="unlocked":
		facility=string.pop(0)
		if state=="locked":
			locked=True
		else:
			locked=False
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			buildings[building][2][room][1]=locked
			if args.verbose: print(building,':',buildings[building])
		else:
			buildings[facility][1]=locked
			if args.verbose: print(building,':',buildings[facility])
		if args.verbose: print("---------------")
	
	if state=="location":
		player=string.pop(0)
		facility=string.pop(0)
		players[player][1]=facility
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			if int(buildings[building][2][room][0])==0:
				buildings[building][2][room][0]=players[player][0]
		else:
			if int(buildings[facility][0])==0:
				buildings[facility][0]=players[player][0]
		if args.verbose: print(player,':',players[player]);print("---------------")
		

if args.verbose: print("MainFlow");print("---------------")
unit=0
for string in MainFlow:
	if args.verbose: print(unit,string)
	action=string.pop(0)

	if action=="enter" or action=="exit" or action=="lock" or action=="unlock":
		#[player,facility]
		player=string.pop(0)
		facility=string.pop(0)
		empty=False
		if re.search("\[.*\]",facility):
			building,room=facility.split('[');room=room.strip(']')
			
			if action=="enter" and int(buildings[building][2][room][0])==0:
				buildings[building][2][room][0]=players[player][0]	#Set Authority of room
			
			elif action=="exit":
				players[player][1]=building	
				for p in players:
					if players[p][1]==facility:
						empty=False;break
				if empty:
					buildings[building][2][room][0]=0
			
			elif (action=="lock" or action=="unlock") and int(buildings[building][2][room][0])<=int(players[player][0]):
				if action=="lock":
					buildings[building][2][room][1]=True
				else:
					buildings[building][2][room][1]=False
				 
		else:
			
			if action=="enter" and int(buildings[facility][0])==0:
				buildings[facility][0]=players[player][0]
			
			elif action=="exit":
				players[player][1]=None
				for p in players:
					if players[p][1]==facility:
						empty=False;break
				if empty:
					buildings[facility][0]=0
			
			elif (action=="lock" or action=="unlock") and int(buildings[facility][0])<=int(players[player][0]):
				if action=="lock":
					buildings[facility][1]=True
				else:
					buildings[facility][1]=False
				
		if action=="enter":
			players[player][1]=facility
		if args.verbose: print(building,':',buildings[building]);print(player,':',players[player]);print("---------------")
	
	else:
		print("Action not found");print("---------------")

	if unit<10: print("Time",unit,"========")
	elif unit<100: print("Time",unit,"=======")
	else: print("Time",unit,"=======")
	for player in players:
		facility=players[player][1]
		if facility is not None:
			if re.search("\[.*\]",facility):
				building,room=facility.split('[');room=room.strip(']')
				print(player,'in',room,'in',building)
			else:
				print(player,'in',facility)
	print("===============")
	unit+=1
print("Total units:",unit);print("---------------")