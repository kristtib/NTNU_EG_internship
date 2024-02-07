import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library

def simplified_Q_trafo (P_mw, Q_mvar, k, S_base_mva):
    P_pu = P_mw/S_base_mva
    #S_pu = np.sqrt(P_mw**2 + Q_mvar**2)/S_base_mva 
    Q_simplified_trafo = -1*((k * P_pu**2)*S_base_mva)
    return Q_simplified_trafo


def generate_basic_network(sgen_p= float, sgen_q = float):
    network = pp.create_empty_network(f_hz=50)
    
    add_trafos_to_std_library(network)

    bus_lv = pp.create_bus(
        network,
        name="bus1",
        vn_kv=230,
        type="b",
    ).item()
    bus_hv = pp.create_bus(
        network,
        name="bus2",
        vn_kv=400,
        type="b",
    ).item()


    pp.create_sgen(net=network, bus=bus_lv, p_mw=sgen_p,q_mvar=sgen_q)

    trafo1 = pp.create_transformer(
        net=network, lv_bus=bus_lv, hv_bus=bus_hv, std_type="ONS_tx_400kV_230kV_400MVA")
    #trafo_tap = pp.create_transformer(net=network, lv_bus = bus_lv, hv_bus = bus_hv, std_type="ONS_tx_400kV_230kV_400MVA")
    
    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name)

    pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
    pp.plotting.to_html(net=network, filename="test.html")

    return network

def p_q_plot(sgen_p= float, sgen_q = list):
    plt.figure()
    plt.xlabel('Q_trafo [MVAr]')
    plt.ylabel('P_in [MW]')

    network = generate_basic_network(sgen_p, sgen_q = 0)
    #simplified_Q = simplified_Q_trafo(sgen_p, sgen_q, k, S_base)
    for q in sgen_q:
        k = network.trafo.vk_percent/100
        S_base = network.trafo.sn_mva
        network.sgen.q_mvar.iloc[0] = q
        active_powers = []
        reactive_powers = []
        simplified_Q = []
        step_p = int(sgen_p/10)
        for i in range (0,sgen_p+step_p,step_p):
            network.sgen.p_mw.iloc[0]=i 
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)           
            active_powers.append(i)
            reactive_powers.append(network.res_bus.iloc[-1].q_mvar - q)
            simplified_Q.append(simplified_Q_trafo(i, q, k, S_base))
            

        plt.plot(reactive_powers, active_powers, label=f"Q_trafo_LF={q}[MVAr]")
        plt.plot(simplified_Q, active_powers,label=f"Q_trafo_simp={q}[MVAr]", linestyle ='dashed' )
    plt.legend(loc="lower left")
    plt.grid()
    plt.show()



def p_q_plot1(sgen_p=float, sgen_q=list):
    
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10, 8))
    ax1.set_xlabel('Q_trafo [MVAr]')
    ax1.set_ylabel('P_in [MW]')
    ax2.set_xlabel('Q_trafo [MVAr]')
    ax2.set_ylabel('Difference (simplified - Load Flow) [MVAr]')

    network = generate_basic_network(sgen_p, sgen_q=0)

    k = network.trafo.vk_percent / 100
    S_base = network.trafo.sn_mva
    simplified_Q = []
    step_p = int(sgen_p / 10)
    for i in range(0, sgen_p + step_p, step_p):
        simplified_Q.append(simplified_Q_trafo(i, sgen_q, k, S_base))

    ax1.plot(simplified_Q, range(0, sgen_p + step_p, step_p), label=f"Q_trafo simplified [MVAr]", color ='black', linewidth ='3')
    
    for q in sgen_q:
        network.sgen.q_mvar.iloc[0] = q
        active_powers = []
        reactive_powers = []   
        delta = []  # Initialize delta for each sgen_q
        step_p = int(sgen_p / 10)
        for i in range(0, sgen_p + step_p, step_p):
            network.sgen.p_mw.iloc[0] = i
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
            active_powers.append(i)
            reactive_powers.append(network.res_bus.iloc[-1].q_mvar - q)
            difference = simplified_Q_trafo(i, q, k, S_base) - (network.res_bus.iloc[-1].q_mvar - q)
            delta.append(difference)
        ax1.plot(reactive_powers, active_powers, label=f"Q_trafo with load flow analysis, Q_in={q}[MVAr]")
        ax2.plot(active_powers, delta, label=f"Difference (simplified - Load Flow) Q_trafo, Q_in={q}[MVAr]")

    ax1.legend(loc="lower left")
    ax1.grid()
    ax2.legend(loc="upper right")
    ax2.grid()
    plt.tight_layout()
    plt.show()

list_of_q = range(-100,101,50)

p_q_plot1(400,list_of_q)


