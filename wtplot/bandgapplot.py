
"""
Usage:
    bandgapplot.py <wt_in> [<gap_dat>...] [-x <xlim>] [-y <ylim>] [-z <zlim>] [-e <Enelim>] [-c <gap_cutoff>] [-m <markersize>]
    bandgapplot.py <wt_in> [<gap_dat>...] [--bz] [-e <Enelim>] [-c <gap_cutoff>] [-m <markersize>]

Options:
    <wt_in>             wtのinput
    <gap_dat>           wtで計算したbandgapのdatfile
    --bz                brillanzone内を埋め尽くすように表示
    -x <xlim>           x座標の範囲, k点を複製し領域を埋め尽くすように表示
    -y <ylim>           y座標の範囲, k点を複製し領域を埋め尽くすように表示
    -z <zlim>           z座標の範囲, k点を複製し領域を埋め尽くすように表示
    -e <Enelim>         gapの存在するEnergyの範囲, min,maxで指定  [default: -100,100 ]
    -c <gap_cutoff>     Energy gapのcutoff  [default: 0.02]
    -m <markersize>     データ点のsize  [default: 2]

"""
from docopt import docopt
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import BZplot as Bp
import plottool as pt

pt.mpl_init()

def read_gapdat(file_gapdat, enelim, gap_cutoff):
    df=pd.read_table(file_gapdat, header=None, skiprows=1, \
                     delim_whitespace = True, \
                     names=["kx", "ky", "kz", "gap", "Ev", "Ec", "k1", \
                            "k2", "k3"], dtype='f8'
    )

    df=df[ df['gap'] <= gap_cutoff ]
    df=df[ df['Ev'] >= enelim[0] ]
    df=df[ df['Ev'] <= enelim[1] ]

    k=[ df["{}".format(kn)].to_list() for kn in ["kx", "ky", "kz"] ]
    Ene=df["Ev"].to_list()
    return k, Ene

def convertinBZ(k: np.ndarray, kcell):
    #与えられたk点とそれの逆格子ベクトルだけ平行移動したk点のノルムを比較し、
    #もし後者の方が小さければk点座標を置き換える。
    #これにより与えられたk点をBZ内の等価なk点に変換する。
    newk = k.copy()
    for i in range(len(k[0])):
        kp = k[:, i].copy()
        kabs = np.linalg.norm(kp)
        for lv in kcell :
            for sgn in [-1, 1] :
                newkp = kp + sgn * lv
                if kabs > np.linalg.norm(newkp) :
                    for j in range(3): newk[j][i] = newkp[j]
                    kabs = np.linalg.norm(newkp)
    return newk

def copyKpoints(K: np.ndarray, kcell: np.ndarray, shift_num, E=[]):
    #与えられたk点を逆格子分だけずらして複製する
    #複製する範囲はmeshgridで決まる.
    #shiftnum: k点を逆格子±n個分だけずらす
    x = np.arange(-1*shift_num, shift_num+1, 1)
    y = np.arange(-1*shift_num, shift_num+1, 1)
    z = np.arange(-1*shift_num, shift_num+1, 1)

    m = np.array(np.meshgrid(x, y, z))
    m = m.reshape([3,-1]).T

    K = K.T
    for i, x in enumerate(m):
        if i == 0: newK = K - np.matmul(x, kcell)
        newK = np.append(newK, K - np.matmul(x, kcell)).reshape([-1, 3])
        if len(E) == len(K):
            if i == 0: newE = E.copy()
            newE = np.append(newE, E)
        if i == 1: print(newK)
    return newK.T, newE

def Klimit(K, E, kcell, xlim, ylim, zlim):
    #与えられたk点とそれの逆格子ベクトルだけ平行移動した等価なk点をlistに入れ、
    #そのlist内で
    K, E = copyKpoints(K, kcell, 2, E=E)
    newK, newE = [], []
    for kp, ene in zip(K.T, E):
        if ( xlim[0] <= kp[0] <= xlim[1] ) and \
           ( ylim[0] <= kp[1] <= ylim[1] ) and \
           ( zlim[0] <= kp[2] <= zlim[1] ) :
            newK.append(kp)
            newE.append(ene)
    return np.array(newK).T, np.array(newE)

def plot_gapdat(ax, fig, k, Ene, markerSize):
    cm = plt.cm.get_cmap('RdYlBu')
    mappable=ax.scatter(k[0], k[1], k[2], c=Ene, cmap=cm, s=markerSize)
    fig.colorbar(mappable, ax=ax)

def main():
    args = docopt(__doc__)

    markersize = float(args['-m'])
    enelim = [ float(e) for e in args['-e'].split(',')]
    gap_cutoff = float(args['-c'])

    K, Ene = [[], [], []], []
    for gap_dat in args['<gap_dat>']:
        kn, En = read_gapdat(gap_dat, enelim, gap_cutoff)
        for i in range(3): K[i] = K[i] + kn[i]
        Ene = Ene + En

    #----- BZのplot -----#
    fig = plt.figure(figsize=(pt.cminch(32),pt.cminch(20)))
    ax = fig.add_axes([ 0.05, 0.1, 1, 0.9], projection='3d')

    bz = Bp.BZ_input(args['<wt_in>'])
    Bp.BZ_plot(ax, bz.kcell)

    #----- 表示範囲に合わせてk点を複製 -----#
    if args['--bz'] == True :
        K = convertinBZ(np.array(K), bz.kcell)
    else :
        if args['-x'] is not None or args['-y'] is not None \
        or args['-z'] is not None:
            if args['-x'] is not None:
                xlim = np.array(args['-x'].split(','), dtype='f8')
            else: xlim = [ min(K[0]), max(K[0]) ]
            if args['-y'] is not None:
                ylim = np.array(args['-y'].split(','), dtype='f8')
            else: ylim = [ min(K[1]), max(K[1]) ]
            if args['-z'] is not None:
                zlim = np.array(args['-z'].split(','), dtype='f8')
            else: zlim = [ min(K[2]), max(K[2]) ]
            K, Ene = Klimit(np.array(K), np.array(Ene), bz.kcell, xlim, ylim, zlim)

    plot_gapdat(ax, fig, K, Ene, markersize)
    ax.set_box_aspect((1,1,1))
    plt.show()

if __name__=='__main__': main()


