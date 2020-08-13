"""
Created on 24/02/2020, 09.19

@author: blauths
"""

import fenics
import numpy as np
from ..nonlinear_solvers import NewtonSolver


class StateProblem:
	"""The state system

	"""

	def __init__(self, form_handler, initial_guess):
		"""Initialize the state system
		
		Parameters
		----------
		form_handler : caospy._forms.FormHandler or caospy._forms.ShapeFormHandler
			the FormHandler of the optimization problem
		initial_guess : list[dolfin.function.function.Function]
			an initial guess for the state variables, used to initialize them in each iteration
		"""
		
		self.form_handler = form_handler
		self.initial_guess = initial_guess

		self.config = self.form_handler.config
		self.bcs_list = self.form_handler.bcs_list
		self.states = self.form_handler.states

		self.rtol = self.config.getfloat('StateEquation', 'picard_rtol', fallback=1e-10)
		self.atol = self.config.getfloat('StateEquation', 'picard_atol', fallback=1e-20)
		self.maxiter = self.config.getint('StateEquation', 'picard_iter', fallback=50)
		self.picard_verbose = self.config.getboolean('StateEquation', 'picard_verbose', fallback=False)
		self.newton_rtol = self.config.getfloat('StateEquation', 'inner_newton_rtol')
		self.newton_atol = self.config.getfloat('StateEquation', 'inner_newton_atol')


		self.number_of_solves = 0
		self.has_solution = False
	
	
	
	def solve(self):
		"""Solves the state system
		
		Returns
		-------
		states : list[dolfin.function.function.Function]
			the solution of the state system
		"""

		if not self.has_solution:
			if self.initial_guess is not None:
				for j in range(self.form_handler.state_dim):
					fenics.assign(self.states[j], self.initial_guess[j])


			if not self.config.getboolean('StateEquation', 'picard_iteration'):
				if self.config.getboolean('StateEquation', 'is_linear'):
					for i in range(self.form_handler.state_dim):
						fenics.PETScOptions.clear()
						fenics.PETScOptions.set('mat_mumps_icntl_24', 1)
						fenics.solve(self.form_handler.state_eq_forms_lhs[i]==self.form_handler.state_eq_forms_rhs[i], self.states[i], self.bcs_list[i],
									 solver_parameters={'linear_solver': 'mumps'})
						# fenics.solve(self.form_handler.state_eq_forms_lhs[i]==self.form_handler.state_eq_forms_rhs[i], self.states[i], self.bcs_list[i], solver_parameters={'linear_solver': 'petsc'})

				else:
					for i in range(self.form_handler.state_dim):
						if self.initial_guess is not None:
							fenics.assign(self.states[i], self.initial_guess[i])

						self.states[i] = NewtonSolver(self.form_handler.state_eq_forms[i], self.states[i], self.bcs_list[i],
													  rtol=self.newton_rtol, atol=self.newton_atol, damped=True, verbose=True)

			else:
				newton_atols = [1 for i in range(self.form_handler.state_dim)]
				for i in range(self.maxiter + 1):
					res = 0.0
					for j in range(self.form_handler.state_dim):
						res_j = fenics.assemble(self.form_handler.state_picard_forms[j])

						[bc.apply(res_j) for bc  in self.form_handler.bcs_list_ad[j]]

						if self.number_of_solves==0 and i==0:
							newton_atols[j] = res_j.norm('l2') * self.newton_atol
							if res_j.norm('l2') == 0.0:
								newton_atols[j] = self.newton_atol

						res += pow(res_j.norm('l2'), 2)

					if res==0:
						break

					res = np.sqrt(res)

					if i==0:
						res_0 = res

					if self.picard_verbose:
						print('Iteration ' + str(i) + ': ||res|| (abs): ' + format(res, '.3e') + '   ||res|| (rel): ' + format(res/res_0, '.3e'))

					if res/res_0 < self.rtol or res < self.atol:
						break

					if i==self.maxiter:
						raise SystemExit('Failed to solve the Picard Iteration')

					for j in range(self.form_handler.state_dim):
						# fenics.solve(self.form_handler.state_eq_forms[j]==0, self.states[j],
						# 			 self.bcs_list[j], solver_parameters={'nonlinear_solver' : 'newton', 'newton_solver' :
						# 													{'linear_solver' : 'mumps','relative_tolerance' : self.newton_rtol,'absolute_tolerance' : self.newton_atol}})
						if self.initial_guess is not None:
							fenics.assign(self.states[i], self.initial_guess[i])
						self.states[j] = NewtonSolver(self.form_handler.state_eq_forms[j], self.states[j], self.bcs_list[j],
													  rtol=np.minimum(0.9*res, 0.9), atol=newton_atols[j], damped=False, verbose=False)


			if self.picard_verbose:
				print('')
			self.has_solution = True
			self.number_of_solves += 1

		return self.states