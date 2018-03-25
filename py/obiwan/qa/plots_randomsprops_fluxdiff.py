import matplotlib
matplotlib.use('Agg') # display backend
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
from scipy.stats import norm
from scipy.optimize import leastsq
from argparse import ArgumentParser

from astrometry.util.fits import fits_table, merge_tables

import obiwan.qa.plots_common as plots

plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

#######################
parser = ArgumentParser(description='DECaLS simulations.')
parser.add_argument('--randoms_table', required=True)
parser.add_argument('--which', choices=['cosmos','eboss','desi'],required=True)
args = parser.parse_args()

dat= fits_table(args.randoms_table)

fracin= np.mean(np.array([dat.tractor_fracin_g,
                          dat.tractor_fracin_r,
                          dat.tractor_fracin_z]),axis=0)
isRec= (dat.obiwan_mask == 1) #& (fracin > 0.7)

rz= dat.psql_r - dat.psql_z
gr= dat.psql_g - dat.psql_r
mags={}
for band in 'grz':
    mags[band]= plots.flux2mag(dat.get('tractor_flux_'+band)/\
                                 dat.get('tractor_mw_transmission_'+band))

if args.which == 'eboss':
    is_elg_input= plots.eboss_ts(dat.psql_g,rz,gr,region='ngc')
    is_elg_trac= plots.eboss_ts(mags['g'],mags['r']-mags['z'],mags['g']-mags['r'],region='ngc')
#elif args.which == 'desi':
#    is_elg_input= plots.desi_ts(dat.psql_g,rz,gr)
#    is_elg_trac= plots.desi_ts(mags['g'],mags['r']-mags['z'],mags['g']-mags['r'])
##########################


def myhist(ax,data,bins=20,color='b',normed=False,lw=2,ls='solid',label=None,
           range=None, return_h=False,alpha=1):
    kw= dict(bins=bins,color=color,normed=normed,
             histtype='step',range=range,lw=lw,ls=ls,alpha=1)
    if label:
        kw.update(label=label)
    h,bins,_=ax.hist(data,**kw)
    if return_h:
        return h

def my_step(ax,bins,height,
            lw=2,color='b',ls='solid',label=None):
    """if plt.hist returns tuple (height,bins) then this reproces that plot.
    
    e.g. bin centers and horizontal lines at the right place...
    """
    kw= dict(color=color,lw=lw,ls=ls)
    if label:
        kw.update(label=label)
    ax.step(bins[:-1],height,where='mid',**kw)

def mytext(ax,x,y,text, ha='left',va='center',fontsize=20,rotation=0,
           color='k',dataCoords=False):
    '''adds text in x,y units of fraction axis'''
    if dataCoords:
        ax.text(x,y,text, horizontalalignment=ha,verticalalignment=va,
                fontsize=fontsize,rotation=rotation,color=color)
    else:
        ax.text(x,y,text, horizontalalignment=ha,verticalalignment=va,
                fontsize=fontsize,rotation=rotation,color=color,
                transform=ax.transAxes)

class getDepth(object):
    def __init__(self):
        self.desi= dict(g=24.0,
                        r=23.4,
                        z=22.5)
        self.eboss_ngc= dict(g=22.9,
                             r=self.desi['r'],
                             z=self.desi['z'])
        self.eboss_sgc= dict(g=22.825,
                             r=self.desi['r'],
                             z=self.desi['z'])

def grz_hist_input_noise_ext(dat,fn='grz_hist_input_noise_ext.png',
                             glim=None,rlim=None,zlim=None):
    fig,axes=plt.subplots(3,1,figsize=(5,12))
    plt.subplots_adjust(hspace=0.1,wspace=0.2)
    xlim= dict(g=glim,
               r=rlim,
               z=zlim)

    kw_hist= dict(normed=False)
    for ax,band in zip(axes,'grz'):
        flux=dict(input_noise_ext= dat.get(band+'flux'),
                  intput_noise= dat.get(band+'flux')/\
                              dat.get('mw_transmission_'+band),
                  input= plots.mag2flux(dat.get('psql_'+band))
                 )
        bins= np.linspace(xlim[band][0],xlim[band][1],num=30)
        for key,color in zip(sorted(list(flux.keys()),key=lambda x:len(x)),
                             'bgk'):
            mag= plots.flux2mag(flux[key])
            myhist(ax,mag,bins=bins,range=xlim[band],
                   color=color,label=key,**kw_hist)
        plots.mytext(ax,0.5,0.05,band,fontsize=14)
        ylab=ax.set_ylabel('Number')
        
    xlab=axes[-1].set_xlabel('True AB mag')
    leg=axes[0].legend(loc=(0,1.01),ncol=3)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def grz_hist_input_ext(dat,fn='grz_hist_input_ext.png',
                       glim=None,rlim=None,zlim=None):
    fig,axes=plt.subplots(3,1,figsize=(5,12))
    plt.subplots_adjust(hspace=0.1,wspace=0.2)
    xlim= dict(g=glim,
               r=rlim,
               z=zlim)

    kw_hist= dict(normed=False)
    for ax,band in zip(axes,'grz'):
        flux=dict(input_ext= dat.get(band+'flux'),
                  input= dat.get(band+'flux')/\
                              dat.get('mw_transmission_'+band))
        bins= np.linspace(xlim[band][0],xlim[band][1],num=30)
        for key,color in zip(sorted(list(flux.keys()),key=lambda x:len(x)),
                             'bgk'):
            mag= plots.flux2mag(flux[key])
            myhist(ax,mag,bins=bins,range=xlim[band],
                   color=color,label=key.replace('_','+'),**kw_hist)
        plots.mytext(ax,0.5,0.05,band,fontsize=14)
        ylab=ax.set_ylabel('Number')
        
    xlab=axes[-1].set_xlabel('True AB mag')
    leg=axes[0].legend(loc=(0,1.01),ncol=2)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def grz_hist_input_rec(dat,fn='grz_hist_input_rec.png',
                       glim=(21.5,23.25),rlim=(21.5,23.25),zlim=(19.5,22.5)):
    fig,axes=plt.subplots(3,1,figsize=(5,12))
    plt.subplots_adjust(hspace=0.2,wspace=0.2)
    xlim= dict(g=glim,
               r=rlim,
               z=zlim)

    kw_hist= dict(normed=False)
    for ax,band in zip(axes,'grz'):
        mag= plots.flux2mag(dat.get(band+'flux')/\
                                dat.get('mw_transmission_'+band))
        bins=np.linspace(xlim[band][0],xlim[band][1],num=30)
        myhist(ax,mag,bins=bins,
               color='b',label='input',**kw_hist)
        myhist(ax,mag[isRec],bins=bins,
               color='g',label='recovered',**kw_hist)
        xlab=ax.set_xlabel('True mag %s' % band)
        ylab=ax.set_ylabel('Number')
        
    leg=axes[0].legend(loc=(0,1.01),ncol=2)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def grz_hist_by_type(dat,fn='grz_hist_by_type.png',x_ivar=0,
                     glim=(21.6,23),rlim=(20.75,22.5),zlim=(19.5,22)):

    x_ivar=0
    x_var= ['true_mag','galdepth','redshift'][x_ivar]
    types= np.char.strip(dat.get('tractor_type'))

    kw_hist=dict(bins=30,normed=True)

    figs,axes= plt.subplots(3,1,figsize=(6,9))
    plt.subplots_adjust(hspace=0.3)

    ratio_area= 1. 
    xlim= dict(g=glim,
               r=rlim,
               z=zlim)
    for ax,band in zip(axes,'grz'):
        if x_var == 'true_mag':
            _x_var= plots.flux2mag(dat.get(band+'flux')/\
                                   dat.get('mw_transmission_'+band))
            xlab= '%s (true mag)' % band
        elif x_var == 'galdepth':
            flux_for_depth= 5 / np.sqrt(dat.get('tractor_galdepth_'+band))
            _x_var= plots.flux2mag(flux_for_depth/\
                                     dat.get('mw_transmission_'+band))
            xlab= 'galdepth %s' % band
        elif x_var == 'redshift':
            _x_var= dat.psql_redshift
            xlab= 'redshift'
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])
        for typ,color in zip(['SIMP','EXP','DEV','PSF'],'bgmc'):
            keep= (isRec) & (types == typ)
            if len(_x_var[keep]) > 0:
                myhist(ax,_x_var[keep],color=color,label=typ,range=xlim[band],**kw_hist)
        ylab='Number'
        if kw_hist['normed']:
            ylab='PDF'
        ylabel=ax.set_ylabel(ylab)
        xlabel=ax.set_xlabel(xlab)
    axes[0].legend(loc='upper left',ncol=1,fontsize=10)
    plt.savefig(fn,bbox_extra_artists=[xlabel,ylabel], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def grz_hist_by_type2(dat,fn='grz_hist_by_type2.png',x_ivar=0,
                      glim=(21.6,23),rlim=(20.75,22.5),zlim=(19.5,22)):

    x_ivar=0
    x_var= ['true_mag','galdepth','redshift'][x_ivar]
    types= np.char.strip(dat.get('tractor_type'))

    kw_hist=dict(bins=30,normed=True)

    figs,axes= plt.subplots(3,2,figsize=(10,9))
    plt.subplots_adjust(hspace=0.3)

    ratio_area= 1. 
    xlim= dict(g=glim,
               r=rlim,
               z=zlim)
    ylim= dict(g=(0,3.7),
               r=(0,2.3),
               z=(0,1.5))
    for row,band in zip(range(3),'grz'):
        if x_var == 'true_mag':
            _x_var= plots.flux2mag(dat.get(band+'flux')/\
                                   dat.get('mw_transmission_'+band))
            xlab= '%s (true mag)' % band
        elif x_var == 'galdepth':
            flux_for_depth= 5 / np.sqrt(dat.get('tractor_galdepth_'+band))
            _x_var= plots.flux2mag(flux_for_depth/\
                                     dat.get('mw_transmission_'+band))
            xlab= 'galdepth %s' % band
        elif x_var == 'redshift':
            _x_var= dat.psql_redshift
            xlab= 'redshift'
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])
        for col,use_types,colors in zip(range(2),[['EXP','DEV','SIMP'],
                                                  ['SIMP','PSF','EXP']],['bgm','mcb']):
            xlabel=axes[row,col].set_xlabel(xlab)
            for typ,color in zip(use_types,colors):
                keep= (isRec) & (types == typ)
                if len(_x_var[keep]) > 0:
                    if (col == 1 and typ == 'EXP') or (col == 0 and typ == 'SIMP'):
                        #alpha= 0.25
                        lw= 0.5
                    else:
                        lw=2
                    kw_hist.update(lw=lw) #alpha=alpha)
                    myhist(axes[row,col],_x_var[keep],color=color,label=typ,range=xlim[band],**kw_hist)

        ylab='Number'
        if kw_hist['normed']:
            ylab='PDF'
        ylabel=axes[row,0].set_ylabel(ylab)
    for col in range(2):
        axes[0,col].legend(loc='upper left',ncol=1,fontsize=10)
    for row,band in zip(range(3),'grz'):
        for col in range(2):
            axes[row,col].set_xlim(xlim[band])
            axes[row,col].set_ylim(ylim[band])
    plt.savefig(fn,bbox_extra_artists=[xlabel,ylabel], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def noise_added_1(dat,fn='noise_added_1.png'):
    fig,ax=plt.subplots()

    kw_hist= dict(bins=10,normed=False)
    ylim=2e-15
    for band,color in zip('grz','gbm'):
        flux= plots.mag2flux(dat.get('psql_'+band))
        flux_noise= dat.get(band+'flux')/\
                        dat.get('mw_transmission_'+band)
        myhist(ax,flux_noise-flux,range=(-ylim,ylim),color=color,
               label=band,**kw_hist)
        ylab=ax.set_ylabel('Number')
        xlab=ax.set_xlabel('dflux (input - db)')
    ax.legend()   
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def noise_added_2(dat,fn='noise_added_2.png'):
    xlim= dict(g=(21.5,23.25),
               r=(20.5,23),
               z=(19.5,22.5))

    fig,axes=plt.subplots(3,1,figsize=(5,8))
    plt.subplots_adjust(hspace=0.2)
    kw_hist= dict(color='b',bins=30,normed=False)
    ylim=2e-15
    for ax,band in zip(axes,'grz'):
        flux= plots.mag2flux(dat.get('psql_'+band))
        flux_noise= dat.get(band+'flux')/\
                        dat.get('mw_transmission_'+band)
        ax.scatter(plots.flux2mag(flux_noise),flux_noise-flux,color='b')
        ax.set_ylim(-ylim,ylim)
        xlab=ax.set_xlabel(band+' mag')
        ylab=ax.set_ylabel('dflux (input - db)')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def delta_dec_vs_delta_ra(dat,fn='delta_dec_vs_delta_ra.png',
                          xlim=(-1,1),ylim=(-1,1),nbins=(30,30)):
    fig,ax= plt.subplots() #figsize=(8, 5))
    plots.myhist2D(ax,(dat.ra[isRec] - dat.tractor_ra[isRec])*3600,
                      (dat.dec[isRec] - dat.tractor_dec[isRec])*3600,
                   xlim=xlim,ylim=ylim,nbins=nbins)
    ax.axhline(0,c='k',ls='--')
    ax.axvline(0,c='k',ls='--')
    #plt.ylim(-1.2,1.2)
    #plt.xlim(-1.2,1.2)
    xlab=plt.xlabel(r'$\Delta \, RA$ arcsec (truth - measured)')
    ylab=plt.ylabel(r'$\Delta \, Dec$ arcsec (truth - measured)')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def number_per_type_input_rec_meas(dat,fn='number_per_type_input_rec_meas.png'):
    types= np.char.strip(dat.get('tractor_type'))
    types[pd.Series(types).isin(['SIMP','REX']).values]= 'EXP'
    use_types= ['PSF','EXP','DEV','COMP']

    #number input, recovered,...
    injected= [0,len(dat[dat.n == 1]),len(dat[dat.n == 4]),0]
    recovered= [0,len(dat[(isRec) & (dat.n == 1)]),
                      len(dat[(isRec) & (dat.n == 4)]),0]
    tractor= [len(dat[(isRec) & (types == typ)])
                   for typ in use_types]

    df= pd.DataFrame(dict(type=use_types,
                          injected=injected,
                          recovered=recovered,
                          tractor=tractor))
    df.set_index('type',inplace=True)

    fig,ax= plt.subplots(figsize=(8, 5))
    df.plot.barh(ax=ax)
    xlab=ax.set_xlabel('Number')
    ylab=ax.set_ylabel('type')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def confusion_matrix_by_type(dat,fn='confusion_matrix_by_type.png'):
    use_types= ['PSF','EXP','DEV','COMP']
    trac_types= np.char.strip(dat.get('tractor_type'))
    trac_types[pd.Series(trac_types).isin(['SIMP','REX']).values]= 'EXP'
    input_types= np.array(['EXP']*len(dat))
    input_types[(isRec) & (dat.n == 4)]= 'DEV'
    cm= plots.create_confusion_matrix(input_types[isRec],trac_types[isRec], 
                                      poss_types=use_types)

    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues, vmin=0,vmax=1)
    cbar=plt.colorbar()
    plt.xticks(range(len(use_types)), use_types)
    plt.yticks(range(len(use_types)), use_types)
    ylab=plt.ylabel('Truth')
    xlab=plt.xlabel('Tractor')
    for row in range(len(use_types)):
        for col in range(len(use_types)):
            if np.isnan(cm[row,col]):
                plt.text(col,row,'n/a',va='center',ha='center')
            elif cm[row,col] > 0.5:
                plt.text(col,row,'%.2f' % cm[row,col],va='center',ha='center',color='yellow')
            else:
                plt.text(col,row,'%.2f' % cm[row,col],va='center',ha='center',color='black')
    plt.savefig(fn, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close()
    print('Wrote %s' % fn)

def hist_true_rhalf_by_type(dat,fn='hist_true_rhalf_by_type'):
    use_types= ['SIMP','EXP','DEV','PSF']
    types= np.char.strip(dat.get('tractor_type'))
   
    ylims= (0,7) 
    figs,ax= plt.subplots(3,1,figsize=(4,9))
    plt.subplots_adjust(hspace=0.2)

    bins= np.linspace(0,2,num=30)
    myhist(ax[0],dat.rhalf,bins=bins,color='k',
           label='Injected',normed=True)
    for typ,color in zip(['SIMP','PSF'],'bc'):
        keep= (isRec) & (types == typ)
        myhist(ax[1],dat.rhalf[keep],bins=bins,color=color,
               label=typ,normed=True)
    for typ,color in zip(['EXP','DEV'],'gm'):
        keep= (isRec) & (types == typ)
        myhist(ax[2],dat.rhalf[keep],bins=bins,color=color,
               label=typ,normed=True)
    
    #plots.mytext(ax,0.9,0.9,typ.upper(),fontsize=14)
    
    #isPostiveFlux= ((np.isfinite(dmag)) &
    #                (np.isfinite(true_mag)))
    #isPostiveFlux= np.ones(len(dmag),bool)
    #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])

    xlab=ax[-1].set_xlabel(r'rhalf (true)')
    #for ax,band in zip(axes,'grz'):
    #    ax.set_xlim(ylim)
    #for ax in axes:
    for i in range(3):
        ax[i].set_ylim(ylims)
        ylab=ax[i].set_ylabel('PDF')
        ax[i].legend(loc='upper right',fontsize=10)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def fraction_recovered(dat,fn='fraction_recovered.png',
                       survey_for_depth=None,
                       glim=(20,26),rlim=(20,26),zlim=(20,26)):
    assert(survey_for_depth in ['eboss_ngc','eboss_sgc','desi'])
    fig,axes=plt.subplots(3,1,figsize=(5,12))
    plt.subplots_adjust(hspace=0.1,wspace=0.2)
    xlim= dict(g=glim,
               r=rlim,
               z=zlim)

    D= getDepth()

    kw= dict(normed=False,return_vals=True)
    for ax,band in zip(axes,'grz'):
        mag= plots.flux2mag(dat.get(band+'flux'))
        mag_rec= mag[isRec]
        n,bins= np.histogram(mag,bins=30,range=xlim[band],normed=False)
        n_rec,_= np.histogram(mag[isRec],bins=bins,range=xlim[band],normed=False)
        my_step(ax,bins,n_rec.astype(float)/n)
        ax.axhline(0.5,c='k',ls='--')
        #ax.axvline(plots.getDepth().eboss_ngc(band),c='k',ls='--')
        ax.axvline(getattr(D,survey_for_depth)[band],c='g',ls='--')
    #     ax.step(bins[:-1],n_rec/n,where='mid')
        plots.mytext(ax,0.5,0.05,band,fontsize=14)
    for ax in axes:
        ylab=ax.set_ylabel('Fraction Recovered')
        ax.set_ylim(0,1)
    xlab=axes[-1].set_xlabel('True AB mag')
    axes[0].legend(loc='upper left')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def redshifts_recovered(dat,fn='redshifts_recovered.png'):
    figs,ax= plt.subplots(2,1,figsize=(4,6))
    plt.subplots_adjust(hspace=0.2)

    bins= np.linspace(0,1.5,num=30)
    # top: pdf of injected all and NGC elgs vs redshift
    myhist(ax[0],dat.psql_redshift[is_elg_input],bins=bins,color='b',
           label='NGC ELG',normed=True)
    #myhist(ax[0],dat.psql_redshift[(is_elg_input) & (isRec)],
    #       bins=bins,color='m',label='recovered',normed=True)
    myhist(ax[0],dat.psql_redshift[(is_elg_input) & (isRec) & (is_elg_trac)],
           bins=bins,color='g',label='legacypipe',normed=True)
    # bottom: fraction of recovered eboss elgs that loose to tractor measurement error
    n_elg,_= np.histogram(dat.psql_redshift[(is_elg_input)],
                                   bins=bins,normed=False)
    n_elg_legacypipe,_= np.histogram(dat.psql_redshift[(is_elg_input) & (isRec) & (is_elg_trac)],
                                   bins=bins,normed=False)
    n_notelg_legacypipe,_= np.histogram(dat.psql_redshift[(~is_elg_input) & (isRec) & (is_elg_trac)],
                                   bins=bins,normed=False)
    my_step(ax[1],bins,n_elg_legacypipe/n_elg.astype(float),
            color='g',label='legacypipe')
    my_step(ax[1],bins,n_notelg_legacypipe/n_elg.astype(float),
            color='m',label='contam by legacypipe')
    
    xlab=ax[-1].set_xlabel(r'redshift')
    ylab=ax[0].set_ylabel('PDF')
    ylab=ax[1].set_ylabel('Fraction')
    ax[1].set_ylim(0,1)
    for i in range(2):
        ax[i].set_xlim(bins[0],bins[-1])
        ax[i].legend(loc='upper left',fontsize=8)
    ax[0].set_yscale('log')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)




def e1_e2(dat,fn='e1_e2.png',nbins=(120,120),
          recovered=False):
    fig,ax=plt.subplots(1,2,figsize=(8,5))
    plt.subplots_adjust(wspace=0.35)

    keep= np.ones(len(dat),bool)
    if recovered:
        keep= isRec
    plots.myhist2D(ax[0],dat.psql_ba[keep],dat.psql_pa[keep],
                   xlim=(0.1,1.1),ylim=(-20,200),nbins=nbins)
    plots.myhist2D(ax[1],dat.e1[keep],dat.e2[keep],
                   xlim=(-1,1),ylim=(-1,1),nbins=nbins)

    ax[0].set_aspect(abs((ax[0].get_xlim()[1]-ax[0].get_xlim()[0])/\
                         (ax[0].get_ylim()[1]-ax[0].get_xlim()[0])))
    ax[1].set_aspect('equal')

    for i,xlab,ylab in [(0,'ba','pa'),(1,'e1','e2')]:
        xlab=ax[i].set_xlabel(xlab)
        ylab=ax[i].set_ylabel(ylab)
    if recovered:
        fn=fn.replace('.png','_recovered.png')
    else:
        fn=fn.replace('.png','_input.png')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def fraction_recovered_vs_rhalf(dat,fn='fraction_recovered_vs_rhalf.png'):
    fig,ax=plt.subplots()
        
    xlim=(0,2.5)
    kw=dict(normed=False,range=xlim)

    n,bins= np.histogram(dat.rhalf,bins=30,**kw)
    n_rec,_= np.histogram(dat.rhalf[isRec],bins=bins,**kw)
    my_step(ax,bins,n_rec/n)
    ax.axhline(0.5,c='k',ls='--')

    xlab=ax.set_xlabel('rhalf (arcsec)')
    ylab=ax.set_ylabel('Fraction Recovered')
    ax.set_ylim(0.0,1.)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)


def fix_for_delta_flux(dat,fn='fix_for_delta_flux.png',
                       band='z'):
    figs,ax= plt.subplots(5,1,figsize=(5,15))
    plt.subplots_adjust(hspace=0)

    dflux= dat.get('tractor_flux_'+band)[isRec] - dat.get(band+'flux')[isRec]
    rad_aper= [0.5,0.75,1.0,1.5,2.0,3.5,5.0,7.0]
    for cnt,i_aper in zip(range(5),
                          [None,5,6,7,'avg']):
        ratio_area= 1. 
        #ratio_area= (1.5*dat.rhalf[isRec] / rad_aper[i_aper])**2
        if i_aper == 'avg':
            name= 'fix: avg(-aperture_resid %.1f,%.1f)' % (rad_aper[6],rad_aper[7])
            fix= ratio_area * np.average([dat.get('tractor_apflux_resid_'+band)[isRec,6],
                                          dat.get('tractor_apflux_resid_'+band)[isRec,7]],
                                        axis=0)
            assert(len(fix)) == len(dat[isRec])
        elif i_aper is None:
            name= 'fix: None'
            fix=0
        else:
            name= 'fix: -aperture_resid %.1f' % rad_aper[i_aper]
            fix= dat.get('tractor_apflux_resid_'+band)[isRec,i_aper]* ratio_area
        y= dflux - fix
        ax[cnt].scatter(dat.get(band+'flux')[isRec],y,
                        alpha=0.2,s=5,c='b',label=name)
        ax[cnt].axhline(0,c='k',ls='-',lw=2)
        ax[cnt].axhline(np.median(y),c='y',lw=2,ls='--',
                        label='Median')

    for i in range(5):
    #     ax[i].set_yscale('log')
    #     ax[i].set_ylim(1e-2,2e1)
        ax[i].set_ylim(-5,5)
        ax[i].legend(loc='upper right',markerscale=3)
    for i in range(4):
        ax[i].set_xticklabels([])
    xlab=ax[-1].set_xlabel('%s flux (nanomaggies)' % band)
    ylab=ax[-1].set_ylabel(r'$\Delta\, Flux\,/\,\sigma$ (Tractor - Truth)')
    fn=fn.replace('.png','_%s.png' % band)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def delta_vs_grzmag(dat,fn='_vs_grzmag.png',
                    delta=None,delta_lims=(-6,6),typ='all',
                    nbins=(30,30),
                    glim=(17,26),rlim=(17,26),zlim=(17,26),
                    percentile_lines=True):
    assert(delta in ['num_std_dev','dmag'])
    assert(typ in ['all','PSF','SIMP','EXP','DEV','REX'])
    fn= delta+fn.replace('.png','_bytype_%s.png' % typ)
    
    figs,axes= plt.subplots(3,1,figsize=(6,10))
    plt.subplots_adjust(hspace=0.4)

    xlim= dict(g=glim,
               r=rlim,
               z=zlim)
    for ax,band in zip(axes,'grz'):
        if delta == 'num_std_dev':
            y= dat.get('tractor_flux_'+band) -\
                       dat.get(band+'flux')
            y *= np.sqrt(dat.get('tractor_flux_ivar_'+band))
            ylabel=r'$\Delta\, Flux\,/\,\sigma$ (Tractor - Truth)'
            keep= isRec
        elif delta == 'dmag':
            # Opposite subtraction order, so < 0 mean Truth is brighter
            # Just as for delta = num_std_dev
            y= plots.flux2mag(dat.get(band+'flux')) -\
                plots.flux2mag(dat.get('tractor_flux_'+band)) 
            ylabel=r'$\Delta\, %s$ (Truth - Tractor)' % band
            keep= (isRec) & (np.isfinite(y))

        if typ != 'all':
            types= np.char.strip(dat.get('tractor_type'))
            keep= (keep) & (types == typ)
         
        true_mag= plots.flux2mag(dat.get(band+'flux')/\
                                   dat.get('mw_transmission_'+band))
        
        bins= np.linspace(xlim[band][0],xlim[band][1],num=30)
        plots.myhist2D(ax,true_mag[keep],y[keep],
                       xlim=xlim[band],ylim=delta_lims,nbins=nbins)
        
        ax.axhline(0,c='r',ls='dotted')
        if percentile_lines:
            binned= plots.bin_up(true_mag[keep],y[keep], 
                                 bin_minmax=xlim[band],nbins=30)
            for perc in ['q25','q50','q75']:
                kw= dict(c='y',ls='-',lw=1)
                ax.plot(binned['binc'],binned[perc],**kw)
        ylab=ax.set_ylabel(ylabel)

    for ax,band in zip(axes,'grz'):
        xlab= ax.set_xlabel('true mag %s' % band)
        ax.legend(loc='upper left',fontsize=10,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def gauss_model(p,x):
    return 1/np.sqrt(2*np.pi*p[0]**2) * np.exp(-x**2/(2*p[0]**2))

def num_std_dev_gaussfit_flux(dat,fn='num_std_dev_gaussfit_flux.png',
                              delta_lims= (-6,6),typ='all',
                              keep_what_put_in='all',thresh=None,
                              sub_mean= True):
    assert(typ in ['all','PSF','SIMP','EXP','DEV','REX'])
    fn= fn.replace('.png','_bytype_%s.png' % typ)
    assert(keep_what_put_in in ['all','neq1','neq4','rhalfeqpt5',
                                'neq1_notrhalf','neq4_notrhalf',
                                'fracflux','fracflux_keep_bad',
                                'fracin','fracin_keep_bad',
                                'allmask','allmask_keep_bad',
                                'fracmask','fracmask_keep_bad'])
    if keep_what_put_in != 'all':
        fn= fn.replace('.png','_keepwhatputin_%s.png' % keep_what_put_in)
    if thresh:
        fn= fn.replace('.png','_%.2f.png' % thresh)
    
    figs,axes= plt.subplots(3,1,figsize=(6,10))
    plt.subplots_adjust(hspace=0.4)


    keep= isRec
    if typ != 'all':
        types= np.char.strip(dat.get('tractor_type'))
        keep= (keep) & (types == typ)
    if keep_what_put_in != 'all':
        pad=0.05
        is_rhalf= (dat.rhalf >= 0.5-pad) & (dat.rhalf <= 0.5+pad)
        if keep_what_put_in == 'neq1':
            keep= (keep) & (dat.n == 1)
        elif keep_what_put_in == 'neq4':
            keep= (keep) & (dat.n == 4)
        elif keep_what_put_in == 'fracflux':
            fraction= np.max(np.array([dat.tractor_fracflux_g,
                                       dat.tractor_fracflux_r,
                                       dat.tractor_fracflux_z]),axis=0)
            assert(len(fraction) == len(dat))
            keep= (keep) & (fraction < thresh)
        elif keep_what_put_in in ['fracin','fracin_keep_bad']:
            frac= np.mean(np.array([dat.tractor_fracin_g,
                                    dat.tractor_fracin_r,
                                    dat.tractor_fracin_z]),axis=0)
            assert(len(frac) == len(dat))
            if keep_what_put_in == 'fracin':
                keep= (keep) & (frac > thresh) #higher fractions are good sources
            elif keep_what_put_in == 'fracin_keep_bad':
                keep= (keep) & (frac <= thresh) 
        elif keep_what_put_in in ['fracmask','fracmask_keep_bad']:
            frac= np.mean(np.array([dat.tractor_fracmasked_g,
                                    dat.tractor_fracmasked_r,
                                    dat.tractor_fracmasked_z]),axis=0)
            assert(len(frac) == len(dat))
            if keep_what_put_in == 'fracmask':
                keep= (keep) & (frac < thresh) 
            elif keep_what_put_in == 'fracmask_keep_bad':
                keep= (keep) & (frac >= thresh) 
        elif keep_what_put_in in ['allmask','allmask_keep_bad']:
            good= ((dat.tractor_allmask_g == 0) &
                   (dat.tractor_allmask_r == 0) &
                   (dat.tractor_allmask_z == 0))
            if keep_what_put_in == 'allmask':
                keep= (keep) & (good) 
            elif keep_what_put_in == 'allmask_keep_bad':
                keep= (keep) & (~good) 
        elif keep_what_put_in == 'rhalfeqpt5':
            keep= (keep) & (is_rhalf)
        elif keep_what_put_in == 'neq1_notrhalf':
            keep= (keep) & (dat.n == 1) & (~is_rhalf)
        elif keep_what_put_in == 'neq4_notrhalf':
            keep= (keep) & (dat.n == 4) & (~is_rhalf)
 
    for ax,band in zip(axes,'grz'):
        data_lab= 'data'
        num_std_dev= dat.get('tractor_flux_'+band) -\
                        dat.get(band+'flux')
        num_std_dev *= np.sqrt(dat.get('tractor_flux_ivar_'+band))
        
        if sub_mean:
            #keep= ((num_std_dev >= num_std_lims[0]) &
            #       (num_std_dev <= num_std_lims[0]) 
            dflux_mean= np.mean(num_std_dev[((keep) &
                                             (num_std_dev > delta_lims[0]) & 
                                             (num_std_dev < delta_lims[1]))])
            #dflux_mean= np.median(num_std_dev[isRec])
            num_std_dev -= dflux_mean
            print('%s: dflux_mean=%f' % (band,dflux_mean))
            data_lab+=' minus mean (%.2f)' % dflux_mean
        
        bins= np.linspace(delta_lims[0],delta_lims[1],num=30)
        h=myhist(ax,num_std_dev[keep],bins=bins,color='b',
                 label=data_lab,normed=True,
                 return_h=True)
        
        rv = norm()
        ax.plot(bins,rv.pdf(bins),'k--',label='Standard Norm')
        
        errfunc = lambda p, x, y: gauss_model(p, x) - y
        p0 = [1.] # Initial guess
        binc= (bins[:-1]+bins[1:])/2
        p1, success = leastsq(errfunc, p0[:], args=(binc, h))
        assert(success != 0)
        norm_fit= norm(scale=p1[0])
        ax.plot(bins,norm_fit.pdf(bins),'k-',label=r'Fit $\sigma=$%.2f' % p1[0])

        ax.axvline(0,c='k',ls='dotted')
        plots.mytext(ax,0.9,0.9,band,fontsize=14)
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])

    xlab=axes[-1].set_xlabel(r'$\Delta$flux (Tractor - True) * sqrt(ivar)')
    #for ax,band in zip(axes,'grz'):
    #    ax.set_xlim(ylim)
    for ax in axes:
        ylab=ax.set_ylabel('PDF')
        ax.legend(loc='upper left',fontsize=10,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def num_std_dev_gaussfit_rhalf(dat,fn='num_std_dev_gaussfit_rhalf.png',
                               delta_lims= (-6,6),typ=None,
                               sub_mean= False,sub_bin_at_max=False):
    assert(typ != 'PSF') # psfsize_grz does not have ivar info
    assert(typ in ['SIMP','EXP','DEV','REX'])
    fn= fn.replace('.png','_bytype_%s.png' % typ)
    
    figs,ax= plt.subplots() #figsize=(6,6))
    #plt.subplots_adjust(hspace=0.4)

    #for ax,typ in zip(axes,['exp','dev']):
    data_lab= 'data'
    #isType= types == typ.upper()
    if typ == 'DEV':
        eff_typ= 'dev'
    else:
        eff_typ= 'exp'
    rhalf= dat.get('tractor_shape%s_r' % eff_typ)
    num_std_dev= rhalf - dat.rhalf
    num_std_dev *= np.sqrt(dat.get('tractor_shape%s_r_ivar' % eff_typ))
    #keep= (np.isfinite(num_std_dev)) #num_std_dev= num_std_dev[isType]
    keep= isRec
    if typ != 'all':
        types= np.char.strip(dat.get('tractor_type'))
        #types[pd.Series(types).isin(['SIMP','REX']).values]= 'EXP'
        keep= (keep) & (types == typ)
    
    if sub_mean:
        #keep= ((num_std_dev >= num_std_lims[0]) &
        #       (num_std_dev <= num_std_lims[0]) 
        dflux_mean= np.mean(num_std_dev[((keep) &
                                         (num_std_dev > delta_lims[0]) & 
                                         (num_std_dev < delta_lims[1]))])
        #dflux_mean= np.median(num_std_dev[isRec])
        num_std_dev -= dflux_mean
        print('%s: dflux_mean=%f' % (band,dflux_mean))
        data_lab+=' minus mean (%.2f)' % dflux_mean
    elif sub_bin_at_max:
        bins= np.linspace(delta_lims[0],delta_lims[1],num=30)
        h,bins=np.histogram(num_std_dev[keep],bins=bins)
        binc= (bins[:-1] + bins[1:])/2
        bin_at_max= binc[np.argmax(h)]
        num_std_dev -= bin_at_max
        data_lab+=' minus bin_at_max (%.2f)' % bin_at_max
     
    bins= np.linspace(delta_lims[0],delta_lims[1],num=30)
    h=myhist(ax,num_std_dev[keep],bins=bins,color='b',
             label=data_lab,normed=True,
             return_h=True)
    
    rv = norm()
    ax.plot(bins,rv.pdf(bins),'k--',label='Standard Norm')
    
    errfunc = lambda p, x, y: gauss_model(p, x) - y
    p0 = [1.] # Initial guess
    binc= (bins[:-1]+bins[1:])/2
    p1, success = leastsq(errfunc, p0[:], args=(binc, h))
    assert(success != 0)
    norm_fit= norm(scale=p1[0])
    ax.plot(bins,norm_fit.pdf(bins),'k-',label=r'Fit $\sigma=$%.2f' % p1[0])

    ax.axvline(0,c='k',ls='dotted')
    #plots.mytext(ax,0.9,0.9,typ.upper(),fontsize=14)
    
    #isPostiveFlux= ((np.isfinite(dmag)) &
    #                (np.isfinite(true_mag)))
    #isPostiveFlux= np.ones(len(dmag),bool)
    #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])

    xlab=ax.set_xlabel(r'$\Delta$rhalf (Tractor - True) * sqrt(ivar)')
    #for ax,band in zip(axes,'grz'):
    #    ax.set_xlim(ylim)
    #for ax in axes:
    ylab=ax.set_ylabel('PDF')
    ax.legend(loc='upper left',fontsize=10,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def residual_gaussfit_rhalf(dat,fn='residual_gaussfit_rhalf.png',
                            delta_lims= (-6,6),typ=None,
                            sub_mean= False,sub_bin_at_max=False):
    """created for typ PSF b/c there is no psfsize_grz_ivar, so cannot compute num_std_dev"""
    assert(typ in ['PSF','SIMP','EXP','DEV','REX'])
    fn= fn.replace('.png','_bytype_%s.png' % typ)
    
    figs,ax= plt.subplots() #figsize=(6,6))
    #plt.subplots_adjust(hspace=0.4)

    #for ax,typ in zip(axes,['exp','dev']):
    data_lab= 'data'
    #isType= types == typ.upper()
    if typ == 'PSF':
        rhalf= np.mean(np.array([dat.tractor_psfsize_g,
                                 dat.tractor_psfsize_r,
                                 dat.tractor_psfsize_z]),axis=0)/2
    elif typ == 'DEV':
        rhalf= dat.get('tractor_shape%s_r' % 'dev')
    else:
        rhalf= dat.get('tractor_shape%s_r' % 'exp')
    resid= rhalf - dat.rhalf
    #keep= (np.isfinite(num_std_dev)) #num_std_dev= num_std_dev[isType]
    keep= isRec
    if typ != 'all':
        types= np.char.strip(dat.get('tractor_type'))
        #types[pd.Series(types).isin(['SIMP','REX']).values]= 'EXP'
        keep= (keep) & (types == typ)
    
    if sub_mean:
        #keep= ((num_std_dev >= num_std_lims[0]) &
        #       (num_std_dev <= num_std_lims[0]) 
        dflux_mean= np.mean(resid[((keep) &
                                   (resid > delta_lims[0]) & 
                                   (resid < delta_lims[1]))])
        #dflux_mean= np.median(num_std_dev[isRec])
        resid -= dflux_mean
        print('%s: dflux_mean=%f' % (band,dflux_mean))
        data_lab+=' minus mean (%.2f)' % dflux_mean
    elif sub_bin_at_max:
        bins= np.linspace(delta_lims[0],delta_lims[1],num=30)
        h,bins=np.histogram(resid[keep],bins=bins)
        binc= (bins[:-1] + bins[1:])/2
        bin_at_max= binc[np.argmax(h)]
        resid -= bin_at_max
        data_lab+=' minus bin_at_max (%.2f)' % bin_at_max
     
    bins= np.linspace(delta_lims[0],delta_lims[1],num=30)
    h=myhist(ax,resid[keep],bins=bins,color='b',
             label=data_lab,normed=True,
             return_h=True)
    
    rv = norm()
    ax.plot(bins,rv.pdf(bins),'k--',label='Standard Norm')
    
    errfunc = lambda p, x, y: gauss_model(p, x) - y
    p0 = [1.] # Initial guess
    binc= (bins[:-1]+bins[1:])/2
    p1, success = leastsq(errfunc, p0[:], args=(binc, h))
    assert(success != 0)
    norm_fit= norm(scale=p1[0])
    ax.plot(bins,norm_fit.pdf(bins),'k-',label=r'Fit $\sigma=$%.2f' % p1[0])

    ax.axvline(0,c='k',ls='dotted')
    #plots.mytext(ax,0.9,0.9,typ.upper(),fontsize=14)
    
    #isPostiveFlux= ((np.isfinite(dmag)) &
    #                (np.isfinite(true_mag)))
    #isPostiveFlux= np.ones(len(dmag),bool)
    #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])

    xlab=ax.set_xlabel(r'$\Delta$rhalf (Tractor - True)')
    #for ax,band in zip(axes,'grz'):
    #    ax.set_xlim(ylim)
    #for ax in axes:
    ylab=ax.set_ylabel('PDF')
    ax.legend(loc='upper left',fontsize=10,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def num_std_dev_gaussfit_e1_e2(dat,fn='num_std_dev_gaussfit_e1_e2.png',
                               delta_lims= (-6,6),
                               sub_mean= True):
    types= np.char.strip(dat.get('tractor_type'))
    types[pd.Series(types).isin(['SIMP','REX']).values]= 'EXP'
    
    figs,axes= plt.subplots(2,1,figsize=(6,6))
    plt.subplots_adjust(hspace=0.4)

    typ='exp'
    for ax,delta in zip(axes,['e1','e2']):
        data_lab= 'data'
        isType= types == typ.upper()
        trac_e= dat.get('tractor_shape%s_%s' % (typ,delta))
        if delta == 'e2':
            trac_e *= -1
        num_std_dev= trac_e -\
                        dat.get(delta)
        #print('delta=',delta)
        #print('straight diff=',num_std_dev[isType])
        num_std_dev *= np.sqrt(dat.get('tractor_shape%s_%s_ivar' % (typ,delta)))
        #print('num_std_dev=',num_std_dev[isType])
        #print('length=',len(num_std_dev[isType]))
        #print('q25,med,q75 num_std_dev=',np.percentile(num_std_dev[isType],25),np.median(num_std_dev[isType]),np.percentile(num_std_dev[isType],75))
        keep= (isType) & (np.isfinite(num_std_dev)) #num_std_dev= num_std_dev[isType]
        
        if sub_mean:
            #keep= ((num_std_dev >= num_std_lims[0]) &
            #       (num_std_dev <= num_std_lims[0]) 
            dflux_mean= np.mean(num_std_dev[((keep) &
                                             (num_std_dev > delta_lims[0]) & 
                                             (num_std_dev < delta_lims[1]))])
            #dflux_mean= np.median(num_std_dev[isRec])
            num_std_dev -= dflux_mean
            print('%s: dflux_mean=%f' % (band,dflux_mean))
            data_lab+=' minus mean (%.2f)' % dflux_mean
        
        bins= np.linspace(delta_lims[0],delta_lims[1],num=30)
        h=myhist(ax,num_std_dev[keep],bins=bins,color='b',
                 label=data_lab,normed=True,
                 return_h=True)
        
        rv = norm()
        ax.plot(bins,rv.pdf(bins),'k--',label='Standard Norm')
        
        errfunc = lambda p, x, y: gauss_model(p, x) - y
        p0 = [1.] # Initial guess
        binc= (bins[:-1]+bins[1:])/2
        p1, success = leastsq(errfunc, p0[:], args=(binc, h))
        assert(success != 0)
        norm_fit= norm(scale=p1[0])
        ax.plot(bins,norm_fit.pdf(bins),'k-',label=r'Fit $\sigma=$%.2f' % p1[0])

        ax.axvline(0,c='k',ls='dotted')
        plots.mytext(ax,0.9,0.9,delta,fontsize=14)
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])

        xlab=ax.set_xlabel(r'$\Delta$%s (Tractor - True) * sqrt(ivar)' % delta)
    #for ax,band in zip(axes,'grz'):
    #    ax.set_xlim(ylim)
    for ax in axes:
        ylab=ax.set_ylabel('PDF')
        ax.legend(loc='upper left',fontsize=10,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)



def rec_lost_contam_gr_rz(dat,fn='rec_lost_contam_gr_rz.png'):
    fig,axes=plt.subplots(4,2,figsize=(10,12))
    plt.subplots_adjust(wspace=0,hspace=0)

    kw_scatter=dict(marker='.',s=20,alpha=1)
    kw_leg= dict(loc='upper left',fontsize=12,markerscale=3,frameon=False)

    for lab,color,row,keep in [('Correct (Tractor ELG)','b',0, 
                                  (isRec) & (is_elg_input) & (is_elg_trac)),
                               ('Contamination (Tractor ELG wrong)','g',1,
                                  (isRec) & (~is_elg_input) & (is_elg_trac)),
                               ('Lost (measure fails TS)','c',2,
                                  (isRec) & (is_elg_input) & (~is_elg_trac)),
                               ('Lost (not recovered)','m',3,
                                  (~isRec) & (is_elg_input))]:
        axes[row,0].scatter(dat.psql_r[keep]-dat.psql_z[keep],
                            dat.psql_g[keep]-dat.psql_r[keep],
                            c=color,label=lab,**kw_scatter)
        axes[row,1].scatter(mags['r'][keep]-mags['z'][keep],
                            mags['g'][keep]-mags['r'][keep],
                            c=color,label=lab,**kw_scatter)
        #axes[row,0].legend(**kw_leg)
        mytext(axes[row,0],0.5,0.9,lab,ha='center',fontsize=12)
    
    for row in range(4):
        for col in range(2):
            axes[row,col].set_xlim(0.5,2)
            axes[row,col].set_ylim(0.2,1.3)
            if row <= 2:
                axes[row,col].set_xticklabels([])
            if col == 1:
                axes[row,col].set_yticklabels([])
    for row in range(4):
        ylab=axes[row,0].set_ylabel('g-r') # (True)')
        #axes[row,1].set_ylabel('g-r (Tractor)')
    xlab=axes[-1,0].set_xlabel('r-z') # (True)')
    xlab=axes[-1,1].set_xlabel('r-z') # (Tractor)')
    title=axes[0,0].set_title('Truth',fontsize=14)
    title=axes[0,1].set_title('Tractor',fontsize=14)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab,title], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def rec_lost_contam_grz(dat,fn='rec_lost_contam_grz.png',
                        x_ivar=0):
    x_var= ['true_mag','galdepth','redshift'][x_ivar]
    kw_hist=dict(bins=30,normed=False)

    figs,axes= plt.subplots(3,1,figsize=(6,9))
    plt.subplots_adjust(hspace=0.3)

    ratio_area= 1. 
    for ax,band in zip(axes,'grz'):
        if x_var == 'true_mag':
            _x_var= plots.flux2mag(dat.get(band+'flux')/\
                                   dat.get('mw_transmission_'+band))
            xlab= '%s (true mag)' % band
            xlim= dict(g=(21.6,23),
                       r=(20.75,22.5),
                       z=(19.5,22))
        elif x_var == 'galdepth':
            flux_for_depth= 5 / np.sqrt(dat.get('tractor_galdepth_'+band))
            _x_var= plots.flux2mag(flux_for_depth/\
                                     dat.get('mw_transmission_'+band))
            xlab= 'galdepth %s' % band
            xlim= dict(g=(22.5,24.5),
                       r=(22.5,24.5),
                       z=(21.5,23.5))
        elif x_var == 'redshift':
            _x_var= dat.psql_redshift
            xlab= 'redshift'
            xlim= dict(g=(0,1.5),
                       r=(0,1.5),
                       z=(0,1.5))
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])
        
        # Plot
        for lab,color,keep in [('Correct (Tractor ELG)','b', 
                                  (isRec) & (is_elg_input) & (is_elg_trac)),
                               ('Contamination (Tractor ELG wrong)','g',
                                  (isRec) & (~is_elg_input) & (is_elg_trac)),
                               ('Lost (measure fails TS)','c',
                                  (isRec) & (is_elg_input) & (~is_elg_trac)),
                               ('Lost (not recovered)','m',
                                  (~isRec) & (is_elg_input))]:
            myhist(ax,_x_var[keep],color=color,label=lab,range=xlim[band],**kw_hist)
        ylab='Number'
        if kw_hist['normed']:
            ylab='PDF'
        ylabel=ax.set_ylabel(ylab)
        xlabel=ax.set_xlabel(xlab)

    leg=axes[0].legend(loc=(0,1.01),ncol=2,fontsize=10,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlabel,ylabel,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def rec_lost_contam_delta(dat,fn='rec_lost_contam_delta.png',
                          x_ivar=0,y_ivar=0,
                          percentile_lines=False):
    x_var= ['true_mag','galdepth','redshift'][x_ivar]
    y_var= ['dmag','chisq'][y_ivar]

    figs,axes= plt.subplots(3,1,figsize=(6,10))
    plt.subplots_adjust(hspace=0.4)

    ratio_area= 1. 
    for ax,band in zip(axes,'grz'):
        fix= ratio_area * np.average([dat.get('tractor_apflux_resid_'+band)[:,6],
                                      dat.get('tractor_apflux_resid_'+band)[:,7]],
                                    axis=0)
        assert(len(fix)) == len(dat)
        if y_var == 'dmag':
            _y_var= plots.flux2mag(dat.get('tractor_flux_'+band)) -\
                       plots.flux2mag(dat.get(band+'flux')+  fix)
            ylab= 'dmag (Tractor - True)'
            ylim=(-2,2)
        elif y_var == 'chisq':
            _y_var= dat.get('tractor_flux_'+band) -\
                       (dat.get(band+'flux')+  fix)
            _y_var *= np.sqrt(dat.get('tractor_flux_ivar_'+band))
            ylab= 'chiflux (Tractor - True) * sqrt(ivar)'
            ylim=(-10,10)
        
        if x_var == 'true_mag':
            _x_var= plots.flux2mag(dat.get(band+'flux')/\
                                   dat.get('mw_transmission_'+band))
            xlab= 'true mag %s' % band
            xlim= dict(g=(21.6,23),
                       r=(20.75,22.5),
                       z=(19.5,22))
        elif x_var == 'galdepth':
            flux_for_depth= 5 / np.sqrt(dat.get('tractor_galdepth_'+band))
            _x_var= plots.flux2mag(flux_for_depth/\
                                     dat.get('mw_transmission_'+band))
            xlab= 'galdepth %s' % band
            xlim= dict(g=(21,24.5),
                       r=(21,24.5),
                       z=(21,24.5))
        elif x_var == 'redshift':
            _x_var= dat.psql_redshift
            xlab= 'redshift'
            xlim= dict(g=(0,1.5),
                       r=(0,1.5),
                       z=(0,1.5))
        
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])
        
        # Plot
        xlabel=ax.set_xlabel(xlab)
        for lab,color,keep in [('lost (recovered but fail TS)','g', (isRec) & (is_elg_input) & (~is_elg_trac)),
                               ('Tractor ELG','b', (isRec) & (is_elg_input) & (is_elg_trac)),
                               ('Tractor ELG (contamiation)', 'c',(isRec) & (~is_elg_input) & (is_elg_trac))]:
            if percentile_lines:
                binned= plots.bin_up(_x_var[keep],_y_var[keep], 
                                     bin_minmax=xlim[band],nbins=30)
                for perc in ['q25','q75']:
                    kw= dict(c=color,lw=2)
                    if perc == 'q25':
                        kw.update(label=lab)
                    ax.plot(binned['binc'],binned[perc],**kw)
            else:
                ax.scatter(_x_var[keep],_y_var[keep],
                           alpha=1,s=5,c=color,label=lab)
                #ax.scatter(true_mag[(isPostiveFlux) & (keep)],dmag[(isPostiveFlux) & (keep)],
                #           alpha=1,s=5,c=color,label=lab)
        
    for ax,band in zip(axes,'grz'):
        ax.axhline(0,c='k',ls='--')
        ax.set_ylim(ylim)
    ylabel=axes[1].set_ylabel(ylab)
    leg=axes[0].legend(loc=(0,1.01),ncol=2,fontsize=12,markerscale=3)
    plt.savefig(fn,bbox_extra_artists=[xlabel,ylabel,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def rec_lost_contam_delta_by_type(dat,fn='rec_lost_contam_delta_by_type.png',
                                  band='g',
                                  x_ivar=0,y_ivar=0,percentile_lines=False):
    x_var= ['true_mag','galdepth','redshift'][x_ivar]
    y_var= ['dmag','chisq'][y_ivar]

    types= np.char.strip(dat.get('tractor_type'))
    use_types= ['PSF','SIMP','REX','EXP','DEV']
    if 'SIMP' in set(types):
        use_types.remove('REX')
    else:
        use_types.remove('SIMP')
    figs,axes= plt.subplots(4,1,figsize=(5,12))
    plt.subplots_adjust(hspace=0.2)

    ### 
    ratio_area= 1. 
    fix= ratio_area * np.average([dat.get('tractor_apflux_resid_'+band)[:,6],
                                      dat.get('tractor_apflux_resid_'+band)[:,7]],
                                    axis=0)
    assert(len(fix)) == len(dat)
    if y_var == 'dmag':
        _y_var= plots.flux2mag(dat.get('tractor_flux_'+band)) -\
                   plots.flux2mag(dat.get(band+'flux')+  fix)
        ylab= 'dmag (Tractor - True)'
        ylim=(-2,2)
    elif y_var == 'chisq':
        _y_var= dat.get('tractor_flux_'+band) -\
                   (dat.get(band+'flux')+  fix)
        _y_var *= np.sqrt(dat.get('tractor_flux_ivar_'+band))
        ylab= 'chiflux (Tractor - True) * sqrt(ivar)'
        ylim=(-10,10)

    if x_var == 'true_mag':
        _x_var= plots.flux2mag(dat.get(band+'flux')/\
                               dat.get('mw_transmission_'+band))
        xlab= 'true mag %s' % band
        xlim= dict(g=(21.6,23),
                   r=(20.75,22.5),
                   z=(19.5,22))
    elif x_var == 'galdepth':
        flux_for_depth= 5 / np.sqrt(dat.get('tractor_galdepth_'+band))
        _x_var= plots.flux2mag(flux_for_depth/\
                                 dat.get('mw_transmission_'+band))
        xlab= 'galdepth %s' % band
        xlim= dict(g=(21,24.5),
                   r=(21,24.5),
                   z=(21,24.5))
    elif x_var == 'redshift':
        _x_var= dat.psql_redshift
        xlab= 'redshift'
        xlim= dict(g=(0,1.5),
                   r=(0,1.5),
                   z=(0,1.5))
    ###   

    for ax,typ in zip(axes,use_types):
        mytext(ax,0.9,0.9,typ, fontsize=12)
        #isPostiveFlux= ((np.isfinite(dmag)) &
        #                (np.isfinite(true_mag)))
        #isPostiveFlux= np.ones(len(dmag),bool)
        #print('true_mag=',true_mag[isPostiveFlux],'trac_mag=',dmag[isPostiveFlux])
        
        # Plot
        xlabel=ax.set_xlabel(xlab)
        for lab,color,keep in [('lost (recovered but fail TS)','g', (isRec) & (is_elg_input) & (~is_elg_trac)),
                               ('Tractor ELG','b', (isRec) & (is_elg_input) & (is_elg_trac)),
                               ('Tractor ELG (contamiation)', 'c',(isRec) & (~is_elg_input) & (is_elg_trac))]:
            subset= (keep) & (types == typ)
            if percentile_lines:
                binned= plots.bin_up(_x_var[subset],_y_var[subset], 
                                     bin_minmax=xlim[band],nbins=30)
                for perc in ['q25','q75']:
                    kw= dict(c=color,lw=2)
                    if perc == 'q25':
                        kw.update(label=lab)
                    ax.plot(binned['binc'],binned[perc],**kw)
            else:
                ax.scatter(_x_var[subset],_y_var[subset],
                           alpha=1,s=5,c=color,label=lab)
                #ax.scatter(true_mag[(isPostiveFlux) & (keep)],dmag[(isPostiveFlux) & (keep)],
                #           alpha=1,s=5,c=color,label=lab)
        
    for ax in axes:
        ax.axhline(0,c='k',ls='--')
        ax.set_ylim(ylim)
    ylabel=axes[-1].set_ylabel(ylab)
    leg=axes[0].legend(loc=(0,1.05),ncol=2,fontsize=10,markerscale=3)
    fn=fn.replace('.png','_%s.png' % band)
    plt.savefig(fn,bbox_extra_artists=[xlabel,ylabel,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

def rec_lost_contam_input_elg_notelg(dat,fn='rec_lost_contam_input_elg_notelg.png'):
    fig,axes=plt.subplots(3,1,figsize=(6,12))
    plt.subplots_adjust(hspace=0.3)
    xlim= dict(g=(21.6,23),
               r=(20.75,22.5),
               z=(19.5,22))

    kw=dict(normed=True)
    for ax,band in zip(axes,'grz'):
        kw.update(bins=np.linspace(xlim[band][0],xlim[band][1],num=30),
                  range=xlim[band])
        myhist(ax,dat.get('psql_'+band)[is_elg_input],color='b',label='input, ELG',**kw)
        myhist(ax,dat.get('psql_'+band)[~is_elg_input],color='g',label='input, not ELG',**kw)

    for ax,band in zip(axes,'grz'):
        xlab=ax.set_xlabel(band)
        ylab=ax.set_ylabel('PDF')
    axes[0].legend(loc='upper left')
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)


def rec_lost_contam_fraction(dat,fn='rec_lost_contam_fraction.png'):
    fig,axes=plt.subplots(1,2,figsize=(10,5))
    plt.subplots_adjust(wspace=0.2)
    # xlim=(0,2.5)
    xlim=None
    kw=dict(range=(0,2),normed=False)

    # Left panel
    ax= axes[0]
    n_tot,bins= np.histogram(dat.psql_redshift,bins=30,**kw)

    lab,keep= 'is ELG', (is_elg_input)
    n_elg,bins= np.histogram(dat.psql_redshift[keep],bins=bins,**kw)
    my_step(ax,bins,n_elg/n_tot,color='b',label=lab)

    lab,keep= 'is ELG, recovered', (isRec) & (is_elg_input)
    n_elg_rec,_= np.histogram(dat.psql_redshift[keep],bins=bins,**kw)
    my_step(ax,bins,n_elg_rec/n_tot,color='g',label=lab)

    # Right panel
    ax= axes[1]
    lab,keep= 'is ELG, recovered ELG', (isRec) & (is_elg_input) & (is_elg_trac)
    n_corr,_= np.histogram(dat.psql_redshift[keep],bins=bins,**kw)
    my_step(ax,bins,n_corr/n_elg_rec,color='b',label=lab)
    print('n_corr=',n_corr)

    lab,keep= 'is ELG, recovered !ELG', (isRec) & (is_elg_input) & (~is_elg_trac)
    n_lost,_= np.histogram(dat.psql_redshift[keep],bins=bins,**kw)
    my_step(ax,bins,n_lost/n_elg_rec,color='g',label=lab)
    print('n_lost=',n_lost)

    lab,keep= 'not ELG, recovered ELG', (isRec) & (~is_elg_input) & (is_elg_trac)
    n_contam,_= np.histogram(dat.psql_redshift[keep],bins=bins,**kw)
    my_step(ax,bins,n_contam/n_elg_rec,color='m',label=lab)
    print('n_contam=',n_contam)

    for ax in axes:
        ax.axhline(0.5,c='k',ls='--')
        ax.set_ylim(-0.1,1.1)
        ylab=ax.set_ylabel('Fraction')
        xlab=ax.set_xlabel('redshift')
    leg=axes[0].legend(loc=(0,1.01),ncol=1)
    leg=axes[1].legend(loc=(0,1.01),ncol=1)
    plt.savefig(fn,bbox_extra_artists=[xlab,ylab,leg], bbox_inches='tight')
    plt.close()
    print('Wrote %s' % fn)

#################   
if args.which == 'cosmos':
    pad=0.2
    kw_lims= dict(glim=(22-pad,24.5+pad),
                  rlim=(21.4-pad,23.9+pad),
                  zlim=(20.5-pad,23+pad))

    delta_dec_vs_delta_ra(dat,xlim=(-1.,1.),ylim=(-1.,1.),nbins=(60,60))
    e1_e2(dat,nbins=(120,120),recovered=False)
    e1_e2(dat,nbins=(120,120),recovered=True)
    grz_hist_input_noise_ext(dat, **kw_lims)
    grz_hist_input_ext(dat,**kw_lims)
    grz_hist_input_rec(dat,**kw_lims)
    grz_hist_by_type(dat,**kw_lims)
    noise_added_1(dat)
    noise_added_2(dat)
    number_per_type_input_rec_meas(dat)
    confusion_matrix_by_type(dat)
    fraction_recovered(dat, survey_for_depth='desi',**kw_lims)
    fraction_recovered_vs_rhalf(dat)
    num_std_dev_gaussfit_flux(dat,delta_lims= (-5,5),
                              sub_mean= True)
    num_std_dev_gaussfit_rhalf(dat,delta_lims= (-7,7),
                               sub_mean= False,sub_bin_at_max=True)
    num_std_dev_gaussfit_e1_e2(dat,delta_lims= (-7,7),
                               sub_mean= False)
    delta_vs_grzmag(dat,delta='num_std_dev',delta_lims=(-10,10),
                    nbins=(60,30),**kw_lims)
    delta_vs_grzmag(dat,delta='dmag',delta_lims=(-1,1),
                    nbins=(60,30),**kw_lims)
    for band in 'grz':
        fix_for_delta_flux(dat, band=band)

elif args.which == 'eboss':
    kw_lims= dict(glim=(21.5,23.25),
                  rlim=(20.5,23.),
                  zlim=(19.5,22.5))
     
    for suffix in ['','_keep_bad']:
        # fracin IS RESPONSIBLE for peak at 1-2 sigma!!
        # num_std_dev for fracin < 0.7 sample and fracin >= 0.7 sample
        for thresh in np.linspace(0.4,1.,num=7): 
            num_std_dev_gaussfit_flux(dat,keep_what_put_in='fracin'+suffix,thresh=thresh,
                                      typ='all',delta_lims= (-7,7),
                                      sub_mean= True)
        # Allmask does not affect peak at 1-2 sigma
        num_std_dev_gaussfit_flux(dat,keep_what_put_in='allmask'+suffix,
                                  typ='all',delta_lims= (-7,7),
                                  sub_mean= True)
        # Fracmask does not affect peak at 1-2 sigma
        for thresh in np.linspace(0.1,0.5,num=5): 
            num_std_dev_gaussfit_flux(dat,keep_what_put_in='fracmask'+suffix,thresh=thresh,
                                      typ='all',delta_lims= (-7,7),
                                      sub_mean= True)
        # Fracflux does not affect peak at 1-2 sigma
        for thresh in [0.01,0.5]: 
            num_std_dev_gaussfit_flux(dat,keep_what_put_in='fracflux'+suffix,thresh=thresh,
                                      typ='all',delta_lims= (-7,7),
                                      sub_mean= True)
    # Injected 0.45 < rhalf < 0.55 does not affect peak at 1-2 sigma
    for keep_what in ['rhalfeqpt5','neq1_notrhalf','neq4_notrhalf']:
        num_std_dev_gaussfit_flux(dat,keep_what_put_in=keep_what,
                                  typ='all',delta_lims= (-7,7),
                                  sub_mean=True)
    # Tractor measures input EXP much better than in put DEV
    for keep_what in ['neq1','neq4']:
        num_std_dev_gaussfit_flux(dat,keep_what_put_in=keep_what,
                                  typ='all',delta_lims= (-7,7),
                                  sub_mean= True)
   
    delta_dec_vs_delta_ra(dat,xlim=(-1.,1.),ylim=(-1.,1.),nbins=(60,60))
    e1_e2(dat,nbins=(120,120),recovered=False)
    e1_e2(dat,nbins=(120,120),recovered=True)
    grz_hist_input_noise_ext(dat, **kw_lims)
    grz_hist_input_ext(dat,**kw_lims)
    grz_hist_input_rec(dat,**kw_lims)
    grz_hist_by_type(dat,**kw_lims)
    grz_hist_by_type2(dat,**kw_lims)
    noise_added_1(dat)
    noise_added_2(dat)
    number_per_type_input_rec_meas(dat)
    confusion_matrix_by_type(dat)
    redshifts_recovered(dat)
    fraction_recovered(dat, survey_for_depth='desi',**kw_lims)
    fraction_recovered_vs_rhalf(dat)
    num_std_dev_gaussfit_flux(dat,delta_lims= (-5,5),
                              sub_mean= True)

    hist_true_rhalf_by_type(dat)
    for typ in ['PSF']:
        residual_gaussfit_rhalf(dat,delta_lims= (-2,2),typ=typ,
                                sub_bin_at_max=True)
    for typ in ['SIMP','EXP','DEV']:
        num_std_dev_gaussfit_rhalf(dat,delta_lims= (-7,7),typ=typ,
                                   sub_bin_at_max=True)

    for typ in ['SIMP','EXP','DEV','PSF','all']:
        num_std_dev_gaussfit_flux(dat,typ=typ,delta_lims= (-7,7),
                                  sub_mean= True)
        delta_vs_grzmag(dat,delta='dmag',typ=typ,delta_lims=(-1,1),
                        nbins=(60,30),**kw_lims)
        delta_vs_grzmag(dat,delta='num_std_dev',typ=typ,delta_lims=(-10,10),
                        nbins=(60,30),**kw_lims)

    num_std_dev_gaussfit_e1_e2(dat,delta_lims= (-7,7),
                               sub_mean= False)
    for band in 'grz':
        fix_for_delta_flux(dat, band=band)
        rec_lost_contam_delta_by_type(dat,band=band,
                                      x_ivar=0,y_ivar=0,percentile_lines=False)
    rec_lost_contam_gr_rz(dat)
    rec_lost_contam_grz(dat,x_ivar=0)
    rec_lost_contam_delta(dat,x_ivar=0,y_ivar=0,percentile_lines=False)
    rec_lost_contam_input_elg_notelg(dat)
    rec_lost_contam_fraction(dat)
    
