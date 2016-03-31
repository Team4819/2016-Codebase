from dynamics import MyRobotDynamics
from int_dynamics.scipy_ilqg import ilqg
import numpy as np
import time
from numpy import linalg
import pickle

target_pos = np.array([0, 0, 0])


def cost_func(x, u):
    # running cost
    cost = 0
    # cost += max(3 - .1*linalg.norm(x[:2]-array([0, 5]))**2, 0)
    cost += 20**((-linalg.norm(x[:2]-np.array([-1, 5]))**2)/8**2)
    cost += 15**((-linalg.norm(x[:2]-np.array([2.5, 10]))**2)/4**2)
    cost += 15**((-linalg.norm(x[:2]-np.array([-2, 15]))**2)/4**2)
    cost += 15**((-linalg.norm(x[:2]-np.array([4, 18]))**2)/4**2)

    cost -= 20**((-linalg.norm(x[:2]-np.array([0, 20]))**2)/8**2)

    if any(np.isnan(u)):
        u[:] = 0
        cost += 3*sabs(linalg.norm(x[:2]-np.array([0, 20])), .1)

    #  control cost coefficients
    cost += np.dot(u*u, 4e-1*np.array([1, 1]))

    return cost


def sabs(x, p):
    # smooth absolute-value function (a.k.a pseudo-Huber)
    return np.sqrt(x*x + p*p) - p


def optimize_path(start_pos, target_pos_in, name):
    global target_pos
    target_pos = target_pos_in
    dynamics_engine = MyRobotDynamics.cached_init("simulation")
    dynamics_engine.dt.set_value(0.1)
    dynamics_engine.loads["drivetrain"].position.set_value(start_pos)
    dynamics_engine.prediction_func()
    init_state = dynamics_engine.mean_state.get_value()

    # optimization problem
    T = 100  # horizon
    u0 = .1 * np.random.randn(T, 2)  # initial controls
    # u0 = zeros((T, 2))  # initial controls
    options = {}

    # run the optimization
    options["lims"] = np.array([[-1, 1],
                                [-1, 1]])

    start_time = time.time()
    x, u, L, Vx, Vxx, cost = ilqg.ilqg(dynamics_engine, cost_func, init_state, u0, options)
    data = {"x": x, "u": u, "Vx": Vx, "Vxx": Vxx, "cost": cost}
    with open("{}.tdc".format(name), 'wb') as f:
        pickle.dump(data, f, -1)
    print(x[-1])
    print("ilqg took {} seconds".format(time.time() - start_time))

if __name__ == "__main__":
    optimize_path(np.array([0, 0, 0]), np.array([0, 10, 0]), "test")