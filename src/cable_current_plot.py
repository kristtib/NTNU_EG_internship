import matplotlib.pyplot as plt
from cable_options import add_cables_to_std_library
import pandapower as pp
import pandas as pd
import openpyxl



def generate_basic_network(sgen_p= float, sgen_q = float, total_line_length = float, per_line_length = float):
    network = pp.create_empty_network(f_hz=50)
    add_cables_to_std_library(network)

    lv_bus=pp.create_bus(
        network,
        name="bus1",
        vn_kv=230,
        type="b",
    ).item()

    pp.create_sgen(net=network, bus=lv_bus, p_mw=sgen_p,q_mvar=sgen_q)

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

    pp.create_ext_grid(net=network, bus=network.bus.iloc[-1].name) #to set voltage of bus
    pp.runpp(net=network, algorithm="nr", run_control=False, numba=True)
    pp.plotting.to_html(net=network, filename="test.html")

    return network

def line_current_plot(network):
    plt.figure()
    plt.xlabel('length [km]')
    plt.ylabel('I [%]')

    line_currents=[]
    comp5050=False
    comp6040=False
    comp8020=False
    for q in range(-200,200,1):
        network.sgen.at[0, "q_mvar"]=q
        pp.runpp(net=network, algorithm="nr", run_control=True, numba=True) #run new power flow calculation

        #Method to see if difference between current in and out of lines are the same. And then find the q compensation that is needed
        #if abs(network.res_line["i_from_ka"].iloc[0]-network.res_line["i_to_ka"].iloc[-1]) <= 1e-3: #If error is less than one
        #    q_compensation=q
        #    line_currents=network.res_line["i_ka"]
        #    line_names=network.line["name"]

        #    break

        error=1e-2 
        if (1-error<=abs((network.res_line["q_from_mvar"].iloc[0])/(network.res_line["q_to_mvar"].iloc[-1])) <= 1+error) and comp5050==False:
            line_currents_5050=network.res_line["i_ka"]

            q_from_5050=network.res_line["q_from_mvar"]
            q_to_5050=network.res_line["q_to_mvar"]
            v_from_5050=network.res_line["vm_from_pu"]
            v_to_5050=network.res_line["vm_to_pu"]

            comp5050=True
            plt.plot(line_currents_5050*100/1.0213003186436418,color='red')
            #pp.plotting.to_html(net=network, filename="test.html")

            '''
            print('For 50/50 compensation:')
            print(f'Q_gen={q}')
            print(f'Q_from={network.res_line["q_from_mvar"].iloc[0]}')
            print(f'Q_to={network.res_line["q_to_mvar"].iloc[-1]}')
            print('\n')
            '''


        error=0.3
        if (60/40)-error <=(abs((network.res_line["q_from_mvar"].iloc[0])/(network.res_line["q_to_mvar"].iloc[-1]))<=(60/40))+error and comp6040==False:
            line_currents_6040=network.res_line["i_ka"]

            q_from_6040=network.res_line["q_from_mvar"]
            q_to_6040=network.res_line["q_to_mvar"]
            v_from_6040=network.res_line["vm_from_pu"]
            v_to_6040=network.res_line["vm_to_pu"]

            comp6040=True
            plt.plot(line_currents_6040*100/1.0213003186436418,color='blue') 
            #pp.plotting.to_html(net=network, filename="test.html")

            '''
            print('For 60/40 compensation:')
            print(f'Q_gen={q}')
            print(f'Q_from={network.res_line["q_from_mvar"].iloc[0]}')
            print(f'Q_to={network.res_line["q_to_mvar"].iloc[-1]}')
            print('\n')
            '''    
        error=1
        if 140-error<=abs(network.res_line["q_from_mvar"].iloc[0])<=140+error and comp8020==False:
        #if (80/20)-error <=(abs((network.res_line["q_from_mvar"].iloc[0])/(network.res_line["q_to_mvar"].iloc[-1]))<=(80/20))+error and comp8020==False:
            line_currents_8020=network.res_line["i_ka"]
            
            plt.plot(line_currents_8020*100/1.0213003186436418,color='green') 


            q_from_8020=network.res_line["q_from_mvar"]
            q_to_8020=network.res_line["q_to_mvar"]
            v_from_8020=network.res_line["vm_from_pu"]
            v_to_8020=network.res_line["vm_to_pu"]
            
            comp8020=True

        if comp5050==True and comp6040==True and comp8020==True:
            break
        
        
    #plt.plot(line_names, line_currents, label=f"Q_sgen={q_compensation}[MVAr]")
    
    plt.xticks([])
    #plt.savefig('compensation_plot.png')
    plt.show()

    #For powerpoint
    '''
    df_5050 = pd.DataFrame([[q_from_5050[0] , q_to_5050.iloc[-1]] , [line_currents_5050[0] , line_currents_5050.iloc[-1]] , [v_from_5050[0],v_to_5050.iloc[-1]], [line_currents_5050[int((len(line_currents_5050))/2)], 0]], index=['Q' , 'I' , 'V','I_middle'], columns=['OFS' , 'ONS'])
    df_5050.to_excel('line_current_5050_compensation.xlsx', sheet_name='Sheet1')

    df_6040 = pd.DataFrame([[q_from_6040[0] , q_to_6040.iloc[-1]] , [line_currents_6040[0] , line_currents_6040.iloc[-1]] , [v_from_6040[0],v_to_6040.iloc[-1]], [line_currents_6040[int((len(line_currents_6040))/2)], 0]], index=['Q' , 'I' , 'V','I_middle'], columns=['OFS' , 'ONS'])
    df_6040.to_excel('line_current_6040_compensation.xlsx', sheet_name='Sheet1')

    df_8020 = pd.DataFrame([[q_from_8020[0] , q_to_8020.iloc[-1]] , [line_currents_8020[0] , line_currents_8020.iloc[-1]] , [v_from_8020[0],v_to_8020.iloc[-1]], [line_currents_8020[int((len(line_currents_8020))/2)], 0]], index=['Q' , 'I' , 'V','I_middle'], columns=['OFS' , 'ONS'])
    df_8020.to_excel('line_current_8020_compensation.xlsx', sheet_name='Sheet1')
    '''

network=generate_basic_network(sgen_p=400,sgen_q=0,total_line_length=70,per_line_length=5)
line_current_plot(network)
