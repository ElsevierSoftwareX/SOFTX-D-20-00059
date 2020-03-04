lc = 1.25e-2;

Point(1) = {0, 0, 0, lc};
Point(2) = {1, 0, 0, lc};
Point(3) = {1, 1, 0, lc};
Point(4) = {0, 1, 0, lc};

Line(1) = {1,2};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,1};

Line Loop(1) = {1,2,3,4};

Plane Surface(1) = {1};

Physical Surface(1) = {1};
Physical Line(1) = {4};
Physical Line(2) = {1};
Physical Line(3) = {2};
Physical Line(4) = {3};

Mesh.CharacteristicLengthExtendFromBoundary= 1;
