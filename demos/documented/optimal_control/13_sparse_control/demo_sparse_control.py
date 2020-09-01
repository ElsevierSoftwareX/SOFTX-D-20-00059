# Copyright (C) 2020 Sebastian Blauth
#
# This file is part of CASHOCS.
#
# CASHOCS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CASHOCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CASHOCS.  If not, see <https://www.gnu.org/licenses/>.

"""For the documentation of this demo, see doc_sparse_control.md

"""

from fenics import *
import cashocs



config = cashocs.create_config('config.ini')
mesh, subdomains, boundaries, dx, ds, dS = cashocs.regular_mesh(50)
V = FunctionSpace(mesh, 'CG', 1)

y = Function(V)
p = Function(V)
u = Function(V)

e = inner(grad(y), grad(p))*dx - u*p*dx
bcs = cashocs.create_bcs_list(V, Constant(0), boundaries, [1, 2, 3, 4])

y_d = Expression('sin(2*pi*x[0])*sin(2*pi*x[1])', degree=1)
alpha = 1e-4
J = Constant(0.5)*(y - y_d)*(y - y_d)*dx + Constant(0.5*alpha)*abs(u)*dx

ocp = cashocs.OptimalControlProblem(e, bcs, J, y, u, p, config)
ocp.solve()