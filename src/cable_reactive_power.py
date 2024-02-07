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
    I=abs((S/V).conjugate())
    
    x_l=network.line.at[0,"x_ohm_per_km"]*tot_km
    Q_l=(I**2)*x_l

    return Q_c-Q_l


def plot_cable_Q(network):
    plt.figure()
    plt.xlabel('Self-generated reactive power in cable [MVar]')
    plt.ylabel('Active power [MW]')

    q_step=10
    p_step=10
    for q in range(0,0+q_step,q_step):
        network.sgen.at[0, "q_mvar"]=q #update q generated from sgen
        #network.sgen.q_mvar[0]=q #update q generated from sgen
        
        q_generated=[]
        q_generated_simplified=[]
        p_generated=[]
        p_generated_simplified=[]
        for p in range(0,int(network.sgen.at[0, "p_mw"])+p_step,p_step):
            network.sgen.at[0,"p_mw"]=p
            #network.sgen.p_mw[0]=p #update p generated from sgen
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True) #run new power flow calculation

            q_in=network.res_line.q_from_mvar[0]
            q_out=network.res_line.q_to_mvar.iloc[-1]
            q_produced=q_in-q_out-q

            #Find values to calculate simplified model
            v_r_mag=network.res_line.vm_to_pu.iloc[-1]*230 #kV
            v_r_angle=network.res_line.va_to_degree.iloc[-1]
            
            v_r=complex(v_r_mag*cmath.cos(math.radians(v_r_angle)), v_r_mag*cmath.sin(math.radians(v_r_angle)))
            s_r=complex(p,q_produced) #MVA
            i_r=s_r.conjugate()/v_r.conjugate() #kA


            v_s,i_s =calculate_simplified_q_cable(network, V_r=v_r, I_r=i_r)
            s_s=v_s*i_s.conjugate()

            q_generated.append(q_produced)
            p_generated.append(p)
            q_generated_simplified.append((s_s).imag)
            p_generated_simplified.append((s_s).real)
    
        plt.plot(q_generated,p_generated,label=f"Q(LFS)")
        plt.plot(q_generated_simplified,p_generated_simplified,linestyle="dashed",label=f"Q(simplified)")
    
    plt.legend(loc="upper right")
    plt.grid()
    plt.show()

network=generate_basic_network(sgen_p=400,sgen_q=0,total_line_length=70,per_line_length=10)
plot_cable_Q(network)
#calculate_simplified_q_cable(network)


