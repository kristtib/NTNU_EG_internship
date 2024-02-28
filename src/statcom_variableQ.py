import pandapower as pp
import numpy as np
import matplotlib.pyplot as plt
import random
import pandapower.control as ct
from cable_options import add_cables_to_std_library
from trafo_options import add_trafos_to_std_library


def calculate_q_mv_bus(sgen_p=float, sgen_q=float, total_line_length=float, per_line_length=float):
    #Create empty network
    network = pp.create_empty_network(f_hz=50)

    #Add cables&trafo
    add_cables_to_std_library(network)
    add_trafos_to_std_library(network)

    #Create full network
    pp.create_bus(
        network,
        name="bus1",
        vn_kv=66,
        type="b",
    ).item()
    pp.create_bus(
        network,
        name="bus2",
        vn_kv=230,
        type="b",
    ).item()

    pp.create_sgen(net=network, bus=0, p_mw=sgen_p,q_mvar=sgen_q)
    pp.create_transformer(
        net=network, lv_bus=0, hv_bus=1, std_type="OFS_tx_220kV_66kV_400MVA"
    )

    for i in range(0, total_line_length, per_line_length):
        pp.create_bus(
            network,
            name="bus"+str(network.bus.iloc[-1].name+2),
            vn_kv=230,
            type="b",
        ).item()

        pp.create_line(
            net=network,
            name=f"line{i+per_line_length}",
            from_bus=network.bus.iloc[-2].name,
            to_bus=network.bus.iloc[-1].name,
            std_type="245kv_1000mm2_cu",
            # std_type="490-AL1/64-ST1A 110.0",
            length_km=per_line_length,
        )
    
    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name)

    pp.runpp(net=network, algorithm="nr", run_control=False, numba=True)

    #Iterate to find reactive powers for different active powers for system
    active_powers=[]
    reactive_power_mv_bus=[]
    step_p = int(sgen_p/10)
    for i in range (0,sgen_p+step_p,step_p):
        network.sgen.p_mw.iloc[0]=i 
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
        active_powers.append(i)
        reactive_power_mv_bus.append(network.res_bus.iloc[-1].q_mvar)

    
    return network, reactive_power_mv_bus, active_powers

def calculate_q_mv_bus_2(a,b):
    sgen_p=400
    active_powers=[]
    reactive_power_mv_bus=[]
    step_p=int(sgen_p/10)
    for p in range (0,sgen_p+step_p,step_p):
        active_powers.append(p)
        reactive_power=a*(p**2)+b
        reactive_power_mv_bus.append(reactive_power)
    
    return reactive_power_mv_bus, active_powers

def create_three_winding_network():
    network = pp.create_empty_network(f_hz=50)

    #Add 3w trafo
    on_tx_400kV_220kV_36kV_450MVA = { "name": "on_tx_400kV_220kV_36kV_450MVA", "sn_hv_mva": 450, "sn_mv_mva": 380, "sn_lv_mva": 250, "vn_hv_kv": 410, "vn_mv_kv": 230, "vn_lv_kv": 35.7, "vk_hv_percent": 13,
                                     "vk_mv_percent": 15, "vk_lv_percent": 18, "vkr_hv_percent": 0.17, "vkr_mv_percent": 0.35, "vkr_lv_percent": 0.44, "pfe_kw": 114 ,
                                     "i0_percent": 0.2, "shift_mv_degree": 0, "shift_lv_degree": 0, "vector_group": "YNyn0d11", "tap_side": "hv",   "tap_neutral": 0,
                                     "tap_min": -10,    "tap_max": 10,  "tap_step_percent": 1.5 }

    pp.create_std_type(
            network,
            name=on_tx_400kV_220kV_36kV_450MVA["name"],
            data=on_tx_400kV_220kV_36kV_450MVA,
            element="trafo3w",
        )
    
    #Create system
    bus_mv = pp.create_bus(
        network,
        name="mv_bus",
        vn_kv=230,
        type="b",
    ).item()
    bus_hv = pp.create_bus(
        network,
        name="hv_bus",
        vn_kv=400,
        type="b",
    ).item()
    bus_lv=pp.create_bus(
        network,
        name="lv_bus",
        vn_kv=35.7,
        type="b"
    ).item()    
    trafo1=pp.create_transformer3w(net=network, hv_bus=bus_hv, mv_bus=bus_mv, lv_bus=bus_lv, std_type="on_tx_400kV_220kV_36kV_450MVA")
    ct.ContinuousTapControl(net=network,tid=trafo1,vm_set_pu=1,side='mv',trafotype='3W')
    #trafo_tap = pp.create_transformer(net=network, lv_bus = bus_lv, hv_bus = bus_hv, std_type="ONS_tx_400kV_230kV_400MVA")
    
    gen=pp.create_sgen(net=network, bus=bus_mv, p_mw=0,q_mvar=0)
    grid=pp.create_ext_grid(net=network, bus=bus_hv)
    statcom=pp.create_load(net=network,bus=bus_lv,const_i_percent=100,q_mvar=0,p_mw=0)

    return network

def calulate_q_statcom(active_powers=list, sgen_q=float):
    network=create_three_winding_network()
    network.sgen.q_mvar.iloc[0]=sgen_q
    
    reactive_power_no_statcom=[]
    for i in range(len(active_powers)):
        network.sgen.p_mw.iloc[0]=active_powers[i]
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
        
        reactive_power_no_statcom.append(network.res_bus.iloc[1].q_mvar)

    reactive_powers_min=[]
    network.load.q_mvar.iloc[0]=-150
    for i in range(len(active_powers)):
        network.sgen.p_mw.iloc[0]=active_powers[i]
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
        reactive_powers_min.append(network.res_bus.iloc[1].q_mvar)
    
    reactive_powers_max=[]
    network.load.q_mvar.iloc[0]=150
    for i in range(len(active_powers)):
        network.sgen.p_mw.iloc[0]=active_powers[i]
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)       
        reactive_powers_max.append(network.res_bus.iloc[1].q_mvar)
        
    array1=np.array(reactive_power_no_statcom)
    array2=np.array(reactive_powers_min)
    array3=np.array(reactive_powers_max)

    reactive_power_statcom_min=array2-array1
    reactive_power_statcom_max=array3-array1

    return reactive_power_statcom_min, reactive_power_statcom_max

def calulate_q_statcom_variableQ(reactive_power_mv_bus=list,active_powers=list):
    network=create_three_winding_network()
    '''
    plt.figure()
    plt.xlabel('Q_statcom [MVAr]')
    plt.ylabel('P_in [MW]')
    '''
    
    reactive_power_no_statcom=[]
    for i in range (len(reactive_power_mv_bus)):
        network.sgen.p_mw[0]=active_powers[i]
        network.sgen.q_mvar[0]=reactive_power_mv_bus[i]
        
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6)

        reactive_power_no_statcom.append(network.res_bus.iloc[1].q_mvar)  

    reactive_powers_min=[]
    network.load.q_mvar.iloc[0]=-150
    for i in range (len(reactive_power_mv_bus)):
        network.sgen.p_mw[0]=active_powers[i]
        network.sgen.q_mvar[0]=reactive_power_mv_bus[i]
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6) 

        reactive_powers_min.append(network.res_bus.iloc[1].q_mvar)
    
    reactive_powers_max=[]
    network.load.q_mvar.iloc[0]=150
    for i in range (len(reactive_power_mv_bus)):
        network.sgen.p_mw[0]=active_powers[i]
        network.sgen.q_mvar[0]=reactive_power_mv_bus[i]
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True,tolerance_mva=1e-6) 

        reactive_powers_max.append(network.res_bus.iloc[1].q_mvar)
        
    array1=np.array(reactive_power_no_statcom)
    array2=np.array(reactive_powers_min)
    array3=np.array(reactive_powers_max)

    reactive_power_statcom_min=array2-array1
    reactive_power_statcom_max=array3-array1
    '''
    plt.plot(reactive_power_statcom_min, active_powers)
    plt.plot(reactive_power_statcom_max, active_powers)
    
    plt.legend(loc="lower left")
    plt.grid()
    plt.show()
    '''

    return reactive_power_statcom_min, reactive_power_statcom_max

def plot_q_statcom():
    fig, (ax1,ax2) = plt.subplots(2,1)

    for b in range (10,70,10):
        for a in range (-90, -25, 5):
            line_color=(random.random(),random.random(),random.random())

            reactive_power_mv_bus,active_powers=calculate_q_mv_bus_2(a=a*1e-5,b=b)
            ax1.plot(reactive_power_mv_bus,active_powers,color=line_color)

            reactive_power_statcom_min_variableQ, reactive_power_statcom_max_variableQ=calulate_q_statcom_variableQ(reactive_power_mv_bus,active_powers)
            ax2.plot(reactive_power_statcom_min_variableQ, active_powers, color=line_color, label=f'Variable Q, b={b}, a={a}')
            ax2.plot(reactive_power_statcom_max_variableQ, active_powers, color=line_color)
    
    sgen_q=0
    reactive_power_statcom_min, reactive_power_statcom_max=calulate_q_statcom(active_powers=active_powers,sgen_q=sgen_q)
    ax2.plot(reactive_power_statcom_min, active_powers,label=f'Const Q_gen=0',color='black',linewidth=2.5)
    ax2.plot(reactive_power_statcom_max, active_powers,color='black',linewidth=2.5)

    ax1.grid()
    ax2.grid()
    plt.show()
    '''
    for b in range (20,70,10):
        for a in range (-50, -25, 5):
            plt.figure()
            plt.title(f'b={b}')
            plt.xlabel('Q_sys [MVAr]')
            plt.ylabel('P_in [MW]')
            reactive_power_mv_bus,active_powers=calculate_q_mv_bus_2(a=a*1e-5,b=b)
            plt.plot(reactive_power_mv_bus,active_powers)
            plt.grid()
            plt.gca().axvline(0, color='black', linewidth=2)  # Make y=0 bold
            plt.gca().axhline(0, color='black', linewidth=2)  # Make x=0 bold


    plt.figure()
    plt.xlabel('Q_statcom [MVAr]')
    plt.ylabel('P_in [MW]')
    
    for b in range (20,70,10):
        for a in range (-50, -25, 5):
            reactive_power_mv_bus,active_powers=calculate_q_mv_bus_2(a=a*1e-5,b=b)

            reactive_power_statcom_min_variableQ, reactive_power_statcom_max_variableQ=calulate_q_statcom_variableQ(reactive_power_mv_bus,active_powers)

            line_color=(random.random(),random.random(),random.random())
            plt.plot(reactive_power_statcom_min_variableQ, active_powers, color=line_color, label=f'Variable Q, b={b}, a={a}')
            plt.plot(reactive_power_statcom_max_variableQ, active_powers, color=line_color)

    sgen_q=0
    reactive_power_statcom_min, reactive_power_statcom_max=calulate_q_statcom(active_powers=active_powers,sgen_q=sgen_q)
    plt.plot(reactive_power_statcom_min, active_powers,label=f'Const Q_gen=0',color='black',linewidth=2.5)
    plt.plot(reactive_power_statcom_max, active_powers,color='black',linewidth=2.5)
    '''
    
    #plt.legend(loc="lower left")
    #plt.grid()
    #plt.show()

plot_q_statcom()