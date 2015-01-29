#!/usr/bin/python3
"""
Solves an arbitrary version of that one problem from Die Hard 3 with the water jugs.
Given some number of jugs with some capacity each and an infinite water supply,
measure a specific amount of water using just the jugs that you have. You can only
fill a jug to full, empty a jug, or fill a jug with another jug. You can't measure
exactly how much a jug has, nor can you partially empty a jug.
"""

import copy

class GoalFound(Exception):
	pass

class Jug(object):
	"""
	A container with some capacity. It can be filled to full, emptied, or its contents
	can be transfered into another Jug.
	"""
	def __init__(self, capacity):
		self.capacity = capacity
		self.amount = 0
	
	def fill_to_full(self):
		self.amount = self.capacity
		
	def empty(self):
		self.amount = 0
		
	def transfer(self, jug):
		remainder = jug._fill(self.amount)
		self.amount = remainder
		
	def _fill(self, amount):
		self.amount += amount
		if self.amount > self.capacity:
			remainder = self.amount - self.capacity
			self.amount -= remainder
			return remainder
		else:
			return 0
		
	def __repr__(self):
		#return "Jug at %s: %i/%i" % (hex(id(self)), self.amount, self.capacity)
		return "Jug: %i/%i" % (self.amount, self.capacity)

class JugsState(object):
	"""
	This keeps track of all the states that the jugs have been in to prevent looping.
	Takes a list of jugs. Should only be used by JugsGraph.
	"""
	def __init__(self, jugs):
		self.jugs = [copy.copy(j) for j in jugs]
		self.next_states = []
		self.parent = None
		self.goal_flag = False
		
	def add_state(self, jugs_state):
		self.next_states.append(jugs_state)
		jugs_state.parent = self
		
	def is_same(self, state):
		# depends on the jugs always being in the same order
		for i, j in enumerate(self.jugs):
			if j.capacity == state.jugs[i].capacity and j.amount != state.jugs[i].amount:
				return False
			
		return True
	
	def has_fill_amount(self, amount):
		# check each jug to see if it has a specific amount filled
		# mainly used to check if it met the goal
		for j in self.jugs:
			if j.amount == amount:
				return True
			
		return False
		
class JugsGraph(object):
	"""
	Uses dynamic programming to solve the jugs problem.
	Takes a list of Jugs and a goal, and it will build the graph that solves the problem.
	"""
	def __init__(self, jugs, goal):
		self.start = JugsState(jugs)
		self.goal = goal
		self.graphed = False # this is just for printing purposes
		
	def state_exists(self, state):
		"""
		Recursively goes through entire graph to find if a jugs state exists.
		A jugs state is the amount filled for each jug. If two states have identical jug
		fill amounts, then it's considered to be the same.
		"""
		def _helper(self_state):
			these_states = [state.is_same(s) for s in self_state.next_states]
			child_states = [_helper(s) for s in self_state.next_states]
			
			exists = False
			for ts in these_states:
				exists = exists or ts
			for cs in child_states:
				exists = exists or cs
			
			return exists
		
		this_state = state.is_same(self.start)
		child_states = _helper(self.start)
		return this_state or child_states
	
	def graph_it(self):
		"""
		Recursively fills in the graph using dynamic programming. Each subproblem is solved only once.
		I check the graph every time to make sure I don't repeat a state that I've been in before.
		(Might not be the most optimal way to do this)
		"""
		def _helper(current_state):
			try:
				# go through each possible jug filling and emptying combinations
				# and check to make sure this doesn't create a duplicate state
				# after each item
				for i,j in enumerate(current_state.jugs):
					# try filling this jug
					fill_state = JugsState(current_state.jugs)
					fill_state.jugs[i].fill_to_full()
					# check states for duplicates, add to graph if there aren't any
					if not self.state_exists(fill_state):
						current_state.add_state(fill_state)
					# check for goal condition, stop computing if found
					if fill_state.has_fill_amount(self.goal):
						fill_state.goal_flag = True
						raise GoalFound()
						
					# try emptying this jug, then check states
					empty_state = JugsState(current_state.jugs)
					empty_state.jugs[i].empty()
					# check states for duplicates, add to graph if there aren't any
					if not self.state_exists(empty_state):
						current_state.add_state(empty_state)
					# check for goal condition, stop computing if found
					if empty_state.has_fill_amount(self.goal):
						empty_state.goal_flag = True
						raise GoalFound()
						
					# try filling this jug into each of the other jugs
					for k in range(len(current_state.jugs)):
						if i == k:
							continue
						transfer_state = JugsState(current_state.jugs)
						transfer_state.jugs[i].transfer(transfer_state.jugs[k])
						# check states for duplicates, add to graph if there aren't any
						if not self.state_exists(transfer_state):
							current_state.add_state(transfer_state)
						# check for goal condition, stop computing if found
						if transfer_state.has_fill_amount(self.goal):
							transfer_state.goal_flag = True
							raise GoalFound()
							
				# recursively go through each of the child states and recurse
				for s in current_state.next_states:
					# this condition should never happen, but it's here just in case
					if s.goal_flag:
						raise GoalFound()
					_helper(s)
			# stop processing here
			except GoalFound:
				pass
			
		self.graphed = True
		_helper(self.start)

	def print_solutions(self):
		"""
		Prints every possible solution in this format:
		Solution <some number>
		[<list of jugs for this state>]
		[<list of jugs for this state>]
		[<list of jugs for this state>]
		...
		<some number> steps
		Solution <some number + 1>
		[<list of jugs for this state>]
		[<list of jugs for this state>]
		[<list of jugs for this state>]
		...
		<some number> steps

		Best solution found:
		[<list of jugs for this state>]
		[<list of jugs for this state>]
		[<list of jugs for this state>]
		...
		<some number> steps
		"""

		# these variables are only used here, but I set it to self to make it persistent
		# across all the inner functions
		self.solution_number = 0
		self.solutions = []

		# look for the goal flag (meaning the target amount was found)
		# then go back up the graph to the root and print each state
		def _traverse_states(current_state):
			if current_state.goal_flag:
				self.solution_number += 1
				print("Solution %i" % self.solution_number)

				state_list = _get_state_path(current_state)
				for s in state_list:
					print(s.jugs)
				print("%i steps" % len(state_list))
				self.solutions.append({
					"steps": len(state_list),
					"list": state_list
				})
			else:
				for s in current_state.next_states:
					_traverse_states(s)

		# recursively goes up the tree to the root and saves it in a list
		def _get_state_path(current_state, current_path = []):
			current_path = [current_state] + current_path
			if current_state.parent:
				return _get_state_path(current_state.parent, current_path)
			else:
				return current_path

		if self.graphed:
			# print every solution
			_traverse_states(self.start)
			# if there weren't any solutions, print this
			if self.solution_number == 0:
				print("No solution found!")
			# find the solution that was shortest
			else:
				print("\nBest solution found:")
				min_steps = 9999999999
				solution = None
				for s in self.solutions:
					if s["steps"] < min_steps:
						min_steps = s["steps"]
						solution = s
				for s in solution["list"]:
					print(s.jugs)
				print("%i steps" % solution["steps"])

		else:
			# graph was never built, so print this
			print("Run graph_it first!")
		
	# recursively iterate through graph, print "-" for each depth
	# print <---- when a solution was found
	def __repr__(self):
		def _helper(states, prefix = "-"):
			string = ""
			for s in states:
				string += prefix + str(s.jugs)
				if s.goal_flag:
					string += " <----"
				string += "\n"
				string += _helper(s.next_states, "-" + prefix)
			return string
				
		string = str(self.start.jugs)
		if self.start.goal_flag:
			string += " <----"
		string += "\n"
		string += _helper(self.start.next_states)
		
		return string

def main():
	jugs = input("Input each jug size, separated by space, then press enter.\n")
	goal = input("Input target amount: ")
	jugs = [Jug(int(x)) for x in jugs.split()]
	goal = int(goal)

	graph = JugsGraph(jugs, goal)
	graph.graph_it()
	print(graph)

	graph.print_solutions()

if __name__ == '__main__':
	main()