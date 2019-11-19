import firedrake as fe
import sapphire.simulations.alloy_phasechange

    
def initial_values(sim):
    
    w_0 = fe.Function(sim.function_space)
    
    h_0, S_l_0 = w_0.split()
    
    assumed_initial_porosity = 1.
    
    constant_initial_enthalpy = \
        sapphire.simulations.alloy_phasechange.enthalpy(
            sim = sim,
            temperature = sim.initial_temperature,
            porosity = assumed_initial_porosity)
    
    h_0 = h_0.assign(constant_initial_enthalpy)
    
    S_l_0 = S_l_0.assign(sim.initial_concentration)
    
    constant_initial_porosity = \
        sapphire.simulations.alloy_phasechange.regularized_porosity(
            sim = sim,
            enthalpy = constant_initial_enthalpy,
            solute_concentration = sim.initial_concentration)
    
    epsilon = 0.01
    
    phi_l_0 = constant_initial_porosity.__float__()
    
    if abs(phi_l_0 - assumed_initial_porosity) >= epsilon:
    
        raise ValueError(
            "For this test, it is assumed that the initial porosity is equal to {} +/- {}.".format(
                assumed_initial_porosity, epsilon)
            +"\nWhen setting initial values, the initial porosity was computed to be {}.".format(
                phi_l_0))
    
    return w_0
    
    
def dirichlet_boundary_conditions(sim):
    
    phi_lc = sim.cold_boundary_porosity
    
    h_c = sapphire.simulations.alloy_phasechange.enthalpy(
        sim = sim,
        temperature = sim.cold_boundary_temperature,
        porosity = phi_lc)
    
    S_l_c = sapphire.simulations.alloy_phasechange.\
        mushy_layer_solute_concentration(
            sim = sim,
            enthalpy = h_c,
            porosity = phi_lc)
        
    W = sim.function_space
    
    return [
        fe.DirichletBC(W.sub(0), h_c, 1),
        fe.DirichletBC(W.sub(1), S_l_c, 1)]
    

class Simulation(sapphire.simulations.alloy_phasechange.Simulation):
    
    def __init__(self, *args, 
            initial_concentration,
            cold_boundary_temperature,
            cold_boundary_porosity,
            mesh_cellcount, 
            cutoff_length, 
            **kwargs):
        
        self.initial_concentration = fe.Constant(initial_concentration)
        
        self.cold_boundary_temperature = fe.Constant(cold_boundary_temperature)
        
        self.cold_boundary_porosity = fe.Constant(cold_boundary_porosity)
        
        super().__init__(
            *args,
            mesh = fe.IntervalMesh(mesh_cellcount, cutoff_length),
            initial_values = initial_values,
            dirichlet_boundary_conditions = dirichlet_boundary_conditions,
            **kwargs)
        