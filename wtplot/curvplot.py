
"""
Usage:
    curvplot.py <file_curv_dat> <axis> [-r <curv_row>] [-c <clim>] [-n <nmax>]
    curvplot.py <file_curv_dat> 2d <axis> [-r <curv_row>] [-c <clim>] [-n <nmax>]
    curvplot.py <file_curv_dat> 3d [-r <curv_row>] [-c <clim>]

Options:
    <file_curv_dat> datfile
    <axis>          これを指定すると2Dの等高線を出力, 高さは指定した軸のcurvの値
    2d              これを指定すると2Dのvectorを表示
    3d              これを指定すると3Dのvectorを表示
    -r <curv_row>   curv_datのcurvの行数 [default: 6-9]
    -c <clim>       colorbarの範囲
    -n <nmax>       normの最大値
"""

from docopt import docopt
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D

import plottool as pt
pt.mpl_init()

def read_curv_dat(file_curv_dat, curv_row):
    with open(file_curv_dat, 'r') as fcd:
        lines = [ l.split() for l in fcd.readlines()[4:] ]
    lines = np.array([ l for l in lines if len(l) > 1 ])

    kp = np.array([ [ float(x) for x in line[:3] ] for line in lines ])
    curv = np.array([ [ float(x) for x in line[curv_row[0]:curv_row[1]] ] for line in lines ])
    return kp, curv

def kp_trans(kp):
    return np.array([ [ k[0], k[1] ] for k in kp ])

def curv_3dvec_plot(ax, fig, kp, curv):
    #ここでのkpは2成分のみ。
    #datの3次元のkpから平面の座標に変換し、そのkpをここに入れる
    xmax = kp[:, 0].max()
    xmin = kp[:, 0].min()
    ymax = kp[:, 1].max()
    ymin = kp[:, 1].min()
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_zlim([-(xmax-xmin)/2, (xmax-xmin)/2])
    ax.set_box_aspect((1, (ymax-ymin)/(xmax-xmin), 1))
    cm = mpl.colormaps['viridis_r']
    cmax = 5
    cmin = 1
    nmax = 100
    default_lt = (xmax-xmin) / (nmax*10)
    for i, cv in enumerate(curv):
        if i%5 != 0: continue
        if int(i/101)%5 != 0: continue
        norm = np.linalg.norm(cv)
        if norm > nmax: lt = (nmax / np.linalg.norm(cv)) * default_lt
        else: lt = default_lt

        if norm > cmax: c=cm(1.0) 
        elif norm < cmin: c=cm(0.0)
        else: c = cm( ((norm-cmin)/(cmax-cmin))*0.9 + 0.1 )


        #print(k[0], k[1], 0, curv[i][0], curv[i][1], curv[i][2])
        ax.quiver(kp[i][0], kp[i][1], 0, cv[0], cv[1], cv[2], lw=1.5, \
                  arrow_length_ratio = 0.4, length = lt, color = c)

    mappable = mpl.cm.ScalarMappable(Normalize(cmin, cmax), cm)
    pp = fig.colorbar(mappable, ax=ax, orientation="vertical")
    #pp.set_clim(-4,4)
    #pp.set_label(“color bar“, fontname="Arial", fontsize=10)


def curv_2dh_plot(ax, fig, kp, curv, clim):
    xmax = kp[:, 0].max()
    xmin = kp[:, 0].min()
    ymax = kp[:, 1].max()
    ymin = kp[:, 1].min()
    ax.set_aspect((ymax-ymin)/(xmax-xmin))
    kx = kp[:, 0].reshape(101, 101)
    ky = kp[:, 1].reshape(101, 101)
    cv = curv.reshape(101, 101)
    cm = mpl.colormaps['viridis']
#    ax.pcolor(kx, ky, cv, vmin=0.5, vmax=3, shading="nearest")
    ax.pcolormesh(kx, ky, cv, vmin=clim[0], vmax=clim[1], \
                        shading='gouraud', cmap=cm)
    mappable = mpl.cm.ScalarMappable(Normalize(clim[0], clim[1]), cm)
    pp = fig.colorbar(mappable, ax=ax, orientation="vertical")

def main():
    args = docopt(__doc__)
    print(args)
    curv_row = [ int(x) for x in args['-r'].split('-') ]

    kp, curv = read_curv_dat(args['<file_curv_dat>'], curv_row)

    if args['3d'] == True:
        #--- figとaxesの作成 ---#
        fig = plt.figure(figsize=(pt.cminch(20), pt.cminch(18)))
        ax = fig.add_axes([ 0.05, 0.05, 0.9, 0.9 ], projection='3d')

        curv_3dvec_plot(ax, fig, kp, curv)
        plt.show()

    elif args['2d'] == True and args['<axis>'] is not None:
        ncurv, nkp = [], []
        for i in range(len(curv)):
            if i%5 != 0: continue
            if int(i/101)%5 != 0: continue
            ncurv.append(curv[i])
            nkp.append(kp[i])
        kp = kp_trans(nkp)
        axisrow = {'x':[1, 2], 'y':[0, 2], 'z':[0, 1]}
        cv = np.array([ [ c[r] for r in axisrow[args['<axis>']] ] for c in ncurv ])
        cvalue = [ np.linalg.norm(v) for v in cv ]


        fig, ax = pt.MakeAxesTable([1], [1], width=18, height=20, margin=2)

        if args['-c'] is not None:
            climpfx=", clim="
            clim = [ float(c) for c in args['-c'].split(',')]
        else: climpfx, clim = "", ""
        if args['-n'] is not None:
            nmaxpfx=", nmax="
            nmax = float(args['-n'])
        else: nmaxpfx, nmax = "", ""

        cb = eval("pt.vec2dplot(ax[0][0], kp, cv, cvalue=cvalue{}{}{}{})".format(climpfx, clim, nmaxpfx, nmax))
        pp = fig.colorbar(cb, ax=ax[0][0], orientation="vertical")

        plt.show()

    elif args['<axis>'] is not None:
        kp = kp_trans(kp)
        axisrow = {'x':0, 'y':1, 'z':2}
        cv = curv[:, axisrow[args['<axis>']]]
        fig, ax = pt.MakeAxesTable([1], [1], width=18, height=20, margin=2)
        if args['-c'] is not None:
            clim = [ float(c) for c in args['-c'].split(',')]
        else: clim = [ cv.min(), cv.max() ]
        curv_2dh_plot(ax[0][0], fig, kp, cv, clim)

        plt.show()

if __name__ == '__main__': main()


