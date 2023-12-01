
"""
Usage:
    bandgapplot.py <wt_in> [<gap_dat>...] [-e <Enelim>] [-c <gap_cutoff>] [-m <markersize>] [-l <lim>] [--bz]

Options:
    <wt_in>             wtのinput
    <gap_dat>           wtで計算したbandgapのdatfile
    -m <markersize>     データ点のsize  [default: 2]
    -c <gap_cutoff>     Energy gapのcutoff  [default: 0.02]
    -x <xlim>
    -y <ylim>
    -z <zlim>
    -e <Enelim>         Energyの範囲, min,maxで指定  [default: -100,100 ]

    -l <lim>            データ点の範囲, 範囲内を埋め尽くすように表示, -1,1/-1.3,1,3/-2,2 のように指定
    --bz                 brillanzone内を埋め尽くすように表示
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
                     names=["kx", "ky", "kz", "gap", "Ev", "Ec", "k1", "k2", "k3"], \
                     dtype={"kx" :np.float32, "ky":np.float32, "kz":np.float32, \
                            "gap":np.float32, "Ev":np.float32, "Ec":np.float32, \
                            "k1" :np.float32, "k2":np.float32, "k3":np.float32 } \
    )

    df=df[ df['gap'] <= gap_cutoff ]
    df=df[ df['Ev'] >= enelim[0] ]
    df=df[ df['Ev'] <= enelim[1] ]

    k=[ df["{}".format(kn)].to_list() for kn in ["kx", "ky", "kz"] ]
    Ene=df["Ev"].to_list()
    return k, Ene

def plot_gapdat(ax, fig, k, Ene, markerSize):
    cm = plt.cm.get_cmap('RdYlBu')
    mappable=ax.scatter(k[0], k[1], k[2], c=Ene, cmap=cm, s=markerSize)
    fig.colorbar(mappable, ax=ax)

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

def Klimit(k, E, kcell, xlim, ylim, zlim):
    #与えられたk点とそれの逆格子ベクトルだけ平行移動した等価なk点をlistに入れ、
    #そのlist内で
    newk, Ene = [], []
    for i in range(len(k[0])):
        newkp = k[:, i].copy()
        for lv in kcell :
            for sgn in [-1, 1] :
                newkp = np.append(newkp, newkp[:3] + sgn * lv)
                for lv2 in kcell :
                    if ( lv == lv2 ).all() : continue
                    for sgn2 in [-1, 1] :
                        newkp = np.append(newkp, newkp[:3] + sgn * lv + sgn2 * lv2)
        newkp = newkp.reshape(-1,3)
        for nkp in newkp :
            if ( xlim[0] <= nkp[0] <= xlim[1] ) and \
               ( ylim[0] <= nkp[1] <= ylim[1] ) and \
               ( zlim[0] <= nkp[2] <= zlim[1] ) :
                newk.append(nkp)
                Ene.append(E[i])
    newk = np.array(newk)
    return [ newk[:, 0], newk[:, 1], newk [:, 2] ], Ene



def main():
    args = docopt(__doc__)
    markersize = float(args['-m'])

    fig = plt.figure(figsize=(pt.cminch(32),pt.cminch(20)))
    ax = fig.add_axes([ 0.05, 0.1, 1, 0.9], projection='3d')

    bz = Bp.BZ_input(args['<wt_in>'])
    Bp.BZ_plot(ax, bz.kcell)
#    Bp.kpath_plot(ax, bz.kpath, bz.kpath_name)
#    Bp.lcvec_plot(ax, bz.kcell)

    enelim = [ float(e) for e in args['-e'].split(',')]
    gap_cutoff = float(args['-c'])
    K, Ene = [[], [], []], []
    for gap_dat in args['<gap_dat>']:
        kn, En = read_gapdat(gap_dat, enelim, gap_cutoff)
        for i in range(3): K[i] = K[i] + kn[i]
        Ene = Ene + En

    if args['--bz'] == True :
        K = convertinBZ(np.array(K), bz.kcell)
    else :
        if args['-l'] is not None : 
            lim = args['-l'].split('/')
            xlim = [ float(x) for x in lim[0].split(',') ]
            ylim = [ float(y) for y in lim[1].split(',') ]
            zlim = [ float(z) for z in lim[2].split(',') ]
            K, Ene = Klimit(np.array(K), np.array(Ene), bz.kcell, xlim, ylim, zlim)
    plot_gapdat(ax, fig, K, Ene, markersize)

    ax.set_box_aspect((1,1,1))
    plt.show()

if __name__=='__main__': main()

