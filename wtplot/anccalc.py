
"""
Usage:
    anccalc.py <ahc_dat> <axis> [-t <T>] [-r] [-s <SAVE_PATH>]

Options:
    <ahc_dat>       ahcの計算を行ったディレクトリ
    <axis>          x,y,z
    -t <T>          温度, "1-100-300"などと指定, いくつ指定してもよい [default:  1-100-300]
    -r              ahcの値の正負を反転する
    -s <SAVE_PATH>  ancdatの出力名
"""

from docopt import docopt
import numpy as np
import pandas as pd
from scipy.constants import *

from matplotlib import pyplot as plt

import plottool as pt
import wtplot.ahcplot as wtahc

pt.mpl_init()
cosh_cutoff=200

def calc_anc(Ene, AHC, T):
    beta=1/(k*T)
    #LはAHCの外挿の収束距離, 端のデータ点の振る舞いが変わる
    L=(Ene[1]-Ene[0])*5

    #ep_mu: ε-μ のこと
    #分母のcoshの中身がcutoffを超えると全体として小さいため、積分計算に含めない
    ep_mu_max=((cosh_cutoff/beta)/e)
    #
    # df/dε=β*1/[2+2cosh(β(ε-μ)*e)]
    #
    # fはFermi分布関数
    # 電気素量eをかけるのはeVからJへの単位変換
    # cosh(x)はx=0でピークを持ち,絶対値が大きくなると指数的に大きくなる。
    # 計算量を減らすため,coshが非常に大きい領域ではdf/dεが0として積分を行う。


    # coshの中身の絶対値がしきい値より小さい領域で、meshを切って内挿or外挿によりデータ点を増やす。
    ep_step=ep_mu_max*2/10000
    ep_mu_mesh=np.arange(-1*ep_mu_max, ep_mu_max, ep_step)
    df_dep_mesh=[ -1/(2+2*np.cosh(beta*e*(ep_mu))) for ep_mu in ep_mu_mesh ]

    ANC_list=[]
    for mu in Ene :

        #----- 内挿 or 外挿によりデータ点をmu周りで10000点作成 -----#
        ep_mesh=[ ep_mu+mu for ep_mu in ep_mu_mesh ]
        sgm_mesh=[]
        for ep in ep_mesh:
            flag=0
            for i,E in enumerate(Ene):
                if ep < E : 
                    flag=1
                    break
            ### 与えられたEneの範囲にepがなければ外挿する ###
            #εがすべてのEneより小さいとき
            if ( i == 0 ) and ( flag == 1 ) :
                a = (AHC[1]-AHC[0])/(Ene[1]-Ene[0])
                sgm=AHC[0]-a*(Ene[0]-ep)*np.exp(-(Ene[0]-ep)/L)

            #εがすべてのEneより大きいとき
            elif ( i == len(Ene)-1 ) and ( flag == 0 ) :
                a=(AHC[i]-AHC[i-1])/(Ene[i]-Ene[i-1])
                sgm=AHC[i]+a*(ep-Ene[i])*np.exp(-(ep-Ene[i])/L)

            ##########

            ### Eneの範囲内ならば線形に内挿してahcのデータ点を得る ###
            else :
                a=(AHC[i]-AHC[i-1])/(Ene[i]-Ene[i-1])
                sgm=AHC[i-1]+a*(ep-Ene[i-1])
            sgm_mesh.append(sgm)

            ##########
            #sgm_mesh, ep_meshが内挿によって得た新たなデータ点のlist
            #ep_meshはmuを中心としたcosh_cutoffを満たす範囲内を10000点に分割する
            #sgm_meshはAHCのリストから線形に内挿することにより得ている
            #Eneの定義域を超えた点のsgm_meshは距離で指数収束する外挿により得ている

        #----- ANCの計算(積分の実行) -----#
        ANC=0
        for i, ep_mu in enumerate(ep_mu_mesh):
            ANC=ANC+sgm_mesh[i]*ep_mu*df_dep_mesh[i]
        ANC=ANC*ep_step*beta/T
        ANC=ANC*100*e #eは分子に2つ分母に1つで1つ残る
        ANC_list.append(ANC)

    return ANC_list

def main():
    args = docopt(__doc__)
    print(args)
    T = [ float(t) for t in args['-t'].split('-') ]
    ahcrow = { 'x':2, 'y':3, 'z':1 }
    Ene, AHC = wtahc.read_ahc_dat(args['<ahc_dat>'], ahcrow[args['<axis>']], args['-r'])

    if args['-s'] is None:
        datname = "anc_{}_{}.dat".format(args['<axis>'], args['-t'])
    else: datname = "{}-anc_{}_{}.dat".format(args['-s'], args['<axis>'], args['-t'])

    df = pd.DataFrame(data = Ene, columns = ["Ene"])
    df["ahc-{}".format(args['<axis>'])] = AHC
    for tp in T:
        df["anc-{}".format(tp)] = calc_anc(Ene, AHC, tp)
        print("Temperature {} end".format(tp))

    with open (datname, 'w') as f: 
        f.write(df.to_string(index=False))


if __name__ == '__main__': main()


