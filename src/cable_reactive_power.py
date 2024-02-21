import matplotlib.pyplot as plt
import pandapower as pp
import numpy as np
import math
import cmath

from gen_network import generate_basic_network

def calculate_q_cable_distributed_pi(network):
    #Find V_r, I_r, S_r at ONS point
    v_r_mag=network.res_line.vm_to_pu.iloc[-1]*230 #kV
    v_r_angle=network.res_line.va_to_degree.iloc[-1]
    p_r=-network.res_line.p_to_mw.iloc[-1]
    q_r=-network.res_line.q_to_mvar.iloc[-1]
            
    V_r=complex(v_r_mag*cmath.cos(math.radians(v_r_angle)), v_r_mag*cmath.sin(math.radians(v_r_angle)))
    S_r=complex(p_r,q_r) #MVA
    I_r=S_r.conjugate()/V_r.conjugate() #kA

    #Calculate parameters for distributed PI model
    f=50
    omega=2*math.pi*f
    
    y=complex(0,omega*network.line.at[0,"c_nf_per_km"]*10**-9)
    z=complex(network.line.at[0,"r_ohm_per_km"], network.line.at[0,"x_ohm_per_km"])
    l=network.line.at[0,"length_km"]

    Z_c=cmath.sqrt(z/y)
    gamma=cmath.sqrt(y*z)

    A=D=cmath.cosh(gamma*l)
    B=Z_c*cmath.sinh(gamma*l)
    C=(cmath.sinh(gamma*l))/Z_c

    #Iterate for each cable segment
    for i in range(len(network.line)):
        V_s=A*V_r + B*I_r
        I_s=C*V_r + D*I_r

        V_r=V_s
        I_r=I_s
    
    #Calculate S_s on OFS point
    S_s=V_s*I_s.conjugate()
    Q_prod=(S_r-S_s).imag #find the reactive power produced in the cable

    return Q_prod

def calculate_q_cable_simplified(network):
    omega=2*math.pi*50
    V=230 #kV

    c_km=network.line.at[0,"c_nf_per_km"]*10**-9
    tot_km=sum(network.line.length_km)
    x_c=1/(omega*c_km*tot_km)
    Q_c=(V**2)/x_c

    S=complex(network.sgen.at[0, "p_mw"],0) #MVA
    I=abs((S/(V)).conjugate())
    
    x_l=network.line.at[0,"x_ohm_per_km"]*tot_km
    Q_l=(I**2)*x_l

    return Q_c-Q_l

def plot_cable_Q(network):
    #Define figures
    fig, (ax1, ax2) = plt.subplots(2)
    ax1.set_title("Self-generated reactive power in cable")
    ax1.set_xlabel("Q [MVar]")
    ax1.set_ylabel("P [MW]")
    ax1.grid()

    ax2.set_title("Error of distributed PI model")
    ax2.set_xlabel("P [MW]")
    ax2.set_ylabel("Error [%]")
    ax2.grid()

    #Define step sizes for plot
    q_step=10
    p_step=10

    #Add plot of simplified pi model for sgen_q=0
    q_generated_simplified=[]
    q_generated_s=[]
    for p in range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step):
        network.sgen.at[0, "q_mvar"]=0
        network.sgen.at[0,"p_mw"]=p
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True)
        
        q_produced_simplified =calculate_q_cable_distributed_pi(network)
        q_generated_simplified.append(q_produced_simplified)

        q_produced_s=calculate_q_cable_simplified(network)
        q_generated_s.append(q_produced_s)
    ax1.plot(q_generated_simplified,range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step),color="black",label=f"Distributed PI model")
    ax1.plot(q_generated_s,range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step),label=f"Simplified model")

    #Add plot for LFS for different compensations
    for q in range(-10,10+q_step,q_step):
        network.sgen.at[0, "q_mvar"]=q #update q generated from sgen
        #network.sgen.q_mvar[0]=q #update q generated from sgen
        
        q_generated=[]
        for p in range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step):
            network.sgen.at[0,"p_mw"]=p
            #network.sgen.p_mw[0]=p #update p generated from sgen
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True) #run new power flow calculation

            #LFS
            q_in=network.res_line.q_from_mvar[0]
            q_out=network.res_line.q_to_mvar.iloc[-1]
            q_produced=-q_out-q_in

            #Add to lists for plotting
            q_generated.append(q_produced)
        
        #Find error in percentage
        error_percent=(np.array(q_generated_simplified)-np.array(q_generated))/np.array(q_generated)            
        
        ax1.plot(q_generated,range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step),label=f"Q_sgen={q}[MVar]")
        ax2.plot(range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step),error_percent,label=f"Q_sgen={q}[MVar]")
    
    ax1.legend(loc="upper right")
    ax2.legend(loc="upper right")

    plt.tight_layout()
    plt.show()

network=generate_basic_network(sgen_p=400,sgen_q=0,total_line_length=70,per_line_length=5)
plot_cable_Q(network)


