import asyncio
import os
import websockets
import sys
import json

lastUser = " "
updateCount = 1
CLIENTS = set() #set of all clients
# create handler for each connection
def getHist():
	fileObj = open('messages.txt', "r") #opens the file in read mode
	words = fileObj.read().split(";") #puts the file into an array
	fileObj.close()
	length = len(words)
	hist = ""
	#hist = words[0]
	for x in range(0, length-1):
		if(x%2 != 0):
			hist = hist + words[x] + "<br>"
		else:
			hist = hist + words[x] + ": "
	return hist

async def broadcast(): #send hist to all connected clients
	await asyncio.gather(*[ws.send(getHist()) for ws in CLIENTS],return_exceptions=False,)
	print("Sending update to " + str(len(CLIENTS)) + " users")

async def handler(websocket, path):
	global lastUser
	global updateCount
	oldSocket = None
	data = await websocket.recv()
	dataJSON = json.loads(data)
	data = dataJSON["request"]
	name = dataJSON["username"]
	user = websocket.remote_address[0]
	if(data == "connection made"):
		print("connection made at: " + user + " by " + name)
	elif(data == "FETCH h"):
		print("update requested at: " + user + " by " + name)
	else:
		print("data recieved from: " + user + " by " + name)
		f = open('messages.txt','a')
		f.write(name + ";" + data + ";")
		f.close()
	hist = getHist()
	await websocket.send(hist)
	for ws in CLIENTS:
		if(ws.remote_address[0] == user):
			oldSocket = ws
	if oldSocket is not None:
		CLIENTS.remove(oldSocket)
	CLIENTS.add(websocket) #start client list gathering
	await broadcast()
	try:
		async for msg in websocket:
			pass
	except websockets.ConnectionClosedError:
		pass
	finally:
		CLIENTS.remove(websocket) #end client list gathering




start_server = websockets.serve(handler, "192.168.1.16", 4000)


#asyncio.get_event_loop().create_task(broadcast()) #run broadcast task
asyncio.get_event_loop().run_until_complete(start_server)
print("running")
asyncio.get_event_loop().run_forever()
