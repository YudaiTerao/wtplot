
"""
Usage:
    ancplot.py <anc_dat> [-t <T>] [-r] [-n|--noahc]

Options:
    <anc_dat>           wtで計算したancのfile
    -t <desplayT>       表示する温度の指定(指定しないとすべて表示)
    -r                  ahcの値の正負を反転する
    -n --noahc          ahcをplotしない
"""

from docopt import docopt
import numpy as np
from matplotlib import pyplot as plt
import plottool as pt

pt.mpl_init()

def read_anc_dat(file_anc_dat, rv):
    #ancdatは1列目Ene, 2列目AHC, 3列目以降ANC
    with open(file_anc_dat, 'r') as f_anc_dat:
        index = f_anc_dat.readline().split()
        lines = np.array([ l.split() for l in f_anc_dat.readlines() ], dtype=float)
    T = [ float(ix.replace("anc-", "")) for ix in index[2:] ]
    Ene = lines[:, 0]
    if rv : AHC = lines[:, 1] * -1
    else  : AHC = lines[:, 1]
    ANC = { tp: lines[:, i+2] for i, tp in enumerate(T) }
    return Ene, AHC, ANC, T, index

def main():
    args = docopt(__doc__)
    Ene, AHC, ANC, T, index = read_anc_dat(args['<anc_dat>'], args['-r'])

    ### 表示するgraph数のカウント ###
    if args['-t'] is not None: 
        dpT = args['-t'].split()
        graphnum = len(dpT)
    else :
        dpT = T.copy()
        graphnum = len(T)
    if args['--noahc'] != True : graphnum = graphnum + 1

    ##########

    ### graph数に応じて横幅や余白等を決める ###
    if graphnum == 1 :   wn, hn, w, h, m, ts, ls = [1], [1], 18, 20, 2.0, 18, 24
    elif graphnum <= 2 : wn, hn, w, h, m, ts, ls = [1, 1], [1], 30, 20, 2.5, 18, 24
    elif graphnum <= 4 : wn, hn, w, h, m, ts, ls = [1, 1], [1, 1], 30, 20, 2.5, 15, 20
    elif graphnum <= 6 : wn, hn, w, h, m, ts, ls = [1, 1, 1], [1, 1], 30, 20, 2.2, 12, 16

    ##########

    fig, ax = pt.MakeAxesTable(wn, hn, width=w, height=h, margin=m)

    for r, axr in enumerate(ax):
        for c, axc in enumerate(axr):
            i = c + r * len(ax[0])
            if i >= graphnum : break

            ### AHC or ANCのplot ###
            if args['--noahc'] != True : 
                if i == 0 : 
                    pt.AHCplot(axc, Ene, AHC)
                    title = index[1]
                else : j = i - 1
            else : j = i
            pt.ANCplot(axc, Ene, ANC[dyT[j]])

            # plot config
            title = index[2:][j]
            axc.tick_params('x', labelsize=ts)
            axc.tick_params('y', labelsize=ts)
            axc.xaxis.label.set_size(ls)
            axc.yaxis.label.set_size(ls)
            axc.annotate(title, (0.5, 1.01), xycoords='axes fraction', fontsize=ls, va='bottom', ha='center')
    plt.show()
            ##########

if __name__ == '__main__': main()

