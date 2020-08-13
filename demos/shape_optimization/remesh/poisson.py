"""
Created on 15/06/2020, 08.09

@author: blauths
"""

from fenics import *
import caospy
import numpy as np



set_log_level(LogLevel.CRITICAL)
config = caospy.create_config('./config.ini')
mesh, subdomains, boundaries, dx, ds, dS = caospy.MeshGen(config.get('Mesh', 'xdmf_file'))
V = FunctionSpace(mesh, 'CG', 1)

bcs = DirichletBC(V, Constant(0), boundaries, 1)

x = SpatialCoordinate(mesh)
# f = 2.5*pow(x[0] + 0.4 - pow(x[1], 2), 2) + pow(x[0], 2) + pow(x[1], 2) - 1
f = Expression('2.5*pow(x[0] + 0.4 - pow(x[1], 2), 2) + pow(x[0], 2) + pow(x[1], 2) - 1', degree=4, domain=mesh)

u = Function(V)
p = Function(V)

e = inner(grad(u), grad(p))*dx - f*p*dx

J = u*dx

optimization_problem = caospy.ShapeOptimizationProblem(e, bcs, J, u, p, boundaries, config)
optimization_problem.solve()

# optimization_problem.solver.line_search.mesh_handler.remesh()
# optimization_problem.solver.finalize()
