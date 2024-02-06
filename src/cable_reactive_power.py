import matplotlib.pyplot as plt
import pandapower as pp

from gen_network import generate_basic_network

def plot_cable_Q(sgen_p=float, sgen_q=float, total_line_length=float, per_line_length=float):
    network=generate_basic_network(sgen_p=sgen_p,sgen_q=sgen_q,total_line_length=total_line_length,per_line_length=per_line_length)

    plt.figure()
    plt.xlabel('Self-generated reactive power in cable [MVar]')
    plt.ylabel('Active power generated [MW]')

    q_step=10
    p_step=10
    for q in range(-30,30+q_step,q_step):
        network.sgen.at[0, "q_mvar"]=q #update q generated from sgen
        #network.sgen.q_mvar[0]=q #update q generated from sgen
        
        q_generated=[]
        p_generated=[]
        for p in range(0,sgen_p+p_step,p_step):
            network.sgen.at[0,"p_mw"]=p
            #network.sgen.p_mw[0]=p #update p generated from sgen
            pp.runpp(net=network, algorithm="nr", run_control=True, numba=True) #run new power flow calculation

            q_in=network.res_line.q_from_mvar[0]
            q_out=network.res_line.q_to_mvar.iloc[-1]
            q_generated.append(q_in-q_out-q)
            p_generated.append(p)
    
        plt.plot(q_generated,p_generated,label=f"Q_generated={q}[MVar]")
    
    plt.legend(loc="upper right")
    plt.grid()
    plt.show()


plot_cable_Q(sgen_p=400,sgen_q=-40,total_line_length=80,per_line_length=10)


