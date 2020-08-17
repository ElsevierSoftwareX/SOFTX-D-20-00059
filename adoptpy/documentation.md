How can adoptpy be used?
------------------------

Since adoptpy is based on FEniCS, most of the user input consists of definining
the objects (such as the state system and cost functional) via UFL forms. If one
has a functioning code for the forward problem and the evaluation of the cost
functional, the necessary modifications to optimize the problem in adoptpy
are minimal. Consider, e.g., the following optimization problem

$$ \min J(y, u) = \frac{1}{2} \int_{\Omega} \lvert y - y_d \rvert^2 \text{d}x + \frac{\alpha}{2} u^2 \text{d}x \\
\text{ subject to } - \Delta y = u \quad \text{ in } \Omega, \\
\hspace{7em} y = 0 \quad \text{ on } \Gamma.
$$

Note, that the entire problem is treated in detail in demo_01.py in the demos folder.

For our purposes, we assume that a mesh for this problem is defined and that a
suitable function space is chosen. This can, e.g., be achieved via

    from fenics import *
    import adoptpy

    config = adoptpy.create_config('path_to_config')
    mesh, _, boundaries, dx, ds, _ = adoptpy.regular_mesh(25)
    V = FunctionSpace(mesh, 'CG', 1)

The config object which is created from a .ini file is used to determine the
parameters for the optimization algorithms.

To define the state problem, we then define a state variable y, an adjoint variable
p and a control variable u, and write the PDE as a weak form

    y = Function(V)
    p = Function(V)
    u = Function(V)
    e = inner(grad(y), grad(p)) - u*p*dx
    bcs = adoptpy.create_bcs_list(V, Constant(0), boundaries, [1,2,3,4])

Finally, we have to define the cost functional and the optimization problem

    y_d = Expression('sin(2*pi*x[0]*sin(2*pi*x[1]))', degree=1)
    alpha = 1e-6
    J = 1/2*(y - y_d)*(y - y_d)*dx + alpha/2*u*u*dx
    opt_problem = adoptpy.OptimalControlProblem(e, bcs, J, y, u, p, config)
    opt_problem.solve()

The only major difference between adoptpy and fenics code is that one has to
use Function objects for states and adjoints, and that Trial- and TestFunctions
are not needed to define the state equation. Other than that, the syntax would
also be valid with fenics.

For a detailed discussion of the features of adoptpy and its usage we refer to the deomos.


Command line interface for meshes
---------------------------------

adoptpy includes a command line interface for converting gmsh mesh files to
xdmf ones, which can be read very easily into fenics. 



A word of caution
-----------------

I develope adoptpy as part of my PhD. I will try my best to document everything
the package is capable of and to maintain the project in a sensible fashion.
However, I cannot guarantee this. It is still undergoing many developments and,
unfortunately, the API still may undergo large changes. So use it with care.


License
-------

adoptpy is licensed under the ... license.