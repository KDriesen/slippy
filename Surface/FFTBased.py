"""
Classes for generating pseudo-random surfaces based on description of FFT:
    ===========================================================================
    ===========================================================================
    Each class inherits functionallity from the Surface but changes the 
    __init__ and descretise functions
    ===========================================================================
    ===========================================================================
    DiscFreqSurface:
        Generate a surface conating only specific frequency componenets
    ProbFreqSurface:
        Generate a surface containing normally distributed amptitudes with a
        specified function for the varience of the distribution based on the 
        frequency
    DtmnFreqSurface:
        Generate a surface containing frequency components with amptitude 
        specifed by a function of the frequency
        
    ===========================================================================
    ===========================================================================

#TODO:
        Add comment blocks to each class with examples of use
        add DtmnFreqSurface
        cheange Prob and dtm to allow for more descriptios of FFTs inc passing
        actual functions and some built in functions
        
"""

from . import Surface
import warnings
import numpy as np

__all__=["DiscFreqSurface", "ProbFreqSurface"]#, "DtmnFreqSurface"]

class DiscFreqSurface(Surface):
    is_descrete=False
    surface_type='discreteFreq'
    
    def __init__(self, frequencies, amptitudes=[1], phases_rads=[0], dimentions=2, **kwargs):
        
        self.init_checks(kwargs)
        self.dimentions=dimentions
        if type(frequencies) is list or type(frequencies) is np.ndarray:
            self.frequencies=frequencies
        else:
            raise ValueError('Frequencies, amptitudes and phases must be equal'
                             'length lists or np.arrays')
        is_complex=[type(amp) is complex for amp in amptitudes]
        if any(is_complex):
            if not len(frequencies)==len(amptitudes):
                raise ValueError('Frequencies, amptitudes and phases must be'
                                 ' equal length lists or np.arrays')
            else:
                self.amptitudes=amptitudes
        else:
            if not len(frequencies)==len(amptitudes)==len(phases_rads):
                raise ValueError('Frequencies, amptitudes and phases must be'
                                 ' equal length lists or np.arrays')
            else:
                cplx_amps=[]
                for idx in range(len(amptitudes)):
                    cplx_amps.append(amptitudes[idx]*
                                     np.exp(1j*phases_rads[idx]))
                self.amptitudes=cplx_amps
            
    def descretise(self, spacing):
        if spacing:    
            self.grid_size=spacing
        self.descretise_checks()
        #TODO write this section
        x=np.linspace(-0.5*self.global_size[0],
                    0.5*self.global_size[0],self.pts_each_direction[0])
        if self.dimentions==1:
            profile=np.zeros_like(x)
            for idx in range(len(self.frequencies)):
                profile+=np.real(self.amptitudes[idx]*
                                 np.exp(-1j*self.frequencies[idx]*x*2*np.pi))
            self.profile=profile
        elif self.dimentions==2:
            y=np.linspace(-0.5*self.global_size[1],
                        0.5*self.global_size[1],self.pts_each_direction[1])
            (X,Y)=np.meshgrid(x,y)
            profile=np.zeros_like(X)
            for idx in range(len(self.frequencies)):
                profile+=np.real(self.amptitudes[idx]*
                                 np.exp(-1j*self.frequencies[idx]*X*2*np.pi)+
                                 self.amptitudes[idx]*
                                 np.exp(-1j*self.frequencies[idx]*Y*2*np.pi))
            self.profile=profile
    
class ProbFreqSurface(Surface):
    
    is_descrete=False
    surface_type='continuousFreq'
    dimentions=2
        #TODO write this function
    def __init__(self, H, qr, qs=0):
        #q is frequency
        self.init_checks()
        self.H=H
        self.qs=qs
        self.qr=qr
        
    def descretise(self, spacing=False): 
        if spacing:
            self.grid_size=spacing
        else:
            spacing=self.grid_size
        self.descretise_checks()
        if self.global_size[0]!=self.global_size[1]:
            ValueError("This method is only defined for square domains")
        qny=np.pi/spacing
        
        u=np.linspace(0,qny,self.pts_each_direction[0])
        U,V=np.meshgrid(u,u)
        Q=np.abs(U+V)
        varience=np.zeros(Q.shape)
        varience[np.logical_and((1/Q)>(1/self.qr),
                                (2*np.pi/Q)<=(self.global_size[0]))]=1
        varience[np.logical_and((1/Q)>=(1/self.qs),
                                (1/Q)<(1/self.qr))]=(Q[np.logical_and(
                1/Q>=1/self.qs,1/Q<1/self.qr)]/self.qr
                    )**(-2*(1+self.H))
        FT=np.array([np.random.normal()*var**0.5 for var in varience.flatten()])
        FT.shape=Q.shape
        self.profile=np.real(np.fft.ifft2(FT))
        