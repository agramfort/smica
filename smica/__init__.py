"""Spectral matching ICA"""

__version__ = '0.0dev'


from .core_fitter import CovarianceFit, CovarianceFitNoise
from .core_smica import SMICA
from .core_smican import SMICAN
from .mne import ICA, transfer_to_ica, transfer_to_mne, plot_components
from .utils import fourier_sampling, loss, compute_covariances
from .sobi import sobi, SOBI, SOBI_mne
from .noiseless_jd import JDIAG, JDIAG_mne
from .dipolarity import dipolarity
from .mutual_info import mutual_information_2d, get_mir
