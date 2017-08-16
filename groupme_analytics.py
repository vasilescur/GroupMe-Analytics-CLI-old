import requests

access_token = 'Yy7L2qS2AF85HNNvMYvRERsbjOX8FkEHaIa9tfFi'
f = open('out.txt', 'w')

class Message:
	def __init__(self, name, text, likers):
		self.name = name
		self.text = text
		self.likers = likers
		
	def __str__(self):
		return 'Message: ' + self.name + ' said "' + self.text + '", liked by ' + str(self.likers)
	
class User:
	def __init__(self, user_id, init_nickname):
		self.user_id = user_id
		self.nicknames = []
		self.nicknames.append(init_nickname)
		self.messages = []
		
		self.mediaCount = 0
		
	def __str__(self):
		return 'User: ' + self.user_id + ' : ' + str(self.nicknames)
		

def menu():
	global access_token

	if len(access_token) == 0:
		access_token = str(input('Access token:'))
	
	print('Most recent groups:')
	groups_data = out_groups()
	
	try:
		group_number = int(input('Group to analyze:'))
		group_id = get_group_id(groups_data, group_number)
		
		# Display info to the user before the analysis begins
		group_name = get_group_name(groups_data, group_id)
		
		# Number of messages to get
		number_of_messages = int(input('Number of messages to analyze (use 0 for all): '))
		if number_of_messages == 0:
			number_of_messages = get_number_of_messages_in_group(groups_data, group_id)
			
		out(('Analyzing ' + str(number_of_messages) + ' messages from ' + group_name))
		
		# Put all the members currently in the group into a dictionary, and make a user-name lookup table
		members_of_group_data = get_group_members(groups_data, group_id)
		users = {}
		user_names = {}
		
		for user in members_of_group_data:
			user_id = user['user_id']
			init_nickname = user['nickname']
			users[user_id] = User(user_id, init_nickname)
			user_names[init_nickname] = user_id
		
		for user in users.values():
			out(user)
		
		
		# Analyze entire conversation
		
		response = requests.get('https://api.groupme.com/v3/groups/' + group_id + '/messages?token=' + access_token)
		data = response.json()
		iterations = 0
		message_id = 0
		done = False
		while not done:
			for i in range(20):
				try:
					iterations += 1
					
					if iterations > number_of_messages:
						out('Reached message ' + str(iterations) + ', stopping.')
						raise IndexError
		
					message = data['response']['messages'][i]
					
					user_id = message['user_id']
					name = message['name']  # Sender
					text = message['text']      # re.sub(r'\W+', ' ', str(message['text']))
					likers = message['favorited_by']
					
					if text is None:
						users[user_id].mediaCount += 1
						continue
					
					msg = Message(name, text, likers)

					try:
						users[user_id].messages.append(msg)
					except KeyError:
						out('Error: user not found (' + user_id + ')')
						continue
					
				except IndexError:
					out('Finished!', end = '\n\n')
					done = True
					break
			
			if done: break
			
			if i == 19:
				message_id = data['response']['messages'][i]['id']
				remaining = round(((iterations / number_of_messages) * 100), 2)
				print(str(remaining) + '% done')
			
			payload = {'before_id': message_id}
			response = requests.get('https://api.groupme.com/v3/groups/' + group_id + '/messages?token=' + access_token, params = payload)
			data = response.json()
			
		print('Done processing.\n')
		
		# Calculate and out user analytics
		
		out('\n----- User Analytics -----\n')
		
		# Calculate mentions
		mentions = {}
		for user in users.values():
			mentions[user.user_id] = 0
			
			# Calculate how many times user has been mentioned
			for _u in users.values():           # \ For all messages
				for msg in _u.messages[1:]:     # /
					for nick in user.nicknames:     # For top-level-user's nicknames
						if ('@' + nick) in msg.text:
							mentions[user.user_id] += 1
					
		
		
		for user in users.values():
			# Name(s)
			out(str(user.nicknames[0]) + ' (user_id: ' + user.user_id + ')')
			out('Past nicknames:\t\t', end = '')
			if len(user.nicknames) > 1:
				out(user.nicknames[1:])
			else: out('None')
			
			# Messages
			out('Messages sent:\t\t' + str(len(user.messages)))
			
			out()
			# Likes
			
			likes_received = 0
			for msg in user.messages:
				likes_received += len(msg.likers)
			out('Likes received:\t\t' + str(likes_received))
			
			out('Avg. likes/msg:\t\t' + str(round(likes_received / len(user.messages), 2)))
			
			# Likes FROM each person
			likes_from = {}
			for _user in users.values():
				likes_from[_user.user_id] = 0
				
			for _user in users.values():
				for _msg in user.messages:
					for liker in _msg.likers:
						likes_from[liker] += 1
			
			out('\nLikes from: ')
			for _user in users.values():
				out(_user.nicknames[0] + ':\t' + str(likes_from[_user.user_id]))
			
			
			# Mentions
			out()
			
			out('Mentions:\t\t' + str(mentions[user.user_id]))
			
			out('---', end = '\n\n')
		
		# "Graphs"
		
		out('\n---- Graphs ----\n')
		
		# Num messages sent
		out('Total messages sent: ')
		for user in users.values():
			out_graph(user.nicknames[0], calc_percentage(len(user.messages), number_of_messages, 30))
		out('---', end = '\n\n')
		
		# Num likes
		out('Total likes received: ')
		for user in users.values():
			likes_received = 0
			for msg in user.messages:
				likes_received += len(msg.likers)
			out_graph(user.nicknames[0], calc_percentage(likes_received, number_of_messages, 90))
		out('---', end = '\n\n')
		
		
		
	except ValueError:
		out('Not a number')


def calc_percentage(value, total, max):
	return int(round(max * (value / total), 0))
	

def out_graph(header, value):
	out("{: >30} {: <30}".format(header, '|' * value))


def out_groups():
	response = requests.get('https://api.groupme.com/v3/groups?token=' + access_token)
	data = response.json()

	if len(data['response']) == 0:
		print('You are not part of any groups.')
		return
	for i in range(len(data['response'])):
		group = data['response'][i]['name']
		print((str(i)+'\''+group+'\''))
	return data


def get_group_id(groups_data, group_number):
	group_id = groups_data['response'][group_number]['id']
	return group_id


def get_group_name(groups_data, group_id):
	i = 0
	while True:
		if group_id == groups_data['response'][i]['group_id']:
			return groups_data['response'][i]['name']
		i += 1


def get_number_of_messages_in_group(groups_data, group_id):
	i = 0
	while True:
		if group_id == groups_data['response'][i]['group_id']:
			return groups_data['response'][i]['messages']['count']
		i += 1


def get_group_members(groups_data, group_id):
	i = 0
	while True:
		if group_id == groups_data['response'][i]['group_id']:
			return groups_data['response'][i]['members']
		i += 1

	
def out(line = '', end = '\n'):
	print(str(line), end = end)
	f.write(str(line) + end)
	

# This method call is here so the program starts right when you run it.
menu()
