-----------------------------------------------------------------------------------------------------------------------------

Required dependencies:

`pygame`    : pip install pygame
`neat`      : pip install neat-python


`visualize.py` is completely optional. It requires some additional dependencies. Feel free to exclude that import. If you decide not to import that module, make sure to comment line numbers #342, #343, #344. 

*If you want the rocks to be dynamic, make sure to uncomment lines #133 through #158. They are commented by default.

-----------------------------------------------------------------------------------------------------------------------------

SimulationTrainedAgents

In this simulation, each Rover will be able to 'see' in 256 directions. If there is a Rock in the line of sight, the Distance between the Rock and the
Rover, the Angle between the line passing through the Rover's horizontal and the line joining the Rock and the Rover, the Width and Height of
the Rock (if any) will be returned. If there are no Rocks in the line of sight of the Rover, they will be returning DEFAULT for all parameters. It will
also know the distance to each boundary and finally it's position in the environment.

Neural Network Architecture*:

Input Layer: 1030 Nodes
    4  - Boundaries
    2  - Rover's Co-ordinates
    256 - Distances in each Direction
    256 - Thetas
    256 - Widths
    256 - Heights

Output Layer: 4 Nodes
    1 - (N) Up
    1 - (S) Down
    1 - (E) Right
    1 - (W) Left

*The architecture of the Neural Network is subject to change with evolution.
