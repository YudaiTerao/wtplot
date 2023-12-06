
from setuptools import setup, find_packages

setup(
    name="wtplot",
    version="0.2.0",
    author="Yudai Terao",
    packages=find_packages(),
    install_requires=[
        'plottool@git+https://github.com/YudaiTerao/plottool.git',
        'BZplot@git+https://github.com/YudaiTerao/BZplot.git'
    ],
    entry_points={
        'console_scripts':[
            'ahc     = wtplot.ahcplot:main',
            'anc     = wtplot.ancplot:main',
            'anccalc = wtplot.anccalc:main',
            'curv    = wtplot.curvplot:main',
            'bdgap   = wtplot.bandgapplot:main',
            'bdplane = wtplot.band_plane_plot:main',
        ],
    },
)

