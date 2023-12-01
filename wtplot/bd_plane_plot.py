"""
Usage:
    bd_plane_plot.py <file_dat> [-n <row>]

Options:
    <file_dat>       datfile
    -n <row>         表示するband番号
"""

from docopt import docopt
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import plottool as pt
pt.mpl_init()
NumOcEne_row = 6


def read_bulkek_plane_dat(file_bp_dat):
    with open(file_bp_dat, 'r') as fbd:
        lines = [ l.split() for l in fbd.readlines()[1:] ] 

    #空白行までの行数を数えることでmeshを調べる
    for i, line in enumerate(lines):
        if len(line) < 1: 
            mesh = [ len(lines[:i]) ]
            break
    lines = np.array([ l for l in lines if len(l) > 1 ])

    #直交するmeshは全体のline数から割ることで求める
    mesh.append( int(len(lines)/mesh[0]) )

    kp = [ [ float(x) for x in line[:3] ] for line in lines ]
    Ene = [ [ float(x) for x in lines[:, i] ] for i in range(6,10) ]
    return np.array(kp), np.array(Ene), mesh

def kp_trans(kp):
    return np.array([ [ k[0], k[1] ] for k in kp ])

def sfplot(ax, kp, Ene, mesh, Emax=0.3, Emin=-0.3):
    #ここでのkpは2成分のみ。
    #datの3次元のkpから平面の座標に変換し、そのkpをここに入れる

    x0=np.reshape(kp[:, 0], (mesh[0], mesh[1]))
    y0=np.reshape(kp[:, 1], (mesh[0], mesh[1]))
    E0=np.reshape(Ene, (mesh[0], mesh[1]))

    xmax = x0.max()
    xmin = x0.min()
    ymax = y0.max()
    ymin = y0.min()
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_zlim([Emin, Emax])
    ax.set_box_aspect((1, (ymax-ymin)/(xmax-xmin), 1))

    x = x0[(x0[:, 0] > xmin) & (x0[:, 0] < xmax),:]
    x = x[:,(y0[0] > ymin) & (y0[0] < ymax)]
    y = y0[(x0[:, 0] > xmin) & (x0[:, 0] < xmax),:]
    y = y[:,(y0[0] > ymin) & (y0[0] < ymax)]
    E = E0[(x0[:, 0] > xmin) & (x0[:, 0] < xmax),:]
    E = E[:,(y0[0] > ymin) & (y0[0] < ymax)]
    E = np.clip(E, Emin, Emax)
    ax.plot_surface(x, y, E, alpha=0.4)

if __name__ == '__main__':
    args = docopt(__doc__)
    print(args)
    kp, Ene, mesh= read_bulkek_plane_dat(args['<file_dat>'])
    kp = kp_trans(kp)

    #--- figとaxesの作成 ---#
    fig = plt.figure(figsize=(pt.cminch(20),pt.cminch(18)))

    ax = fig.add_axes([ 0.05, 0.05, 0.9, 0.9], projection='3d')
    if args['-n'] is not None: bn = [ int(n) + 1 for n in args['-n'].split(',')]
    else : bn = range(0, 4)
    for n in bn:
        sfplot(ax, kp, Ene[n], mesh)

    plt.show()
